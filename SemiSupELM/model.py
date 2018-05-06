from scipy.stats import logistic
from sklearn.neighbors import NearestNeighbors
import numpy as np
import os
import math
import time

def gen_inlayer(ni, nh):
    """Returns a matrix niXnh that represents the mapping
       from ni to nh, obtained via matrix multiplication via an input

       H = X*W
     Nxnh = Nxni X nixnh
    """
    W = np.random.uniform(low=-1.0, high=1.0, size=(ni, nh))
    return W

def get_label_proportions(labeled, label_to_index_map):
    """return a mapping index:number_of_occurences,
       where index is the index corresponding to a class label
    """
    proportions = {}
    for label in labeled:
        assert label.size == 1
        key = label_to_index_map[label[0]]
        if key not in proportions:
            proportions[key] = 0
        proportions[key] += 1
    assert sum(proportions[key] for key in proportions) == len(labeled)
    return proportions

def adjacency(features, n_neighbors, param_sigma):
    """Calculates the adjacency weight matrix,
       as the gaussian of the distances between xi and xj
       (where xi and xj are within the n_neighbours of eachother)

       param_sigma is currently not used; it is listed as a hyperparameter
        in a paper cited by the paper being reproduced, but results with this
        listed sigma is so poor it is only reasonable to assume there is some
        mistake somewhere, either in interpretation or implementation.
    """
    def gaussian(x, sigma):
        below = 2.0*(sigma**2.0)
        E = np.exp(-(x**2.0)/below)
        return E
    func = np.vectorize(gaussian, excluded=['sigma'])
    NN = NearestNeighbors(n_neighbors=n_neighbors,
                          algorithm='auto',
                          metric='euclidean',
                          n_jobs= 1) # setting jobs higher might be faster,
                                     # though it might also cause isses with
                                     # determinism?
    NN.fit(features)

    # ALTERNATIVE 1 (weights = 1)
    #result = NN.kneighbors_graph(mode='connectivity')

    # ALTERNATIVE 2 and 3:
    result = NN.kneighbors_graph(mode='distance')
    actual_sigma = result[result != 0].std()
    #   ALTERNATIVE 2
    result[result != 0] = func(result[result != 0], actual_sigma)
    #   ALTERNATIVE 3 (results are poor with this (param))
    #result[result != 0] = func(result[result != 0], param_sigma)

    return result

def diagonals(W):
    """Calculate D^(-1/2) here because 0 to negative powers in the actual
       diagonal matrix is undefined"""
    components = np.sum(W,axis=1)
    DPM_components = np.power(components, -0.5)

    D = np.diagflat(components)
    DPM = np.diagflat(DPM_components)
    return D,DPM

def laplacian(features, n_neighbours, sigma):
    """Calculate the graph laplacian

       The paper mentions that [52] discusses a method of rather than using
        L directly, using L^p or D^(-1/2)LD^(-1/2) to normalize.
       The cited paper unfortunately is just as vague in its description of this,
        mentioning no method of selecting the integer p. [TODO]
       I can only assume that D here only raises the values on the diagonal to
        the specified power, as values elsewhere will be zero which can not be
        raised to the negative power.
    """
    W = adjacency(features, n_neighbours, sigma)
    D,DPM = diagonals(W)
    L = D - W
    DLD = DPM @ L @ DPM
    return DLD

def gen_beta(H, L, C0, lam, Y, nh, label_proportions):
    """Generates the beta matrix used in the output layer
       Worth to note is that the paper mentions in the ELM-section that
        beta can be obtained in a more stable manner rather than inverting
        explicitly, though this is never mentioned again, or the method
        described in detail.
       Instead, this section uses numpys method for inverting a matrix. TODO?
    """
    # number of samples per class label
    nlab = sum((label_proportions[key] for key in label_proportions))
    C = np.zeros_like(L)
    for key in label_proportions:
        C[key, key] = float(C0)/label_proportions[key]

    # More labeled examples than hidden neurons
    if nh <= nlab:
        eye = np.eye(nh)
        inv_arg = eye + (H.T @ C @ H) + lam*(H.T @ L @ H)
        inv = np.linalg.inv(inv_arg)

        beta = (inv @ H.T @ C @ Y)
    # Less labeled examples than hidden neurons (apparently the more common case)
    else:
        eye = np.eye(L.shape[0])
        inv_arg = eye + (C @ H @ H.T) + lam*(L @ H @ H.T)
        inv = np.linalg.inv(inv_arg)

        beta = (H.T @ inv @ C @ Y)
    return beta

def eval_h(X, hlayer_w):
    hidden = (X @ hlayer_w)
    sig = logistic.cdf(hidden)
    return sig

def evaluate_model(X, hlayer_w, beta):
    H = eval_h(X, hlayer_w)
    result = (H @ beta)
    return result

def __IDX2LAB(idx, map):
    return map[idx]
IDX2LAB = np.vectorize(__IDX2LAB, excluded=['map'])

