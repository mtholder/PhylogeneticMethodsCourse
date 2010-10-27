#!/usr/bin/env python
f = open("r","rU")
row = [0.0]*100
mat = [list(row) for i in xrange(50)]
for n, line in enumerate(f):
    ls = [float(i) for i in line.split()]
    for j, v in enumerate(ls):
        mat[j][n] = v
f.close()


f = open("transposedR","w")
for row in mat:
    f.write(" ".join([str(i) for i in row]))
    f.write("\n")
f.close()

for row in mat:
    mean = sum(row)/len(row)
    for i in range(len(row)):
        row[i] -= mean


f = open("centeredR","w")
for row in mat:
    f.write(" ".join([str(i) for i in row]))
    f.write("\n")
f.close()

for colInd in xrange(100):
    column = [mat[rowInd][colInd] for rowInd in xrange(50)]
    mv = max(column)
    for rowInd in xrange(50):
        mat[rowInd][colInd] = mv - mat[rowInd][colInd]

f = open("maxDiffR","w")
for row in mat:
    f.write(" ".join([str(i) for i in row]))
    f.write("\n")
f.close()

diffs = [203.13967, 196.12935, 117.24391, 200.45065, 115.97927, 111.48261, 130.47016, 202.71930, 179.28198, 144.81122, 149.17189, 121.95636,  80.98998, 112.98782, 111.55729, 182.33182, 157.37861, 201.68918,  14.30567, 105.25317, 125.52924,  88.00839, 125.11395, 185.46003,  28.61099,  64.29409, 211.15960, 121.40311, 138.56016, 104.45307, 206.87110, 169.58771, 149.82506, 155.49377, 159.38475,  67.23369, 201.68919, 102.52505, 0.0, 191.39472, 101.64062, 210.67091, 138.09559, 170.61804, 146.29158,  92.53407, 178.12376, 168.63984, 209.42131,  84.61266, ]
pVals = []
for n, row in enumerate(mat):
    d = diffs[n]
    c = sum([1 for i in row if i >= d])
    pVals.append(c)

print "\n".join([str(i) for i in pVals])
