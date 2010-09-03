import sys
try:
    from PyQt4 import QtGui
except:
    sys.stderr.write("PyQt4 must be installed!")
    raise

#!/usr/bin/env python
from tree_likelihood_viz.utility import obtain_initial_pattern_counts
from tree_likelihood_viz.simple_tree_drawing import TreeWorkspace
from tree_likelihood_viz.simple_tree import TopologyEnum, generate_branch_length_model, Tree
from tree_likelihood_viz.histo_window import LnLWorkspace

class GenericLikelihoodApp(QtGui.QMainWindow):
    def __init__(self, 
                 title,
                 char_model_source,
                 branch_length_source=generate_branch_length_model,
                 fixed_params=None):
        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle(title)
        sb = self.statusBar()
        self.trees = []
        self.treeWindows = []
        for i, topo in enumerate([TopologyEnum.AB, TopologyEnum.AC, TopologyEnum.AD]):
            if callable(branch_length_source):
                branches = branch_length_source(topo, char_model=char_model)
            else:
                branches = branch_length_source[i]

            if callable(fixed_params):
                fixed = fixed_params(topo, char_model=char_model)
            elif fixed_params is None:
                fixed = []
            else: 
                fixed = fixed_params[i]

            t = Tree(topology=topo,
                     char_model=char_model_source[i],
                     branch_length_model=branches, 
                     fixed_params=fixed)
            w = TreeWorkspace(t)
            self.trees.append(t)
            self.treeWindows.append(w)

        self.lnL = LnLWorkspace(prob_sources=self.trees)
        for w in self.treeWindows:
            w.lnLPanel = self.lnL
        self.lnL.move(0,0)
        for i, w in enumerate(self.treeWindows):
            w.move(500 + 15*i,20 + 15*i)

    def show(self):
        for w in self.treeWindows:
            w.show()
        self.lnL.show()
        QtGui.QMainWindow.show(self)

def runApp(title, char_models, branches=None, fixed_params=None, num_possible_patterns=8):
    if branches is None:
        branches = generate_branch_length_model
    app = QtGui.QApplication(sys.argv)
    qb = GenericLikelihoodApp(title=title, 
                              char_model_source=char_models,
                              branch_length_source=branches,
                              fixed_params=fixed_params)
    qb.show()
    pattern_count_data = obtain_initial_pattern_counts(num_patterns=num_possible_patterns)
    qb.lnL.set_counts(pattern_count_data)
    sys.exit(app.exec_())

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
