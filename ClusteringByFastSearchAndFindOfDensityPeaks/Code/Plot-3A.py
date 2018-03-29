#Plots the clusters from Figure 3A. This includes the points not found in the halo.
#
#Running the code:
#Download the .txt file with the dataset from https://cs.joensuu.fi/sipu/datasets/Aggregation.txt
#Use it to run the clustering (cluster_dp.m)
#Put Aggregation.txt in the same folder as Plot-3A.py (this file)
#Put the output file (CLUSTER_ASSIGNATION) from the clustering method in the same folder as Plot-3A.py (this file)
#Run this code to get the plot.

from matplotlib import pyplot as plt

file = open('Aggregation.txt', 'r')

clusters = open('CLUSTER_ASSIGNATION', 'r')

points = []
for line in file:
    parts = line.split()
    points.append([float(parts[0]), float(parts[1]), -1])

clusterTypes = []
index = 0
for cluster in clusters:
    parts = cluster.split()
    value = int(parts[1])
    if value not in clusterTypes:
        clusterTypes.append(value)
    points[index][2] = value
    index += 1

plotPoints = []
for j in range(len(clusterTypes)):
    plotPoints.append([])
for p in points:
    i = p[2] - 1
    plotPoints[i].append([p[0], p[1]])

colors = ['red', 'blue', 'green', 'yellow', 'purple', 'black', 'orange']

colorIndex = 0

for tpoint in plotPoints:

    for x, y in tpoint:
        plt.scatter(x, y, color=colors[colorIndex])
    colorIndex += 1

plt.show()
