try:
    from PyQt4 import QtGui, QtCore
except:
    sys.stderr.write("PyQt4 must be installed!")
    raise
font_x_offset = 10
font_y_offset = 5
        
class TopologyDisplay:
    colors = [QtCore.Qt.red, QtCore.Qt.blue, QtCore.Qt.green]
    txt_fmt = ['<font color="red">%s</font>', '<font color="blue">%s</font>', '<font color="green">%s</font>']
    best_txt_fmt = ['<font color="red"><u>%s</u></font>', '<font color="blue"><u>%s</u></font>', '<font color="green"><u>%s</u></font>']
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
