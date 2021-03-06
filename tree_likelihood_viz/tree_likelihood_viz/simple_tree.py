#!/usr/bin/env python
from tree_likelihood_viz.utility import debug
from tree_likelihood_viz.model import Parameter, CharModel, DataConditioning, BranchLengthModel, CFN, CFNPinv, CompatModel
class BranchEnum:
    A, B, INTERNAL, C, D = 0, 1, 2, 3, 4
    names = ["A", "B", "Internal", "C", "D"]


class TopologyEnum:
    AB, AC, AD = 0, 1, 2
    order = [0, 1, 2]
    names = ["AB | CD", "AC | BD", "AD | BC"]

PATTERN_NAMES = ('0000', '0001', '0010', '0011', '0100', '0101', '0110', '0111')

def generate_branch_length_model(topology, char_model):
    mn = 0.0
    mx = char_model.max_branch_length
    assert (mn <= mx)
    mode = char_model.branch_length_mode
    value = mn + 0.1
    if value > mx:
        value = max(mn, mn + (mx-mn)/2.0)
    p = [Parameter(name=BranchEnum.names[i], value=value, min_val=mn, max_val=mx) for i in range(5)]
    return BranchLengthModel(p, interpretation=mode)

class Tree(object):
    def __init__(self, topology, char_model, branch_length_model, fixed_params=None):
        self.topology = topology
        self.num_branches = 5 # currently only fully resolved, unrooted trees are supported
        self.branch_length_model = branch_length_model
        self.branch_length_list = branch_length_model.param_list
        assert(len(branch_length_model.param_list) == self.num_branches)
        self.fixed_params = []
        if fixed_params:
            self.fixed_params.extend(fixed_params)
        # figure out what sets of branch lengths are free to vary
        self.indep_branches, self.branch_len_to_indep_ind = branch_length_model.find_independent_params()
 
        self.char_model = char_model
        self.indep_subst_params, self.subst_param_to_ind = char_model.find_independent_params()
        self.pat_prob_calc_callbacks = []
            
    def get_name(self):
        return TopologyEnum.names[self.topology]
    name = property(get_name)

    def branch_is_free(self, p):
        return (p in self.branch_len_to_indep_ind) and (p not in self.fixed_params)
    def model_param_is_free(self, p):
        return (p in self.subst_param_to_ind) and (p not in self.fixed_params)

    def get_br_lens(self):
        return [i.value for i in self.branch_length_list]


    def get_funky_ordered_br_lens(self):
        if self.topology == TopologyEnum.AB:
            return self.get_br_lens()
        a_ch, b_ch, int_ch, c_ch, d_ch = self.get_br_lens()
        if self.topology == TopologyEnum.AC:
            b_ch, c_ch = c_ch, b_ch
        else:
            b_ch, c_ch, d_ch = d_ch, b_ch, c_ch
        return a_ch, b_ch, int_ch, c_ch, d_ch

    def calc_pat_p_scores(self):
        """Pattern parsimony scores returned in order:
        A  00000000
        B  00001111
        C  00110011
        D  01010101
        """
        if self.topology == TopologyEnum.AB:
            return (0, 1, 1, 1, 1, 2, 2, 1)
        elif self.topology == TopologyEnum.AC:
            return (0, 1, 1, 2, 1, 1, 2, 1)
        return (0, 1, 1, 2, 1, 2, 1, 1)

    def calc_pat_probs(self, alert_pat_prob_listener=True):
        if isinstance(self.char_model, CFNPinv):
            return self.calc_pat_probs_cfn_pinv(alert_pat_prob_listener=alert_pat_prob_listener)
        elif isinstance(self.char_model, CFN):
            return self.calc_pat_probs_cfn(alert_pat_prob_listener=alert_pat_prob_listener)
        elif isinstance(self.char_model, CompatModel):
            return self.calc_pat_probs_compat(alert_pat_prob_listener=alert_pat_prob_listener)

    def calc_pat_probs_compat(self, alert_pat_prob_listener=True):
        assert(self.char_model.conditioning == DataConditioning.VARIABLE)
        pars_scores = self.calc_pat_p_scores()
        params = self.char_model.param_list
        assert(len(params) == 1)
        epsilon = params[0].value
        noisy_char_prob = 1/7.0 # assuming binary characters, and only variable sites
        perfect_prob = 0.2 # assuming binary, 4-leaf tree
        prob_list = [0.0]
        incompat_prob = epsilon*noisy_char_prob
        compat_prob = (1.0 - epsilon)*perfect_prob + incompat_prob
        for pars_score in pars_scores[1:]:
            if pars_score == 1:
                prob_list.append(compat_prob)
            else:
                prob_list.append(incompat_prob)
        x = self.apply_conditioning_to_prob_vector(prob_list)
        if alert_pat_prob_listener:
            for listener in self.pat_prob_calc_callbacks:
                listener()
        return x
    
    def calc_pat_probs_cfn_pinv(self, alert_pat_prob_listener=True):
        x = self.calc_pat_probs_cfn(False)
        
        if alert_pat_prob_listener:
            for listener in self.pat_prob_calc_callbacks:
                listener()
        pinv = self.char_model.get_pinv()
        omp = 1.0 - pinv
        x = [omp * i for i in x]
        x[0] += pinv
        return x

    def calc_pat_probs_cfn(self, alert_pat_prob_listener=True):
        """Pattern likelihoods returned in order (assumes CFN with A=0),
        A  00000000
        B  00001111
        C  00110011
        D  01010101
        """
        b = self.get_funky_ordered_br_lens()
        a_ch, b_ch, int_ch, c_ch, d_ch = b
        a_no_ch, b_no_ch, int_no_ch, c_no_ch, d_no_ch = [1.0 - i for i in b]
        # print "b = ", b
        # ab anc
        ab0, ab1= a_no_ch, a_ch
        # ab anc and b
        b0ab0 = ab0*b_no_ch
        b1ab0 = ab0*b_ch
        b0ab1 = ab1*b_ch
        b1ab1 = ab1*b_no_ch
        # print b0ab0, b1ab0, b0ab1, b1ab1
        # ab anc, b and cd anc
        b0ab0cd0 = b0ab0*int_no_ch
        b0ab0cd1 = b0ab0*int_ch
        b1ab0cd0 = b1ab0*int_no_ch
        b1ab0cd1 = b1ab0*int_ch
        b0ab1cd0 = b0ab1*int_ch
        b0ab1cd1 = b0ab1*int_no_ch
        b1ab1cd0 = b1ab1*int_ch
        b1ab1cd1 = b1ab1*int_no_ch
        # b and cd anc
        b0cd0 = b0ab0cd0 + b0ab1cd0
        b1cd0 = b1ab0cd0 + b1ab1cd0
        b0cd1 = b0ab0cd1 + b0ab1cd1
        b1cd1 = b1ab0cd1 + b1ab1cd1
        # b, c and cd anc
        b0cd0c0 = b0cd0*c_no_ch
        b0cd0c1 = b0cd0*c_ch
        b1cd0c0 = b1cd0*c_no_ch
        b1cd0c1 = b1cd0*c_ch
        b0cd1c0 = b0cd1*c_ch
        b0cd1c1 = b0cd1*c_no_ch
        b1cd1c0 = b1cd1*c_ch
        b1cd1c1 = b1cd1*c_no_ch
        # b, c, d and cd anc
        b0cd0c0d0 = b0cd0c0*d_no_ch
        b0cd0c0d1 = b0cd0c0*d_ch
        b0cd0c1d0 = b0cd0c1*d_no_ch
        b0cd0c1d1 = b0cd0c1*d_ch
        b1cd0c0d0 = b1cd0c0*d_no_ch
        b1cd0c0d1 = b1cd0c0*d_ch
        b1cd0c1d0 = b1cd0c1*d_no_ch
        b1cd0c1d1 = b1cd0c1*d_ch
        b0cd1c0d0 = b0cd1c0*d_ch
        b0cd1c0d1 = b0cd1c0*d_no_ch
        b0cd1c1d0 = b0cd1c1*d_ch
        b0cd1c1d1 = b0cd1c1*d_no_ch
        b1cd1c0d0 = b1cd1c0*d_ch
        b1cd1c0d1 = b1cd1c0*d_no_ch
        b1cd1c1d0 = b1cd1c1*d_ch
        b1cd1c1d1 = b1cd1c1*d_no_ch
        # b, c, d
        b0c0d0 = b0cd0c0d0 + b0cd1c0d0
        b0c0d1 = b0cd0c0d1 + b0cd1c0d1
        b0c1d0 = b0cd0c1d0 + b0cd1c1d0
        b0c1d1 = b0cd0c1d1 + b0cd1c1d1
        b1c0d0 = b1cd0c0d0 + b1cd1c0d0
        b1c0d1 = b1cd0c0d1 + b1cd1c0d1
        b1c1d0 = b1cd0c1d0 + b1cd1c1d0
        b1c1d1 = b1cd0c1d1 + b1cd1c1d1
        # swap elements
        if self.topology == TopologyEnum.AC:
            b0c0d0 , b0c0d1 , b0c1d0 , b0c1d1 , b1c0d0 , b1c0d1 , b1c1d0 , b1c1d1 = (b0c0d0 , b0c0d1 , b1c0d0 , b1c0d1 , b0c1d0 , b0c1d1 , b1c1d0 , b1c1d1)
        elif self.topology == TopologyEnum.AD:
            b0c0d0 , b0c0d1 , b0c1d0 , b0c1d1 , b1c0d0 , b1c0d1 , b1c1d0 , b1c1d1 = (b0c0d0 , b1c0d0 , b0c0d1 , b1c0d1 , b0c1d0 , b1c1d0 , b0c1d1 , b1c1d1)
        # return with d = ones bit, c = 2's bit, d = 4's bit
        v = (b0c0d0 , b0c0d1 , b0c1d0 , b0c1d1 , b1c0d0 , b1c0d1 , b1c1d0 , b1c1d1)
        x = self.apply_conditioning_to_prob_vector(v)
        if alert_pat_prob_listener:
            for listener in self.pat_prob_calc_callbacks:
                listener()
        return x

    def apply_conditioning_to_prob_vector(self, v):
        if self.char_model.conditioning == DataConditioning.NONE:
            return v
        
        if self.char_model.conditioning == DataConditioning.VARIABLE \
            or ( self.char_model.conditioning == DataConditioning.VARIABLE_SHOW_CONST):
            sub_list = v[1:]
        else:
            assert(self.char_model.conditioning == DataConditioning.PARSIMONY_INFORMATIVE)
            sub_list = [v[3], v[5], v[6]]
        s = sum(sub_list)
        t = tuple([i/s for i in sub_list])
        if (self.char_model.conditioning == DataConditioning.VARIABLE_SHOW_CONST):
            t = tuple([0.0] + list(t))
        #debug('conditioned = %s' % str(t))
        return t
    def get_pat_names(self):
        if self.char_model.conditioning == DataConditioning.NONE \
            or self.char_model.conditioning == DataConditioning.VARIABLE_SHOW_CONST:
            return PATTERN_NAMES
        elif self.char_model.conditioning == DataConditioning.VARIABLE:
            return tuple(PATTERN_NAMES[1:])
        else:
            assert(self.char_model.conditioning == DataConditioning.PARSIMONY_INFORMATIVE)
            return (PATTERN_NAMES[3], PATTERN_NAMES[5], PATTERN_NAMES[6])

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
