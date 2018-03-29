#Calculate the percentage of points from the dataset used in Figure S7 in cluster cores correctly classified
#
#Running the Code:
#Download the .txt file with the dataset from https://archive.ics.uci.edu/ml/machine-learning-databases/00236/seeds_dataset.txt
#Use it to run the clustering (cluster_dp.m)
#Put seeds_dataset.txt in the same folder as Calculate-S7-Result.py (this file)
#Put the output file (CLUSTER_ASSIGNATION) from the clustering method in the same folder as Calculate-S7-Result.py (this file)
#Run this code to get the result.

file = open('CLUSTER_ASSIGNATION', 'r')
file_truths = open('seeds_dataset.txt', 'r')

clusters = []

for line in file:
    parts = line.split()
    clusterID = int(parts[2])
    clusters.append(clusterID)

truths = []

for line in file_truths:
    parts = line.split()
    clusterID = int(parts[-1])
    truths.append(clusterID)

total = 0.0
correctPoints = 0.0

for i in range(len(truths)):
    if clusters[i] == truths[i]:
        correctPoints += 1

    if clusters[i] != 0:
        total += 1

correctRatio = correctPoints / total
correctPercent = correctRatio * 100

print(correctPercent,'% of points in cluster cores correctly classified', sep='')


    

