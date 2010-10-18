import math
base1 = 'A'
base2 = 'A'
base3 = 'G'
base4 = 'C'
len1 = 0.05
len2 = 0.05
len3 = 0.4
len4 = 0.4
lenInternal = 0.05

def prob_no_change(nu, kappa):
    tpk = 2 + kappa 
    return 0.25*(1 + math.exp(-4.0*nu/(tpk)) + 2*math.exp(-(2*nu*(1 + kappa)/(tpk))))

def prob_ti(nu, kappa):
    tpk = 2 + kappa 
    return 0.25*(1 + math.exp(-4.0*nu/(2.0+kappa)) - 2*math.exp(-(2*nu*(1 + kappa)/(tpk))))

def prob_tv(nu, kappa):
    return 0.25*(1 - math.exp(-4.0*nu/(2.0+kappa)))

def calc_prob(to_b, from_b, nu, kappa):
    ti_dict = {'A':'G', 'G':'A', 'T':'C', 'C':'T'}
    if to_b == from_b:
        p = prob_no_change(nu, kappa)
    elif to_b == ti_dict[from_b]:
        p = prob_ti(nu, kappa)
    else:
        p = prob_tv(nu, kappa)
    print "Pr(", from_b, "->", to_b, " | nu =", nu, ") =", p
    return p

kappa = 2

for nu in [0.05, 0.4]:
    print "Pr(A->A | nu = ", nu, ") = ", prob_no_change(nu, kappa)
    print "Pr(A->G | nu = ", nu, ") = ", prob_ti(nu, kappa)
    print "Pr(A->C | nu = ", nu, ") = ", prob_tv(nu, kappa)

anc_prob = {}

for baseAnc24 in 'ACGT':
    pr_anc_to_2 = calc_prob(base2, baseAnc24, len2, kappa)
    pr_anc_to_4 = calc_prob(base4, baseAnc24, len4, kappa)
    anc_prob[baseAnc24]  = pr_anc_to_2*pr_anc_to_4

total_prob = 0.0
for root in 'ACGT':
    pr_root_to_1 = calc_prob(base1, root, len1, kappa)
    pr_root_to_3 = calc_prob(base3, root, len3, kappa)
    f = pr_root_to_1*pr_root_to_3
    pr_root_to_24 = 0.0
    for baseAnc24 in 'ACGT':
        t = anc_prob[baseAnc24]*calc_prob(baseAnc24, root, lenInternal, kappa)
        pr_root_to_24 += t
        
        print "\n*** Pr from root=",root, "and other internal=", baseAnc24, "=", 0.25*f*t, "\n"
    total_prob += f*pr_root_to_24*0.25
print "character likelihood =", total_prob
print "character lnL =", math.log(total_prob)
