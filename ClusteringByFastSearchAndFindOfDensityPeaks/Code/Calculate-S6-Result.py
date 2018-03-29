#Checks whether all points from the clustering of the dataset used in Figure S6 are in the correct cluster.
#
#Running the Code:
#Download the .txt file with the dataset from https://cs.joensuu.fi/sipu/datasets/dim256.txt
#Use it to run the clustering (cluster_dp.m)
#Put the output file (CLUSTER_ASSIGNATION) from the clustering method in the same folder as Calculate-S6-Result.py (this file)
#Run this code to get the result.


def isAllPointsInRightCluster():

    file = open('CLUSTER_ASSIGNATION', 'r')

    clusters = []
    counter = 0

    for line in file:
        parts = line.split()
        clusterID = int(parts[1])

        if counter % 16 == 0:
            clusters.append(clusterID)

        counter += 1

        if clusterID != clusters[-1]:
            return False


    return True


if isAllPointsInRightCluster():
    print('Success: All points are clustered correctly')
else:
    print('Failure: Not all points are clustered correctly')





    

