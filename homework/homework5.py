import math, itertools
pd = [0.19, 0.1, 0.25, 0.25, 0.11, 0.25]
patd = [0.21, 0.12, 0.25, 0.23, 0.12, 0.27]

def jc_corr(p):
    return -.75*math.log(1.0-4*p/3.0)
c = [jc_corr(i) for i in pd]
sse = 0.0
for p_el, c_el, pat_el in itertools.izip(pd, c, patd):
    diff = c_el - pat_el
    diff_sq = diff*diff
    sse += diff_sq
    to_print = (p_el, c_el, pat_el, diff, diff_sq)
    print ' & '.join([str(i) for i in to_print])
print 'sse = ', sse 
