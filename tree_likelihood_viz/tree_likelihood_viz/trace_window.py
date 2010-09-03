#!/usr/bin/env python
import math, sys

SHOW_DATA_BARS = [True, True, True, True]
try:
    from PyQt4 import QtGui, QtCore
except:
    sys.stderr.write("PyQt4 must be installed!")
    raise

from tree_likelihood_viz.graphics_util import TopologyDisplay, font_x_offset, font_y_offset
from tree_likelihood_viz.utility import debug
from tree_likelihood_viz.optimizer import TreeLikelihoodFunc

class LnLTrace(QtGui.QDialog):
    def __init__(self, data_source, parameters, trees, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.data_source = data_source
        self.param_list = parameters
        self.trees = trees
        self.rescaled = []
        self.axes_lines = []
        self.axes_text = []
        self.setWindowTitle("Trace of lnL of %s" % parameters[0].name)
        gridLayout = QtGui.QGridLayout()
        self.trace_button = QtGui.QPushButton("Trace")
        gridLayout.addWidget(self.trace_button, 0, 0)

        self.plot_y_range_mult = 2.0 # 
        self.traceCanvas = QtGui.QFrame()
        self.height_pix = 300
        self.width_pix = 500
        self.width_offset = 50
        self.drawable_height = 200
        self.num_points_to_plot = 200
        gridLayout.setRowMinimumHeight(1, self.height_pix)
        gridLayout.addWidget(self.traceCanvas, 1, 0, 1, 5)
        self.tracePaintX, self.tracePaintY = (self.width_pix, self.height_pix)
        self.pen_list = [QtGui.QPen(TopologyDisplay.colors[i], 2, QtCore.Qt.SolidLine) for i in range(len(parameters))]
        self.axis_pen = QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.DashLine)
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
        stride = (mx - mn)/self.num_points_to_plot
        score_lists = []
        inverted_maxima = []
        overall_max = []
        for i, parameter in enumerate(self.param_list):
            tree = self.trees[i]
            to_optimize = TreeLikelihoodFunc(tree, data, parameter)
            prev = parameter.value
            curr = mn
            sc = []
            max_pt = (mn, float('-inf'))
            while curr < mx:
                val = to_optimize(curr)
                pt = (curr, val)
                if val > max_pt[1]:
                    max_pt = pt
                sc.append(pt)
                curr += stride
            # call the function to reset the variable  to its original value
            to_optimize(prev)
            inverted_maxima.append((max_pt[1], max_pt[0], sc.index(max_pt), i))
            score_lists.append(sc)
        inverted_maxima.sort(reverse=True)
        maxima = [(i[1], i[0]) for i in inverted_maxima]
        self.do_plot(score_lists, maxima, x_range=(mn, mx) )

    def do_plot(self, score_lists, maxima, x_range):
        worst_index = len(score_lists) - 1
        worst_best = maxima[worst_index]
        best_best = maxima[0]
        self.rescaled = []
        self.axes_lines = []
        self.axes_text = []
        unscaled_x_width = x_range[1] - x_range[0]
        if best_best[1] != float('-inf'):
            while (worst_best[1] == float('-inf')) and worst_index > 1:
                worst_index -= 1
                worst_best = maxima[worst_index]
            if worst_best[1] == float('-inf'):
                best_best_index = best_best[2]
                score_set_index = best_best[3]
                half_best_best_x = int(best_best_index/2)
                from_top = len(score_lists[score_set_index]) - best_best_index
                half_bigger_best_x = best_best_index + int(from_top/2)
                score_lists = score_lists[score_set_index]
                lower_sc = min(score_lists[half_best_best_x][1], score_lists[half_bigger_best_x][1])
            else:
                lower_sc = worst_best[1]

            diff = best_best[1] - lower_sc
            height_in_lnL = self.plot_y_range_mult*diff
            y_offset = diff - lower_sc
            scale = -self.drawable_height/(height_in_lnL)

            # now we rescale the points to pixels...
            for sc in score_lists:
                rsc = []
                cached = None
                prev_in_range = False
                for unscaled_x, unscaled_y in sc:
                    plot_x = self.width_offset + (unscaled_x - x_range[0])*self.width_pix/unscaled_x_width
                    plot_y = self.height_pix + scale*(unscaled_y + y_offset) 
                    if unscaled_x < x_range[0]:
                        cached = (plot_x, plot_y)
                    elif unscaled_x > x_range[1]:
                        if prev_in_range:
                            rsc.append((plot_x, plot_y))
                        prev_in_range = False
                    else:
                        if cached:
                            rsc.append(cached)
                            cached = None
                        rsc.append((plot_x, plot_y))
                        prev_in_range = True
                print "RSC = ", rsc
                self.rescaled.append(rsc)
            
            upper_axis_y = self.height_pix + scale*(best_best[1] + y_offset)
            lower_axis_y = self.height_pix 
            left_axis_x = self.width_offset
            right_axis_x = self.width_offset + self.width_pix
            mle_x = self.width_offset + (best_best[0] - x_range[0])*self.width_pix/unscaled_x_width
            mle_y = self.height_pix + scale*(best_best[1] + y_offset)
            self.axes_lines = [((left_axis_x, lower_axis_y),(right_axis_x, lower_axis_y)),
                ((left_axis_x, 2*lower_axis_y),(left_axis_x, upper_axis_y)),
                ((left_axis_x, mle_y),(mle_x, mle_y)),
                ((mle_x, lower_axis_y + font_y_offset),(mle_x, mle_y)),
                ]
            self.axes_text = [
                (((left_axis_x + right_axis_x)/2 - 3*font_x_offset, lower_axis_y + 3*font_y_offset), self.param_list[0].name),
                ((left_axis_x - 3*font_x_offset, lower_axis_y - font_y_offset), "lnL"),
                ((2, mle_y + font_y_offset), "%6.2f" % (best_best[1])),
                ((mle_x - 2*font_x_offset, lower_axis_y + 5*font_y_offset), "%6.2f" % (best_best[0])),
                ]

            # add lines for the other trees if they are above near the lower axis
            for i, sub_opt in enumerate(maxima[1:]):
                if sub_opt[1] > best_best[1] - 1.5*height_in_lnL:
                    sub_mle_x = self.width_offset + (sub_opt[0] - x_range[0])*self.width_pix/unscaled_x_width
                    sub_mle_y = self.height_pix + scale*(sub_opt[1] + y_offset)
                    self.axes_lines.append(((left_axis_x, sub_mle_y),(sub_mle_x, sub_mle_y)))
                    self.axes_lines.append(((sub_mle_x, lower_axis_y + (3*i + 4)*font_y_offset),(sub_mle_x, sub_mle_y)))
                    self.axes_text.append(((2, sub_mle_y + font_y_offset), "%6.2f" % (sub_opt[1])))
                    self.axes_text.append(((sub_mle_x - 2*font_x_offset, lower_axis_y + (3*i + 8)*font_y_offset), "%6.2f" % (sub_opt[0])))
        self.repaint()

    def paintEvent(self, event):
        if not self.rescaled:
            return

        paint = QtGui.QPainter()
        paint.begin(self)
        for i, rsc in enumerate(self.rescaled):
            pen = self.pen_list[i]
            paint.setPen(pen)
            fx, fy = rsc[0]
            for x, p in enumerate(rsc[1:]):
                sx, sy = p
                try:
                    #debug("(%d, %d) -> (%d, %d)" % (int(fx), int(fy), int(sx), int(sy)))
                    ifx, ify = int(fx), int(fy)
                    isx, isy = int(sx), int(sy)
                except:
                    pass
                else:
                    try:
                        paint.drawLine(ifx, ify, isx, isy)
                    except:
                        #pass
                        raise
                fx, fy = sx, sy

        paint.setPen(self.axis_pen)
        for axis_line in self.axes_lines:
            from_pt, to_pt = axis_line
            paint.drawLine(from_pt[0], from_pt[1], to_pt[0], to_pt[1])
        
        for axis_text_blob in self.axes_text:
            from_pt, text = axis_text_blob
            paint.drawText(from_pt[0], from_pt[1], text)
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
