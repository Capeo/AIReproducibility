#Calculates the metric used to evaluate the Olivetti dataset result
#
#Running the code:
#Download the .txt file with the dataset from http://people.sissa.it/~laio/Research/Clustering_source_code/distances_olivetti.dat
#Use it to run the clustering (cluster_dp.m)
#Put the output file (CLUSTER_ASSIGNATION) from the clustering method in the same folder as Calculate-Olivetti-Result.py (this file)
#Run this code to get the result.

from matplotlib import pyplot as plt

def differenceWithin(vector):
    rT = 0
    total = 0
    for k in range(len(vector)):
        for l in range(k+1, len(vector)):
            total += 1
            if vector[k] == vector[l]:
                rT += 1

    return total, rT

def differenceBetween(a, b):
    rF = 0
    total = 0
    for k in range(len(a)):
        for l in range(len(b)):
            total += 1
            if a[k] == b[l]:
                rF += 1
    return total, rF

file = open('CLUSTER_ASSIGNATION', 'r')

matrix = []

cc = 0

for line in file:
    if cc % 10 == 0:
        matrix.append([])
    cc += 1
    parts = line.split()
    nn = int(parts[1])
    matrix[-1].append(nn)
    
    

rTrue = 0
rTTotal = 0
rFalse = 0
rFTotal = 0

for i in range(len(matrix)):
    row = matrix[i]

    rTTotalInc, rTrueInc = differenceWithin(row)
    rTrue += rTrueInc
    rTTotal += rTTotalInc

    for j in range(i+1, len(matrix)):
        rFTotalInc, rFalseInc = differenceBetween(row, matrix[j])
        rFalse += rFalseInc
        rFTotal += rFTotalInc

rTrueRatio = (float(rTrue) / float(rTTotal)) * 100
rFalseRatio = (float(rFalse) / float(rFTotal)) * 100
print("rTrueRatio", rTrueRatio, " rFalseRatio", rFalseRatio)
