#!/usr/bin/env python
import os, sys
prog_name = os.path.split(sys.argv[0])[1]
ofname = "sitelikesforconsel.txt"
if os.path.exists(ofname):
    sys.exit('The file "%s" already exists. Move it before running %s' % (ofname, prog_name))
try:
    infilename = sys.argv[1]
except:
    sys.exit("Expecting the name of a PAUP sitelikelihoods file as an argument")

try:
    infilestream = open(infilename, 'rU')
except:
    sys.exit("Could not open the file \"%s\"" % infilename)

fiter = iter(infilestream)
try:
    first_line = fiter.next().strip().split()
    assert(first_line[0] == "Tree")
    assert(first_line[1] == "-lnL")
    assert(first_line[-2] == "Site")
    assert(first_line[-1] == "-lnL")
except:
    sys.exit('Expecting the first line to begin with "Tree\t-lnL\t...\tSite\t-lnL"')

ofstream = open(ofname, 'w')
ofstream.write('Tree\t-lnL\tSite\t-lnL\n')
buffered = []
for line in fiter:
    if line.startswith('\t'):
        buffered.append(line.strip().split())
    else:
        sp = line.strip().split()
        ofstream.write('\t'.join(sp[:2]) + '\n')
        for b in buffered:
            ofstream.write('\t\t%s\n' % '\t'.join(b[:2]))
            buffered = []
sys.stderr.write('The file "%s" should now contain the site lnL values in a form that is readable by consel.\n' % ofname)
            
