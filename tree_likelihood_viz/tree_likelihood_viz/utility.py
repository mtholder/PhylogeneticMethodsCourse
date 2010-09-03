#!/usr/bin/env python
import sys
import os
import random
def randomly_choose_indices(p, n):
    """Treats `p` as a list of category probabilities.  Returns as list of `n`
    indices that were randomly drawn from this discrete probability distribution.
    Does not verify that sum(p) == 1.0.  All rounding error is "given" to the
    list category.
    """
    last_ind = len(p) - 1
    c = [0]*len(p)
    for i in xrange(n):
        u = random.random()
        ind = 0
        while ind < last_ind:
            u -= p[ind]
            if u < 0.0:
                break
            ind += 1
        c[ind] = c[ind] + 1
    return c


def parse_counts_from_fn(pattern_count_filename, num_patterns):
    sys.stderr.write('Attempting to read pattern counts from  "%(pcf)s" ...' % {'pcf':pattern_count_filename})
    inp = open(pattern_count_filename, 'rU')
    pcd = [float(i.strip()) for i in inp if i.strip()]
    assert len(pcd) >=num_patterns
    for i in pcd:
        assert i >= 0.0
    return pcd[:num_patterns]


def obtain_initial_pattern_counts(num_patterns):
    '''if PATTERN_COUNT_FILE is in the environment, then that file path is read
    as a count of patterns (one float per line).
    '''
    pattern_count_filename = os.environ.get("PATTERN_COUNT_FILE")

    if pattern_count_filename:
        try:
            pattern_count_data = parse_counts_from_fn(pattern_count_filename, num_patterns)
        except:
            sys.exit("Expecting %s to be a file of pattern counts (one-per line)." % pattern_count_filename)
    else:
        pattern_count_data = [0]*num_patterns
    return pattern_count_data

def debug(msg):
    sys.stderr.write('debug: %s\n' % msg)

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
