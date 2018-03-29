#Processes datasets
#The Input.txt is the dataset with n rows, where the first n-1 rows are coordinates.
#The Output.dat is the preprocessed version of the Input.txt. It contains three rows.
#The two first is the index (1 indexed) of the points in Input.txt and the third row is the distance between those points.
#
#Running the Code:
#Put the .txt file with the data in the same folder as this file
#Change the 'Input.txt' (line 11) to the name of the data.
#Run the Code


import math
import scipy.spatial

file = open('Input.txt', 'r')

points = []

output = []

for line in file:
    parts = line.split()[:-1]
    vector = []
    for p in parts:
        vector.append(float(p))

    points.append(vector)

for i in range(1, 1 + len(points)):
    for j in range(1, 1 + len(points)):
        dist = scipy.spatial.distance.euclidean(points[i-1], points[j-1])
        newStr = str(i) + "\t" + str(j) + "\t" + str(dist) + "\n"
        output.append(newStr)

fileOutput = open('Output.dat', 'w')

for o in output:
    fileOutput.write(o)

fileOutput.close()
