#!/usr/bin/env python
import math, sys

SHOW_DATA_BARS = [True, True, True, True]
try:
    from PyQt4 import QtGui, QtCore
except:
    sys.stderr.write("PyQt4 must be installed!")
    raise

from tree_likelihood_viz.graphics_util import TopologyDisplay
from tree_likelihood_viz.utility import debug
from tree_likelihood_viz.optimizer import calc_ln_L_from_counts, TreeLikelihoodFunc

class MultiBarWidget(QtGui.QWidget):
    def __init__(self, parent):
        self.h = []
        QtGui.QWidget.__init__(self, parent)
        self.max_dim = 300
        self.max_prob = 1.0
        self.px_per_unit_prob = self.max_dim/self.max_prob
        self.bar_dim = 10
        self.bar_skip = 0
        self.setMinimumHeight(4.5*(self.bar_dim+ self.bar_skip))
        self.setMinimumWidth(self.max_dim)
    def paintEvent(self, event):
        paint = QtGui.QPainter()
        paint.begin(self)
        colors = [QtCore.Qt.black, QtCore.Qt.red, QtCore.Qt.blue, QtCore.Qt.green, ]
        y = 0
        for n, b in enumerate(self.h):
            if SHOW_DATA_BARS[n]:
                w = b*self.px_per_unit_prob
                r = QtCore.QRect(0, y, w, self.bar_dim)
                curr_color = colors[n]
                paint.fillRect(r, curr_color)
            #print 0, y, w, self.bar_dim
            y += self.bar_dim + self.bar_skip
        paint.end()

