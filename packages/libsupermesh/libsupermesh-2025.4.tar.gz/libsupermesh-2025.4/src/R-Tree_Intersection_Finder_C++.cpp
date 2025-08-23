/*
  For copyright information see COPYING in the libsupermesh root directory. For
  authors see AUTHORS in the libsupermesh root directory.

  The file is part of libsupermesh
    
  This library is free software; you can redistribute it and/or
  modify it under the terms of the GNU Lesser General Public
  License as published by the Free Software Foundation;
  version 2.1 of the License.

  This library is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
  Lesser General Public License for more details.

  You should have received a copy of the GNU Lesser General Public
  License along with this library; if not, write to the Free Software
  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
*/

/*
 * The following code is derived from include/Element_Intersection.h, 
 * include/MeshDataStream.h, and femtools/Element_Intersection.cpp in
 * Fluidity git revision 4e6c1d2b022df3a519cdec120fad28e60d1b08d9 (dated
 * 2015-02-25). This uses modified versions of code from Rtree 0.4.3, added
 * 2016-02-24. This uses modified code from libspatialindex 1.8.5, added
 * 2016-02-24.
 */
 
// Fluidity copyright information (note that AUTHORS mentioned in the following
// has been renamed to Fluidity_AUTHORS):

/*
  Copyright (C) 2006 Imperial College London and others.
  
  Please see the AUTHORS file in the main source directory for a full list
  of copyright holders.

  Prof. C Pain
  Applied Modelling and Computation Group
  Department of Earth Science and Engineering
  Imperial College London

  amcgsoftware@imperial.ac.uk
  
  This library is free software; you can redistribute it and/or
  modify it under the terms of the GNU Lesser General Public
  License as published by the Free Software Foundation,
  version 2.1 of the License.

  This library is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
  Lesser General Public License for more details.

  You should have received a copy of the GNU Lesser General Public
  License along with this library; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307
  USA
*/

// Rtree 0.4.3 copyright information:

/*
# =============================================================================
# Rtree spatial index. Copyright (C) 2007 Sean C. Gillies
#
# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License 
# along with this library; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
# Contact email: sgillies@frii.com
# =============================================================================
*/

// libspatialindex 1.8.5 copyright information:

/******************************************************************************
 * Project:  libspatialindex - A C++ library for spatial indexing
 * Author:   Marios Hadjieleftheriou, mhadji@gmail.com
 ******************************************************************************
 * Copyright (c) 2002, Marios Hadjieleftheriou
 *
 * All rights reserved.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a
 * copy of this software and associated documentation files (the "Software"),
 * to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included
 * in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
 * OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 * THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 * DEALINGS IN THE SOFTWARE.
******************************************************************************/

#include "libsupermesh_configuration.h"
#include "spatialindex/SpatialIndex.h"

#include <cmath>

#include "R-Tree_Intersection_Finder_C++.h"

using namespace libsupermesh;

// Modified version of code from rtree/gispyspatialindex.h
// (GISPySpatialIndex), rtree/gispyspatialindex.cc (GISPySpatialIndex), and
// rtree/wrapper.cc (RtreeIndex_intersects) in Rtree 0.4.3. Added 2016-02-24.
// Original Fluidity ElementIntersectionFinder had comment:
  // Interface to spatialindex to calculate element intersection lists between
  // meshes using bulk storage
  // Uses code from gispatialindex.{cc,h} in Rtree 0.4.1
libsupermesh::RTree::RTree(const int &dim, const double *positions,
  const int &loc, const int &nelements, const int *enlist)
  : dim(dim), visitor(nelements) {
  this->memory = SpatialIndex::StorageManager::createNewMemoryStorageManager();
  this->buffer = SpatialIndex::StorageManager::createNewRandomEvictionsBuffer(*this->memory, capacity, bWriteThrough);
  
  // Properties as used in PropertySet version of createAndBulkLoadNewRTree in
  // src/rtree/RTree.cc, libspatialindex 1.8.5
  Tools::PropertySet properties;
    
  Tools::Variant treeVariant;
  treeVariant.m_varType = Tools::VT_LONG;
  treeVariant.m_val.lVal = SpatialIndex::RTree::RV_RSTAR; 
  properties.setProperty("TreeVariant", treeVariant);
  
  Tools::Variant v_fillFactor;
  v_fillFactor.m_varType = Tools::VT_DOUBLE;
  v_fillFactor.m_val.dblVal = fillFactor;
  properties.setProperty("FillFactor", v_fillFactor);
  
  Tools::Variant v_indexCapacity;
  v_indexCapacity.m_varType = Tools::VT_ULONG;
  v_indexCapacity.m_val.ulVal = indexCapacity;
  properties.setProperty("IndexCapacity", v_indexCapacity);
  
  Tools::Variant v_leafCapacity;
  v_leafCapacity.m_varType = Tools::VT_ULONG;
  v_leafCapacity.m_val.ulVal = leafCapacity;
  properties.setProperty("LeafCapacity", v_leafCapacity);
  
  Tools::Variant dimension;
  dimension.m_varType = Tools::VT_ULONG;
  dimension.m_val.ulVal = dim;
  properties.setProperty("Dimension", dimension);
  
  Tools::Variant pageSize;
  pageSize.m_varType = Tools::VT_ULONG;
  // James R. Maddison note: this is as large as possible to attempt to avoid disk swapping.
  // This value is later multiplied by the ExternalSortBufferTotalPages property, which must be at least 2, hence the divide.
  pageSize.m_val.ulVal = std::numeric_limits<uint32_t>::max() / 2;
  properties.setProperty("ExternalSortBufferPageSize", pageSize);
  
  Tools::Variant numberOfPages;
  numberOfPages.m_varType = Tools::VT_ULONG;
  numberOfPages.m_val.ulVal = 2;
  properties.setProperty("ExternalSortBufferTotalPages", numberOfPages);
      
  MeshDataStream stream(dim, positions, loc, nelements, enlist);
  SpatialIndex::id_type indexIdentifier = 0;
  this->tree = SpatialIndex::RTree::createAndBulkLoadNewRTree(
    SpatialIndex::RTree::BLM_STR, stream, *this->buffer, properties, indexIdentifier);
}
// End of modified code from rtree/gispyspatialindex.h,
// rtree/gispyspatialindex.cc, and rtree/wrapper.cc

extern "C" {  
  void libsupermesh_build_rtree(void **rtree, int dim, int nnodes,
    const double *positions, int loc, int nelements, const int *enlist) {
    *rtree = static_cast<void*>(new libsupermesh::RTree(dim, positions, loc, nelements, enlist));
  }
  
  void libsupermesh_query_rtree(void **rtree, int dim, int loc_a,
    const double *element_a, int *neles_b) {
    assert(dim == (static_cast<libsupermesh::RTree*>(*rtree))->dim);
    *neles_b = (static_cast<libsupermesh::RTree*>(*rtree))->query(loc_a, element_a);
  }
  
  void libsupermesh_query_rtree_intersections(void **rtree, int *eles_b) {
    (static_cast<libsupermesh::RTree*>(*rtree))->query_intersections(eles_b);
  }
  
  void libsupermesh_deallocate_rtree(void **rtree) {
    delete (static_cast<libsupermesh::RTree*>(*rtree));
  }
}
