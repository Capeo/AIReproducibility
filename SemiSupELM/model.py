from scipy.stats import logistic
from sklearn.neighbors import NearestNeighbors
import numpy as np
import os
import math
import time

def mmatmul(*args):
    """Matrix multiplication with several arguments, should be associative
       save for floating point inaccuracies between different evaluation
       orders.
       Purely to make the code more readable, I could not find numpy support
       for several arguments to one call.
       AxBxCxD -> [A,B,C,D]
        result = (Ax(Bx(CxD)))
    """
    args = list(args)
    result = args.pop()
    while args:
        arg = args.pop()
        result = np.matmul(arg,result)
    return result

def gen_inlayer(ni, nh):
    """Returns a matrix niXnh that represents the mapping
       from ni to nh, obtained via matrix multiplication via an input

       H = X*W
     Nxnh = Nxni X nixnh
    """
    W = np.random.uniform(low=-1.0, high=1.0, size=(ni, nh))
    W = W.astype(np.float64)
    return W

def get_label_proportions(labeled):
    """Number of samples per class label"""
    proportions = {}
    for pattern,label in zip(*labeled):
        assert label.size == 1
        label = label[0]
        if label not in proportions:
            proportions[label] = 0
        proportions[label] += 1
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
                          n_jobs= 1) # setting jobs higher might be faster,
                                     # though it might also cause isses with
                                     # determinism?
    NN.fit(features)
    #result = NN.kneighbors_graph(mode='connectivity')
    result = NN.kneighbors_graph(mode='distance')
    actual_sigma = result[result != 0].std()
    result[result != 0] = func(result[result != 0], actual_sigma)
    #result[result != 0] = func(result[result != 0], param_sigma) # results are poor with this (param)
    return result

def diagonals(W):
    """Calculate D^(-1/2) here because 0 to negative powers in the actual
       diagonal matrix is undefined"""
    components = np.sum(W,axis=1)
    DPM = np.power(components, -0.5)
    DPP = np.power(components,  0.5)

    D = np.diagflat(components)
    DPM = np.diagflat(DPM)
    DPP = np.diagflat(DPP)
    return D,DPM,DPP

def laplacian(features, n_neighbours, sigma):
    """Calculate the graph laplacian

       The paper mentions that [52] discusses a method of rather than using
        L directly, using L^p or D^(-1/2)LD^(1/2) to normalize.
       The cited paper unfortunately is just as vague in its description of this,
        mentioning no method of selecting the integer p. [TODO]
       I can only assume that D here only raises the values on the diagonal to
        the specified power, as values elsewhere will be zero which can not be
        raised to the negative power.
    """
    W = adjacency(features, n_neighbours, sigma)
    D,DPM,DPP = diagonals(W)
    L = D - W
    DLD = mmatmul(DPM, L, DPP)
    return DLD

def gen_beta(H, L, C0, lam, Y, nh, label_proportions):
    """Generates the beta matrix used in the output layer
       Worth to note is that the paper mentions in the ELM-section that
        beta can be obtained in a more stable manner rather than inverting
        explicitly, thogh this is never mentioned again, or the method
        described in detail. 
       Instead, this section uses numpys method for inverting a matric. TODO?
    """
    # number of samples per class label
    nlab = sum((label_proportions.get(key) for key in label_proportions))
    C = np.zeros_like(L)
    for key in label_proportions:
        # labels start at 1
        C[key-1, key-1] = float(C0)/label_proportions[key]

    HT = np.transpose(H)
    # More labeled examples than hidden neurons
    if nh <= nlab:
        eye = np.eye(nh)
        inv_arg = eye + mmatmul(HT, C, H) + lam*mmatmul(HT, L, H)
        inv = np.linalg.inv(inv_arg)

        beta = mmatmul(inv, HT, C, Y)
    # Less labeled examples than hidden neurons (apparently the more common case)
    else:
        eye = np.eye(L.shape[0], dtype=L.dtype)
        inv_arg = eye + mmatmul(C, H, HT) + lam*mmatmul(L, H, HT)
        inv = np.linalg.inv(inv_arg)

        beta = mmatmul(HT, inv, C, Y)
    return beta

def eval_h(X, hlayer_w):
    hidden = mmatmul(X, hlayer_w)
    sig = logistic.cdf(hidden)
    return sig

def evaluate_model(X, hlayer_w, beta):
    H = eval_h(X, hlayer_w)
    result = mmatmul(H, beta)
    # Use closest integer as the predicted class
    #  Perhaps this is not a fair assumption ? [TODO]
    return np.rint(result).astype(np.int64)

def calculate_accuracy(predicted, target):
    correct = np.count_nonzero(predicted == target)
    #print("{:8.4f}, {:}/{:}".format( float(correct)/target.size, correct, target.size))

    return float(correct)/target.size

def get_right_wrong_count(predicted, target):
    correct = np.count_nonzero(predicted == target)
    wrong = np.count_nonzero(predicted != target)
    return correct,wrong

def run_SS(labeled, unlabeled, validation, test, nh, NN, sigma):
    """Train and run the model given sets partitioned into:

        Labeled, Unlabeled, Validation, and Test
       As well as:
        the number of hidden neurons,
        numbe of nearest neighbours for the weight matrix,
        and an (unused) sigma value claimed to be a hyperparameter
    """
    # number of labeled training samples for each label, used for weighting
    label_proportions = get_label_proportions(labeled)

    training = np.vstack((labeled[0], unlabeled[0]))
    # set the labeled portion of target to the label values, and the remainder
    # (i.e the unlabeled portion) to 0 (using the shape of the unlabeled sets
    #  unused labels as a mold).                     v only used to get the right shape
    target = np.vstack(  (labeled[1], np.zeros_like(unlabeled[1]))  )

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
            beta = gen_beta(H, LAP, C0, lam, target, nh, label_proportions)
            result = evaluate_model(validation[0], hlayer_w, beta)
            acc = calculate_accuracy(result, validation[1])
            if acc > best_accuracy:
                best_C0 = C0
                best_lam = lam
                best_accuracy = acc

    print("Selected C0: {}\nSelectec lam: {}".format(best_C0, best_lam))
    # evaluate performance on test set, using the best-performing values of
    # the parameters C0 and lambda (on the validation set), found above.
    beta = gen_beta(H, LAP, best_C0, best_lam, target, nh, label_proportions)
    result = evaluate_model(test[0], hlayer_w, beta)
    acc = calculate_accuracy(result, test[1])
    correct,wrong = get_right_wrong_count(result, test[1])
    print("Percentage of correct testset classifications: {}\n".format(acc))
    # predicted, target, number_correct, number_wrong
    return result, test[1], correct, wrong