def get_right_wrong_count(predicted, target, index_to_label_map):
    """returns the number of correct and incorrect classifications as
        a tuple (num_correct, num_incorrect)
    """
    predicted_values = np.argmax(predicted, axis=1)
    assert predicted_values.shape == target.shape

    predicted_labels = IDX2LAB(predicted_values, index_to_label_map)
    assert predicted_labels.shape == target.shape

    correct   = np.count_nonzero(predicted_labels == target)
    incorrect = np.count_nonzero(predicted_labels != target)
    assert correct + incorrect == target.size

    return correct,incorrect

def create_onehot(labels):
    """Given an (n,1) matrix of labels, create an (n,k) one-hot matrix
       with ones at the indices of the label and zeros everywhere else

       The labels might not neatly correspond to indices, so return a
       dictionary mapping {index:label} and {label:index} as well.
    """
    unique_labels = set(x[0] for x in labels)
    ordered_labels = sorted(list(unique_labels))

    # map each unique label to an index from 0 to num_uniq
    label_to_index_map = {lab:i for i,lab in enumerate(ordered_labels)}

    mold = np.repeat(np.zeros_like(labels), len(label_to_index_map), axis=1)

    # for each row in the heatmap, find out which index to set to 1 by
    # looking up which index corresponds to the correct label for that row
    indices = [label_to_index_map[lab[0]] for lab in labels]
    # then set the correct index of each such row to 1
    mold[np.arange(mold.shape[0]), indices] = 1

    # create the reverse mapping so that the index with the highest predicted
    # value can be looked up to get the predicted label
    index_to_label_map = {label_to_index_map[lab]:lab for lab in label_to_index_map}

    # check that the labels passed in have been represented in the mold (one-hot map)
    for label,row in zip(labels, mold):
        # each row has exactly one correct target value
        assert np.count_nonzero(row) == 1
        # the label when mapped to an index gives the index of the 1
        assert np.argmax(row) == label_to_index_map[label[0]]

    return mold, index_to_label_map, label_to_index_map

def run_SS(labeled, unlabeled, validation, test, nh, NN, sigma):
    """Train and run the model given sets partitioned into:

        Labeled, Unlabeled, Validation, and Test
       As well as:
        the number of hidden neurons,
        numbe of nearest neighbours for the weight matrix,
        and an (unused) sigma value claimed to be a hyperparameter
    """
    training = np.vstack((labeled[0], unlabeled[0]))

    # create a one-hot matrix using target labels
    labeled_onehot, index_to_label_map, label_to_index_map = create_onehot(labeled[1])
    # the target one-hot matrix includes zeros in place of any unlabeled samples
    unlabeled_onehot = np.zeros(shape=(unlabeled[1].size, len(index_to_label_map)))

    target_one_hot = np.vstack((labeled_onehot, unlabeled_onehot))
    #print(target_one_hot[:10])
    #print(target_one_hot.shape)

    # number of labeled training samples for each label, used for weighting
    label_proportions = get_label_proportions(labeled[1], label_to_index_map)
    print("Label proportions:", label_proportions)


    # randomly generated hidden layer weights + biases
    ni = training.shape[1] # each X is a training pattern of length ni
    hlayer_w = gen_inlayer(ni, nh)
    H = eval_h(training, hlayer_w)

    # Graph laplacian from labeled and unlabeled data
    LAP = laplacian(training, NN, sigma)

    # determine parameters C0 and lambda using validation set
    best_C0 = 10.0**(-6.0)
    best_lam = 10.0**(-6.0)
    best_accuracy = -1.0
    for i in range(-6, 6+1):
        C0 = 10.0**i
        for j in range(-6, 6+1):
            lam = 10.0**j
            beta = gen_beta(H=H,
                            L=LAP,
                            C0=C0,
                            lam=lam,
                            Y=target_one_hot,
                            nh=nh,
                            label_proportions=label_proportions)

            result = evaluate_model(validation[0], hlayer_w, beta)
            correct,wrong = get_right_wrong_count(result, validation[1], index_to_label_map)
            acc = float(correct)/(correct + wrong)
            if acc > best_accuracy:
                best_C0 = C0
                best_lam = lam
                best_accuracy = acc

    print("Selected C0: {}\nSelectec lam: {}".format(best_C0, best_lam))
    # evaluate performance on test set, using the best-performing values of
    # the parameters C0 and lambda (on the validation set), found above.
    beta = gen_beta(H=H,
                    L=LAP,
                    C0=best_C0,
                    lam=best_lam,
                    Y=target_one_hot,
                    nh=nh,
                    label_proportions=label_proportions)

    result = evaluate_model(test[0], hlayer_w, beta)
    correct,wrong = get_right_wrong_count(result, test[1], index_to_label_map)
    acc = float(correct)/(correct + wrong)
    print("Percentage of correct testset classifications: {}\n".format(acc))
    # predicted, target, number_correct, number_wrong
    return result, test[1], correct, wrong


