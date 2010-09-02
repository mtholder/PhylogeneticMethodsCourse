#!/usr/bin/env python
import sys
try:
    from PyQt4 import QtGui
except:
    sys.stderr.write("PyQt4 must be installed!")
    raise

from tree_likelihood_viz.utility import obtain_initial_pattern_counts
from tree_likelihood_viz.cfn import CFN
from tree_likelihood_viz.simple_tree_drawing import TreeWorkspace
from tree_likelihood_viz.simple_tree import TopologyEnum, generate_branch_length_model, Tree
from tree_likelihood_viz.histo_window import LnLWorkspace


char_model = CFN()

class CFNLikelihoodApp(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle('tree likelihood visualizer')
        sb = self.statusBar()
        blm = generate_branch_length_model(topology=TopologyEnum.AB, char_model)
        self.abTree = Tree(topology=TopologyEnum.AB, char_model, blm)
        self.abTreeW = TreeWorkspace(self.abTree)

        blm = generate_branch_length_model(topology=TopologyEnum.AC, char_model)
        self.acTree = Tree(topology=TopologyEnum.AC, char_model, blm)
        self.acTreeW = TreeWorkspace(self.acTree)

        blm = generate_branch_length_model(topology=TopologyEnum.AD, char_model)
        self.adTree = Tree(topology=TopologyEnum.AD, char_model, blm)
        self.adTreeW = TreeWorkspace(self.acTree)

        self.lnL = LnLWorkspace(prob_sources=[self.abTree, self.acTree, self.adTree])
        self.abTreeW.lnLPanel = self.lnL
        self.acTreeW.lnLPanel = self.lnL
        self.adTreeW.lnLPanel = self.lnL
        self.lnL.move(0,0)
        self.abTreeW.move(500,20)
        self.acTreeW.move(520,40)
        self.adTreeW.move(530,50)
    def show(self):
        self.acTreeW.show()
        self.abTreeW.show()
        self.adTreeW.show()
        self.lnL.show()
        QtGui.QMainWindow.show(self)
app = QtGui.QApplication(sys.argv)
qb = CFNLikelihoodApp()
qb.show()
pattern_count_data = obtain_initial_pattern_counts(num_patterns=8)
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
