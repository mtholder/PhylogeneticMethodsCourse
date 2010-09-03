#!/usr/bin/env python
import math
from tree_likelihood_viz.utility import debug

TOL = 0.000001
PARAM_TOL = 0.00001
def calc_ln_L_from_counts(counts, freqs):
    sum = 0.0
    for n, c in enumerate(counts):
        if c > 0:
            f = freqs[n]
            try:
                char_ln_l = c*math.log(f)
            except ValueError:
                return float('-inf')
            sum += char_ln_l
    return sum

class TreeLikelihoodFunc(object):
    def __init__(self, tree, data, parameter):
        self.tree = tree
        self.data = data
        self.parameter = parameter
    def __call__(self, v):
        self.parameter.value = v
        curr_pat_p = self.tree.calc_pat_probs()
        return calc_ln_L_from_counts(self.data, curr_pat_p)

def do_opt(f, parameter, curr_step):
    curr_v = parameter.value
    curr_lnL = f(curr_v)
    best_v, best_lnL = curr_v, curr_lnL
    lower_lnL = None
    lower_v = curr_v
    higher_lnL = None
    higher_v = curr_v
    while True:
        if lower_lnL is not None and lower_lnL - TOL > curr_lnL:
            curr_v, curr_lnL = lower_v, lower_lnL
            parameter.value = curr_v
        elif higher_lnL is not None and  higher_lnL - TOL > curr_lnL:
            curr_v, curr_lnL = higher_v, higher_lnL
        else:
            if (higher_lnL is not None) and (lower_lnL is not None):
                lnLConv = ((abs(lower_lnL - curr_lnL) < TOL) and (abs(lower_lnL - curr_lnL) < TOL)) 
                lnLBad = curr_lnL == float('-inf')
                paramConv = ((higher_v - lower_v) < PARAM_TOL*curr_v)
                if lnLConv or lnLBad or paramConv:
                    parameter.value = curr_v
                    return curr_v, curr_lnL
                    parameter.value = curr_v
                    return curr_v, curr_lnL
            curr_step /= 2
        best_v, best_lnL = curr_v, curr_lnL
        lower_v = parameter.restrict_to_legal_range(curr_v - curr_step)
        lower_lnL = f(lower_v)
        higher_v = parameter.restrict_to_legal_range(curr_v + curr_step)
        higher_lnL = f(higher_v)
        #debug('In do_opt curr = %s lower = %s higher %s' % (str((curr_v, curr_lnL)), str((lower_v, lower_lnL)), str((higher_v, higher_lnL))))
