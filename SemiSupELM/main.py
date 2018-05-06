import os
import sys
import random
import numpy as np

from main_gendata import json_output_directory
from main_gendata import mat_path_coil20
from main_gendata import mat_path_g50c
from main_gendata import mat_path_uspst

from model import run_SS
import datasets

# The parameters nh below are from the main paper being reproduced, page 8
#  (2000 for all except g50c which has 1000)
# The other parameters (NN, sigma) are from [57, melacci] cited in the same
#  paper, in the table on page 31 (1179).
# Sigma not used, but is a hyperparameter from a paper the paper being reproduced
#  cites, although results using this are so poor it is only reasonable to assume there
#  is a problem with interpretation or implementation.
#  Instead, sigma is calculated based on the sigma (stdev) of the dataset
#   (this sounds reasonable, considering the scaling in the gaussian then depends on
#    the data itself, the weight-values being similar for different datasets)
def coil20(L,U,V,T):
    nh = 2000;  NN = 2;  sigma = 0.6
    return run_SS(labeled=L, unlabeled=U, validation=V, test=T, nh=nh, NN=NN, sigma=sigma)

def coil20b(L,U,V,T):
    nh = 2000;  NN = 2;  sigma = 0.6
    return run_SS(labeled=L, unlabeled=U, validation=V, test=T, nh=nh, NN=NN, sigma=sigma)

def g50c(L,U,V,T):
    nh = 1000;  NN = 50;  sigma = 17.5
    return run_SS(labeled=L, unlabeled=U, validation=V, test=T, nh=nh, NN=NN, sigma=sigma)

def uspst(L,U,V,T):
    nh = 2000;  NN = 15;  sigma = 9.4
    return run_SS(labeled=L, unlabeled=U, validation=V, test=T, nh=nh, NN=NN, sigma=sigma)

def uspstb(L,U,V,T):
    nh = 2000;  NN = 15;  sigma = 9.4
    return run_SS(labeled=L, unlabeled=U, validation=V, test=T, nh=nh, NN=NN, sigma=sigma)


def main_SS(experiment_name, experiment_function, json_path, dataset_path, add_biases, binarize, offset=0):
    """Given an experiment function (e.g coil20),
       The path to a json-file containing the list of dicts where each dict has
        the indices of each set (training (L,U,V), test (T)),
       The path to the original .mat file of the dataset,
       A boolean of whether to add bias-entries to the dataset,
       Whether to binarize an otherwise multiclass dataset,
       And an offset to the random seed,

       Perform k-fold cross validation using the SS-ELM algorithm described
       in the paper.
    """
    seed = 64 + offset
    random.seed(seed)
    np.random.seed(seed)
    print(("Running SS experiment {} using folds {} and dataset {}, " +
          "with binarize={} and random seed={}").format(experiment_name,
                                                        json_path,
                                                        dataset_path,
                                                        binarize,
                                                        seed))

    json_data = datasets.load_json(json_path)
    main_data = datasets.load_dataset(dataset_path, add_biases, binarize)
    results = []
    right = 0
    wrong = 0
    print("Number of invocations (test set folds): {}".format(len(json_data)))
    for i,fold in enumerate(json_data):
        print("Fold {}/{}:".format(i+1,len(json_data)))
        L,U,V,T = datasets.dict_to_numpy(fold, main_data)
        predicted_labels,correct_labels,num_correct,num_wrong = coil20(L,U,V,T)
        indices = np.matrix(fold['T']).transpose()
        fold_number = np.empty_like(indices)
        fold_number.fill(i)

        csv_rows = np.hstack([indices, predicted_labels, correct_labels, fold_number])
        results.extend(csv_rows)
        right += num_correct
        wrong += num_wrong

    # add a .csv or a .summary extension afterwards
    results_pathname = datasets.create_results_path(experiment_name)
    datasets.results_to_csv(results, results_pathname + '.csv')
    s = datasets.save_summary(right, wrong, results_pathname + '.summary')
    print(s)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        experiment = "print_usage_info"
    else:
        experiment = sys.argv[1]
        partition_path = sys.argv[2]


    if experiment == "coil20":
        main_SS(experiment, coil20, partition_path, mat_path_coil20, True, False, offset=0)
    elif experiment == "coil20b":
        main_SS(experiment, coil20b, partition_path, mat_path_coil20, True, True, offset=1)
    elif experiment == "g50c":
        main_SS(experiment, g50c, partition_path, mat_path_g50c, True, False, offset=2)
    elif experiment == "uspst":
        main_SS(experiment, uspst, partition_path, mat_path_uspst, True, False, offset=3)
    elif experiment == "uspstb":
        main_SS(experiment, uspstb, partition_path, mat_path_uspst, True, True, offset=4)
    else:
        print("Usage example: \n" +
              "  python3 main.py coil20 idx_datasets/pregen/coil20.json\n" +
              "or\n" +
              "  python3 main_runall.py")
