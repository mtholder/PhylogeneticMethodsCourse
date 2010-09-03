#!/usr/bin/env python
from tree_likelihood_viz.model import CFN
from tree_likelihood_viz.app_for_model import runApp

runApp(title='CFN Tree likelihood visualizer', char_model=CFN())

################################################################################
# tree_likelihood_viz is a small package for creating interactive graphical
#   depictions of quantities related to the calculation of likelihood on
#   phylogenetic trees using a few simple models of character evolution. The 
#   primary purpose of the package is to assist in teaching.
# 
# Copyright (C) 2010  Mark T. Holder mtholder@gmail.com
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
################################################################################