class LnLTrace(QtGui.QDialog):
    def __init__(self, data_source, parameters, trees, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.data_source = data_source
        self.param_list = parameters
        self.trees = trees
        self.rescaled = []
        self.setWindowTitle("Trace of lnL of %s" % parameters[0].name)
        gridLayout = QtGui.QGridLayout()
        self.trace_button = QtGui.QPushButton("Trace")
        gridLayout.addWidget(self.trace_button, 0, 0)

        self.traceCanvas = QtGui.QFrame()
        self.height_pix = 300
        self.drawable_height = 250
        gridLayout.setRowMinimumHeight(1, self.height_pix)
        gridLayout.addWidget(self.traceCanvas, 1, 0, 1, 5)
        self.tracePaintX, self.tracePaintY = (50, self.height_pix)
        self.pen_list = [QtGui.QPen(TopologyDisplay.colors[i], 2, QtCore.Qt.SolidLine) for i in range(len(parameters))]
        self.connect(self.trace_button,  QtCore.SIGNAL('clicked()'), self.trace)
        self.setLayout(gridLayout)
        self.resize(570, 400)
        
    def trace(self):
        debug("Trace called")
        data = self.data_source.get_counts()
        if sum(data) == 0.0:
            return
        mn = self.param_list[0].min_val
        mx = self.param_list[0].max_val
        stride = (mx - mn)/250
        score_lists = []
        maxima = []
        for i, parameter in enumerate(self.param_list):
            tree = self.trees[i]
            to_optimize = TreeLikelihoodFunc(tree, data, parameter)
            prev = parameter.value
            curr = mn
            sc = []
            while curr < mx:
                sc.append(to_optimize(curr))
                curr += stride
            to_optimize(prev)
            m = max(sc)
            maxima.append(m)
            score_lists.append(sc)
        max_lnL = max(maxima)
        worst_best = min(maxima)
        diff = max_lnL - worst_best
        height_in_lnL = 2*diff
        offset = worst_best - diff
        scale = -self.drawable_height/(height_in_lnL)
        self.rescaled = []
        for sc in score_lists:
            rsc = [self.height_pix + scale*(i - offset) for i in sc]
            self.rescaled.append(rsc)
        print score_lists
        print self.rescaled
        self.repaint()

    def paintEvent(self, event):
        if not self.rescaled:
            return

        paint = QtGui.QPainter()
        paint.begin(self)
        for i, rsc in enumerate(self.rescaled):
            pen = self.pen_list[i]
            paint.setPen(pen)
            fy = rsc[0]
            fx = 0
            for x, sy in enumerate(rsc[1:]):
                sx = 1 + 2*x
                try:
                    paint.drawLine(30 + int(fx), int(fy), 30 + int(sx), int(sy))
                except:
                    pass
                fx = sx
                fy = sy
        paint.end()

class LnLWorkspace(QtGui.QDialog):
    """Internally the tree calculations are done as if we have a AB|CD tree.
    Then patterns and branch lengths are swapped into the correct order.
    """
    def __init__(self, prob_sources, parent=None):
        QtGui.QWidget.__init__(self, parent)
        assert(len(prob_sources) == 3)
        self.prob_sources = prob_sources
        abp, acp, adp = [i.calc_pat_probs(False) for i in self.prob_sources]
        for i, p in enumerate(self.prob_sources):
            f = lambda : self.prob_vec_updated(i)

        self.setWindowTitle("Data and Likelihoods")
        gridLayout = QtGui.QGridLayout()
        dheader = QtGui.QLabel("Data (counts)")
        gridLayout.addWidget(dheader, 0, 0)
        tax_labels = QtGui.QLabel("A B C D")
        gridLayout.addWidget(tax_labels, 0, 1)
        self.showDataChkBox = QtGui.QCheckBox("Data")
        self.showAB = QtGui.QCheckBox("AB")
        self.showAC = QtGui.QCheckBox("AC")
        self.showAD = QtGui.QCheckBox("AD")
        self.showBarsBoxes = [self.showDataChkBox, self.showAB, self.showAC, self.showAD]
        for el in self.showBarsBoxes:
            el.setChecked(True)
            self.connect(el,  QtCore.SIGNAL('stateChanged(int)'), self.show_bars_changed)
        gridLayout.addWidget(self.showDataChkBox, 0, 2)
        gridLayout.addWidget(self.showAB, 0, 3)
        gridLayout.addWidget(self.showAC, 0, 4)
        gridLayout.addWidget(self.showAD, 0, 5)
        patternCountValidator = QtGui.QDoubleValidator(self)
        patternCountValidator.setBottom(0.0)
        self.data_labels = []
        self.data_counts = []
        self.plot_widget_list = []
        pattern_names = prob_sources[0].get_pat_names()
        for i, pat_name in enumerate(pattern_names):
            spaced_pat_name = " ".join(list(pat_name))
            lab = QtGui.QLabel(spaced_pat_name)
            vlab = QtGui.QLineEdit()
            vlab.setMaximumWidth(100)
            vlab.setText("0")
            vlab.setValidator(patternCountValidator)
            self.data_labels.append(lab)
            self.data_counts.append(vlab)
            plot_widget = MultiBarWidget(self)
            plot_widget.h = [0.0, abp[i], acp[i], adp[i]]
            self.plot_widget_list.append(plot_widget)
            gridLayout.addWidget(vlab, 1 + i, 0)
            gridLayout.addWidget(lab, 1 + i, 1)
            gridLayout.addWidget(plot_widget, 1 + i, 2, 1, 3)
        for el in self.data_counts:
            self.connect(el,  QtCore.SIGNAL('textChanged(QString)'), self.counts_changed)
        w = QtGui.QLabel('ln(Likelihood)')
        gridLayout.addWidget(w, 9, 0, 1, 2)
        w = QtGui.QLabel('Parsimony score')
        gridLayout.addWidget(w, 10, 0, 1, 2)
        # font for the text boxes for the lnL
        self.notBestFont = QtGui.QFont()
        self.bestFont = QtGui.QFont()
        self.bestFont.setUnderline(True)
        self.lnL_labels = [QtGui.QLabel(''), QtGui.QLabel(''), QtGui.QLabel('')]
        for n, el in enumerate(self.lnL_labels):
            gridLayout.addWidget(el, 9, 2 + n)
        self.pars_labels = [QtGui.QLabel(''), QtGui.QLabel(''), QtGui.QLabel('')]
        for n, el in enumerate(self.pars_labels):
            gridLayout.addWidget(el, 10, 2 + n)
        self.setLayout(gridLayout)
        self.resize(570, 500)
    def show_bars_changed(self):
        for n, el in enumerate(self.showBarsBoxes):
            if el.isChecked():
                SHOW_DATA_BARS[n] = True
            else:
                SHOW_DATA_BARS[n] = False
        self.repaint()
    def prob_vec_updated(self, prob_vec_index):
        debug("prob_vec_updated(%d)" % prob_vec_index)
        self.repaint()

    def counts_changed(self):
        abp, acp, adp = [i.calc_pat_probs(False) for i in self.prob_sources]
        c = [float(i.text() or 0) for i in self.data_counts]
        #print c
        t = sum(c)
        have_data = True
        if t == 0.0:
            t = 1.0
            have_data = False
        for n, el in enumerate(c):
            self.plot_widget_list[n].h = [el/t, abp[n], acp[n], adp[n]]
            self.plot_widget_list[n].repaint()
        if have_data:
            lnL_values = self.calc_ln_L()
            pars_scores = self.calc_pars_scores()
            #print pars_scores
            highest_index = lnL_values.index(max(lnL_values))
            most_pars_index = pars_scores.index(min(pars_scores))
            as_str = ["%6.2f" % i for i in lnL_values]
            for n, el in enumerate(self.lnL_labels):
                if n == highest_index:
                    el.setFont(self.bestFont)
                else:
                    el.setFont(self.notBestFont)
                fmt_str = TopologyDisplay.txt_fmt[n]
                txt = TopologyDisplay.txt_fmt[n] % as_str[n]
                el.setText(txt)
                el.show()
            as_str = ["%6.2f" % i for i in pars_scores]
            for n, el in enumerate(self.pars_labels):
                if n == most_pars_index:
                    el.setFont(self.bestFont)
                else:
                    el.setFont(self.notBestFont)
                fmt_str = TopologyDisplay.txt_fmt[n]
                txt = TopologyDisplay.txt_fmt[n] % as_str[n]
                el.setText(txt)
                el.show()
        self.repaint()
    def probs_changed(self):
        self.counts_changed()
        self.repaint()
    def get_counts(self):
        c = []
        for i in self.data_counts:
            try:
                x = float(i.text())
            except:
                x = 0.0
            c.append(x)
        return c
    def calc_pars_scores(self):
        c = self.get_counts()
        non_const = sum(c[1:])
        homoplasy_ab = c[5] + c[6]
        homoplasy_ac = c[3] + c[6]
        homoplasy_ad = c[3] + c[5]
        return [non_const + homoplasy_ab, non_const + homoplasy_ac, non_const + homoplasy_ad]
    def calc_ln_L(self):
        c = self.get_counts()
        freqs = [i.calc_pat_probs() for i in self.prob_sources]
        return [calc_ln_L_from_counts(c, f) for f in freqs]
    def set_counts(self, pattern_count_data):
        for n, x in enumerate(pattern_count_data):
            try:
                self.data_counts[n].setText(str(int(x)))
            except:
                self.data_counts[n].setText(str(x))
            if n == 7:
                break
        self.repaint()
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
