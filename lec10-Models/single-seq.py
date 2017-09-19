#!/usr/bin/env python
from __future__ import print_function
from math import log
import sys

n_a, n_c, n_g, n_t = 8, 1, 3, 6


def calc_lnL(pi_a, pi_c, pi_g):
    pi_t = 1 - pi_a - pi_c - pi_g
    return sum([n_a*log(pi_a),
                n_c*log(pi_c),
                n_g*log(pi_g),
                n_t*log(pi_t),
               ])

if __name__ == '__main__':
    tf = [float(i) for i in sys.argv[1:]]
    pi_a, pi_c, pi_g = tf
    lnL = calc_lnL(pi_a, pi_c, pi_g)
    print("Interpreting the args as base frequencies:")
    print("pi_a = {}, pi_c={}, pi_g={}, lnL = {}".format(pi_a, pi_c, pi_g, lnL))

    pi_r, pi_a_g_r, pi_c_g_y = tf
    pi_a = pi_r*pi_a_g_r
    pi_g = pi_r*(1 - pi_a_g_r)
    pi_c = (1 - pi_r)*pi_c_g_y
    lnL = calc_lnL(pi_a, pi_c, pi_g)
    print("Interpreting the args as P(R), P(A|R), and P(C|Y):")
    print("pi_a = {}, pi_c={}, pi_g={}, lnL = {}".format(pi_a, pi_c, pi_g, lnL))


    n = float(n_a + n_c + n_g + n_t)
    pi_a = n_a/n
    pi_c = n_c/n
    pi_g = n_g/n
    lnL = calc_lnL(pi_a, pi_c, pi_g)
    print("Unconstrained MLE:")
    print("pi_a = {}, pi_c={}, pi_g={}, lnL = {}".format(pi_a, pi_c, pi_g, lnL))
    