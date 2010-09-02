#!/usr/bin/env python
import math
try:
    from PyQt4 import QtGui, QtCore
except:
    sys.stderr.write("PyQt4 must be installed!")
    raise


from tree_likelihood_viz.simple_tree import BranchEnum, TopologyEnum
from tree_likelihood_viz.utility import randomly_choose_indices, debug
from tree_likelihood_viz.graphics_util import TopologyDisplay
from tree_likelihood_viz.optimizer import TOL, TreeLikelihoodFunc, do_opt
# ratios of dimensions for 45 degree lines
HYP_OVER_HORIZ = math.sqrt(2)
HORIZ_OVER_HYP = 1/HYP_OVER_HORIZ
HYP_OVER_VERT = math.sqrt(2)
VERT_OVER_HYP = 1/HYP_OVER_VERT





class TreeWorkspace(QtGui.QDialog):
    """Internally the tree calculations are done as if we have a AB|CD tree.
    Then patterns and branch lengths are swapped into the correct order.
    """
    def __init__(self, tree, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.tree = tree
        self._lnLPanel = None
        
        self.setWindowTitle(self.tree.name)

        gridLayout = QtGui.QGridLayout()
        self.labels = []
        self.spinboxes = []
        self.free_parameters = []
        self.opt_buttons = []
        self.opt_all_callbacks = []
        self.MAX_BRANCH_LEN = 0.0
        for i, p in enumerate(self.tree.branch_length_list):
            lab = QtGui.QLabel("length of '%s'" % p.name)
            self.labels.append(lab)
            gridLayout.addWidget(lab, i, 2)

            sb = QtGui.QDoubleSpinBox()
            sb.setRange(p.min_val, p.max_val)
            self.MAX_BRANCH_LEN = max(self.MAX_BRANCH_LEN, p.max_val)
            sb.setDecimals(4)
            sb.setSingleStep(float(p.max_val - p.min_val)/100.0)
            sb.setValue(p.value)
            
            if self.tree.branch_is_free(p):
                debug("FREE param")
                sb.setEnabled(True)
                gridLayout.addWidget(sb, i, 1)
                self.spinboxes.append(sb)
                self.connect(sb,  QtCore.SIGNAL('valueChanged(double)'), self.param_changed)
                opt = QtGui.QPushButton("Optimize")
                self.opt_buttons.append(opt)
                gridLayout.addWidget(opt, i, 0)
                opt_callback = getattr(self, "opt_" + p.name)
                self.connect(opt,  QtCore.SIGNAL('clicked()'), opt_callback)
                self.opt_all_callbacks.append(opt_callback)
                self.free_parameters.append(p)
            else:
                debug("NON-FREE param")
                sb.setEnabled(False)
                self.free_parameters.append(None)
            p.setValueListeners.append(self)
            p.setValueListeners.append(sb)

        opt = QtGui.QPushButton("Optimize all")
        self.opt_buttons.append(opt)
        gridLayout.addWidget(opt, 5, 0)
        self.connect(opt, QtCore.SIGNAL('clicked()'), self.opt_all)

        pat_pr = self.tree.calc_pat_probs()
        pat_names = self.tree.get_pat_names()
        self.pr_labels = []
        self.pr_values = []
        SHOW_PAT_FREQS_ON_TREE = False
        for i, bits in enumerate(pat_names):
            lab = QtGui.QLabel("Pr(%s) =" % bits)
            vlab = QtGui.QLabel("%0.5f" % pat_pr[i])
            self.pr_labels.append(lab)
            self.pr_values.append(vlab)
            if SHOW_PAT_FREQS_ON_TREE:
                gridLayout.addWidget(lab, i, 3)
                gridLayout.addWidget(vlab, i, 4)
                gridLayout.setRowStretch(i, 1)
        if SHOW_PAT_FREQS_ON_TREE:
            gridLayout.setColumnStretch(0, .5)
            gridLayout.setColumnStretch(1, .5)

        self.treeCanvas = QtGui.QFrame()
        gridLayout.setRowMinimumHeight(6, 250)
        gridLayout.addWidget(self.treeCanvas, 6, 0, 1, 5)
        self.treePaintX, self.treePaintY = (50, 300)
        self.treePaintScaler = 290
        self.treePen = QtGui.QPen(TopologyDisplay.colors[self.tree.topology], 2, QtCore.Qt.SolidLine)
        sim = QtGui.QPushButton("Simulate...")
        self.load_data_button = QtGui.QPushButton("Load Data")
        gridLayout.addWidget(sim, 9, 0)
        gridLayout.addWidget(self.load_data_button, 10, 0)
        self.num_chars_edit = QtGui.QLineEdit()
        num_char_validator = QtGui.QIntValidator(self)
        num_char_validator.setBottom(0)
        self.num_chars_edit.setText("500")
        self.num_chars_edit.setValidator(num_char_validator)
        gridLayout.addWidget(self.num_chars_edit, 9, 1)
        lab = QtGui.QLabel("... characters")
        gridLayout.addWidget(lab, 9, 2)
        self.connect(sim,  QtCore.SIGNAL('clicked()'), self.simulate)
        self.connect(self.load_data_button,  QtCore.SIGNAL('clicked()'), self.load_data)
        self.setLayout(gridLayout)
        self.resize(570, 400)

    def get_lnL_panel(self):
        return self._lnLPanel
    def set_lnL_panel(self, p):
        self._lnLPanel = p
    lnLPanel = property(get_lnL_panel, set_lnL_panel)


    def setValue(self, ignored_val):
        self.repaint()
    def simulate(self):
        if not self.lnLPanel:
            return
        try:
            t = self.num_chars_edit.text()
            n = int(t)
        except:
            raise

        p = self.tree.calc_pat_probs()
        c = randomly_choose_indices(p, n)
        print "simulated counts = ", c
        self.lnLPanel.set_counts(c)

    def load_data(self):
        if not self.lnLPanel:
            return
        load_data_filedialog = QtGui.QFileDialog(self)
        #sys.stderr.write("\n".join(dir(load_data_filedialog)))
        if load_data_filedialog.exec_():
            f = load_data_filedialog.selectedFiles()
            if f:
                pattern_count_filename= f[0]
                try:
                    c = parse_counts_from_fn(pattern_count_filename, num_patterns=len(self.tree.get_pat_names()))
                    self.lnLPanel.set_counts(c)
                except:
                    sys.stderr.write("Error reading data from %s" % pattern_count_filename)


    def call_opt(self, parameter, curr_step=0.04):
        calc = self.lnLPanel
        if not calc:
            return
        data = calc.get_counts()
        if sum(data) == 0.0:
            return
        to_optimize = TreeLikelihoodFunc(self.tree, data, parameter)
        return do_opt(to_optimize, parameter, curr_step=curr_step)
    
    def opt_all(self):
        if not self.opt_all_callbacks:
            return
        curr_step = 0.04
        first_callback = self.opt_all_callbacks[0]
        v, prev_lnl = first_callback(curr_step=curr_step)
        same_score_count = 0
        while True:
            for curr_callback in self.opt_all_callbacks:
                v, curr_lnl = curr_callback(curr_step=curr_step)
            if abs(prev_lnl - curr_lnl) < TOL:
                same_score_count += 1
            else:
                same_score_count = 0
            if same_score_count > 1:
                return
            prev_lnl = curr_lnl
            curr_step /= 10
    def opt_A(self,curr_step=0.04):
        debug('opt_A')
        return self.call_opt(self.free_parameters[BranchEnum.A], curr_step=curr_step)
    def opt_B(self,curr_step=0.04):
        debug('opt_B')
        return self.call_opt(self.free_parameters[BranchEnum.B], curr_step=curr_step)
    def opt_Internal(self,curr_step=0.04):
        debug('opt_Internal')
        return self.call_opt(self.free_parameters[BranchEnum.INTERNAL], curr_step=curr_step)
    def opt_C(self,curr_step=0.04):
        debug('opt_C')
        return self.call_opt(self.free_parameters[BranchEnum.C], curr_step=curr_step)
    def opt_D(self,curr_step=0.04):
        debug('opt_D')
        return self.call_opt(self.free_parameters[BranchEnum.D], curr_step=curr_step)
    def param_changed(self):
        for i, p in enumerate(self.free_parameters):
            if p is not None:
                sb = self.spinboxes[i]
                v = sb.value()
                p.value = v
        self.repaint()
        if self.lnLPanel:
            self.lnLPanel.probs_changed()

    def refresh_pat_prob_GUI(self):
        pat_pr = self.tree.calc_pat_probs()
        for i, item in enumerate(self.pr_values):
            t = "%0.5f" % pat_pr[i]
            item.setText(t)
            # print i, t

    def paintEvent(self, event):
        self.refresh_pat_prob_GUI()
        paint = QtGui.QPainter()
        paint.begin(self)
        scaler = self.treePaintScaler
        abAncX = (self.treePaintX + self.MAX_BRANCH_LEN*scaler*HORIZ_OVER_HYP)
        abAncY = (self.treePaintY+ self.MAX_BRANCH_LEN*scaler*VERT_OVER_HYP)
        a_len, b_len, int_len, c_len, d_len = self.tree.get_funky_ordered_br_lens()
        cdAncX = abAncX + scaler*int_len
        cdAncY = abAncY
        aX = abAncX - scaler*HORIZ_OVER_HYP*a_len
        aY = abAncY - scaler*VERT_OVER_HYP*a_len
        bX = abAncX - scaler*HORIZ_OVER_HYP*b_len
        bY = abAncY + scaler*VERT_OVER_HYP*b_len
        cX = cdAncX + scaler*HORIZ_OVER_HYP*c_len
        cY = cdAncY - scaler*VERT_OVER_HYP*c_len
        dX = cdAncX + scaler*HORIZ_OVER_HYP*d_len
        dY = cdAncY + scaler*VERT_OVER_HYP*d_len
        font_x_offset = 10
        font_y_offset = 5
        if self.tree.topology == TopologyEnum.AB:
            b_text, c_text, d_text = "B", "C", "D"
        elif self.tree.topology == TopologyEnum.AC:
            b_text, c_text, d_text = "C", "B", "D"
        else:
            b_text, c_text, d_text = "D", "B", "C"
        paint.setPen(self.treePen)
        paint.drawLine(abAncX, abAncY, cdAncX, cdAncY)
        paint.drawLine(abAncX, abAncY, aX, aY)
        paint.drawText(aX - font_x_offset, aY + font_y_offset, "A")
        paint.drawLine(abAncX, abAncY, bX, bY)
        paint.drawText(bX - font_x_offset, bY+ font_y_offset, b_text)
        paint.drawLine(cdAncX, cdAncY, cX, cY)
        paint.drawText(cX+4, cY + font_y_offset, c_text)
        paint.drawLine(cdAncX, cdAncY, dX, dY)
        paint.drawText(dX+4, dY+ font_y_offset, d_text)
        paint.end()
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
