This folder contains the code used in the reproduction attempt. 
Below there is a short description of each of the files. 
Instructions are found in the comments in the beginning of each code file.

The data for Fig 3A was downloaded from https://cs.joensuu.fi/sipu/datasets/Aggregation.txt
The data for Fig 3C was downlaoded from https://cs.joensuu.fi/sipu/datasets/flame.txt
The data for Fig 3D was downloaded from https://cs.joensuu.fi/sipu/datasets/spiral.txt
The data for Olivetti was downlaoded from http://people.sissa.it/~laio/Research/Clustering_source_code/distances_olivetti.dat
The data for Fig S6 was downloaded from https://cs.joensuu.fi/sipu/datasets/dim256.txt
The data for Fig S7 was downloaded from https://archive.ics.uci.edu/ml/machine-learning-databases/00236/seeds_dataset.txt
  
Clustering-Method.txt contains a description of the changes made to the source code to reproduce the results in the article. 

Pre-Processing.py is used to process datasets. 
It takes a text file with coordinates of points and returns a dat file with distances. 
The Olivetti data set is the only data set which was in a pre-processed state. 
The others were processed by using the Pre-Processing.py

Plot-3A.py is used to plot the Figure 3A from the output from the source code. 

Calculate-Olivetti-Result.py is used to calculate the metric for the Olivetti dataset.

Calculate-S6-Result.py is used to check if the clustering of the dataset used in Figure S6 is correct.

Calculate-S7-Result.py is used to calculate the metric for the dataset used in Figure S7.

