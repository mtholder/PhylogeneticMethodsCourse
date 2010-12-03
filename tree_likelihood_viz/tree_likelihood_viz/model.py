#!/usr/bin/env python
class DataConditioning:
    NONE, VARIABLE, PARSIMONY_INFORMATIVE, VARIABLE_SHOW_CONST = range(4)

class Parameter(object):
    def __init__(self, name, value, min_val=None, max_val=None):
        self.name = name
        self._value = value
        self.min_val = min_val
        self.max_val = max_val
        self.set_value_listeners = []
    def assert_legal(self, x):
        if x < self.min_val:
            raise ValueError("Value %(x)f is below the minimum %(m)s" % {'x':x, 'm':self.min_val})
        if x > self.max_val:
            raise ValueError("Value %(x)f is above the maximum %(m)s" % {'x':x, 'm':self.max_val})
        
    def restrict_to_legal_range(self, x):
        if x < self.min_val:
            return self.min_val
        if x > self.max_val:
            return self.max_val
        return x
    def set_value(self, x):
        self.assert_legal(x)
        self._value = x
        for v in self.set_value_listeners:
            v(x)
    def get_value(self):
        return self._value
    value = property(get_value, set_value)

class Model(object):
    def __init__(self, param_list=None):
        if param_list is None:
            self._param_list = []
        else:
            self._param_list = param_list
    def get_params(self):
        return self._param_list
    def get_num_params(self):
        return len(self._param_list)
    param_list = property(get_params)
    num_params = property(get_num_params)
    
    def find_independent_params(self):
        '''Returns:
            (list of unique parameters in order, dict mapping parameter to index in param_list)
            
            This is useful when wading through all of the parameters in a model.
        '''
        d = {}
        vec = []
        for i, p in enumerate(self.param_list):
            if p not in d:
                d[p] = i
                vec.append(p)
        return vec, d


class BranchLengthModel(Model):
    SEPARATE_LENGTH, EQUAL_LENGTHS = (0,1)
    PROB_CHANGE, EXPECTED_NUM_CHANGES = (0,1)
    def __init__(self, param_list, interpretation=PROB_CHANGE):
        Model.__init__(self, param_list)
        self.interpretation = interpretation

class CharModel(Model):
    def __init__(self, param_list=None, **kwargs):
        Model.__init__(self, param_list)
        self.branch_length_mode = kwargs.get('branch_length_mode', BranchLengthModel.PROB_CHANGE) 
        self.conditioning = DataConditioning.NONE

    def get_num_states(self):
        return self.__class__.NUM_STATES
    num_states = property(get_num_states)

    def get_max_branch_length(self):
        if self.branch_length_mode == BranchLengthModel.PROB_CHANGE:
            return float(self.num_states - 1) / self.num_states 
        return float('inf')
    max_branch_length = property(get_max_branch_length)


class CFN(CharModel):
    NUM_STATES = 2
    def __init__(self, **kwargs):
        CharModel.__init__(self, **kwargs)

class CFNPinv(CFN):
    def __init__(self, **kwargs):
        self.pinv = Parameter(name='pinv', value=0.01, min_val=0.0, max_val=1.0)
        parameter_list = [self.pinv]
        CFN.__init__(self, param_list=parameter_list, **kwargs)
    def get_pinv(self):
        return self.pinv.value

class CFNVar(CFN):
    def __init__(self, **kwargs):
        CFN.__init__(self, **kwargs)
        self.conditioning = DataConditioning.VARIABLE_SHOW_CONST

class CompatModel(CharModel):
    NUM_STATES = 2
    def __init__(self, param_list, **kwargs):
        CharModel.__init__(self, param_list=param_list, **kwargs)
        self.conditioning = DataConditioning.VARIABLE

class TreeModel(Model):
    def __init__(self, char_model, branch_length_model):
        self.char_model = char_model
        self.branch_length_model = branch_length_model
        p = list(char_model.param_list)
        p.extend(branch_length_model.param_list)
        Model.__init__(self, p)
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
