from sklearn.utils import shuffle as sklearn_shuffle
from scipy import io as sio
import numpy as np
import json
import os
import time


def load_dataset(path, add_biases=True, binarize=False):
    """Load a dataset used in the experiment, adding biases to
       the features for mathematical convenience, and binarizing
       the set by grouping the first N//2 class labels together if appropriate.

       Only pass binarize=True if the class labels in the dataset are
       appropriate (e.g 1-20). [TODO]
    """
    dataset = sio.loadmat(path)

    #add dummy values to represent biases
    # shape = (num_inputs, num_features)
    if add_biases:
        new_X = np.insert(dataset['X'], obj=0, values=1, axis=1)
        dataset['X'] = new_X

    # does not work in general, but works for the datasets uspstb and coil20b
    # where labels go from 0 to 9 and 1 to 20 respectively
    if binarize:
        classes = []
        for y in dataset['y']:
            if y not in classes:
                classes.append(y)
        num_classes = len(classes)

        # all labels up to and including this belong to the first class
        # (the rest of the labels belong to the second class)
        # (class 1 is x <= 4 for uspstb  and  x <= 10 coil20b)
        first_class = max(num_classes//2,  1)

        new_y = np.where(dataset['y'] <= first_class, 1, 2)
        dataset['y'] = new_y

    return dataset

def create_results_path(experiment_name):
    t = str(time.time()).split('.')[0]
    name = experiment_name + '_' + t
    return os.path.join('results', name)

def save_summary(right_count, wrong_count, path):
    accuracy = float(right_count)/(right_count + wrong_count)
    error_rate = 1.0 - accuracy
    s = '''right: {}\nwrong: {}\naccuracy: {}\nerror_rate: {}\n'''.format(right_count,
                                                                          wrong_count,
                                                                          accuracy,
                                                                          error_rate)
    with open(path, 'w') as f:
        f.write(s)
    return s

def results_to_csv(results, outpath):
    """stacks the matrices in results vertically
       each matrix in results is a set of rows (index,prediction,target,foldnumber)
        where the rows are the result of one invocation of the algorithm.
      e.g with the 12 folds results contains a matrix for each fold with the
       classification results of the algorithm, and this function stacks them into
       one final result with all the classifications.
      Then save the result as a csv, the final full result of the reproduction attempt
    """
    separator = ";"
    mx = np.vstack(results)
    np.savetxt(fname=outpath, X=mx, delimiter=separator, fmt="%d")

def dict_to_numpy(fold_dict, main_data):
    """Given a dict representing the indices from the dataset each set (LUVT)
       has, return numpy arrays containing the rows from the dataset for each
       such set.
    """
    LX = main_data['X'][fold_dict['L']]
    Ly = main_data['y'][fold_dict['L']]

    UX = main_data['X'][fold_dict['U']]
    Uy = main_data['y'][fold_dict['U']]

    VX = main_data['X'][fold_dict['V']]
    Vy = main_data['y'][fold_dict['V']]

    TX = main_data['X'][fold_dict['T']]
    Ty = main_data['y'][fold_dict['T']]

    return [(LX,Ly), (UX,Uy), (VX,Vy), (TX,Ty)]

def dump_json(obj, path):
    with open(path, 'w') as f:
        json.dump(obj, f, sort_keys=True)

def load_json(path):
    with open(path) as f:
        obj = json.load(f)
    return obj

def _create_folds(array, k, size):
    """split array into k chunks of approx size=size"""
    folds = []
    current = 0
    for i in range(k-1):
        folds.append(array[current:current + size])
        current = current + size
    folds.append(array[current:])
    return folds

#shuffled_X, shuffled_y = sklearn_shuffle(dataset['X'], dataset['y'])
def generate_folds_SS(dataset, size, L, U, V, T):
    """splits the dataset into 4 folds, each fold the size of T, possibly with
        the last fold being slightly smaller/larger than T. With the default values,
        there should be 4 folds).
       Then partition the remaining LUV-fold into sizes L, U, V in such a way
        that L and V contains at least one element from each class (that is
        present in the remaining three folds).
       Finally fill the folds with the rest of the datapoints randomly.
       Repeat 4 times, setting T to one fold and the three remaining sets to
       the three remaining folds in turn.
       This assumes that the sizes of L, U, V, T conform to the portions from
        the paper (i.e T=25%~, the sum of the rest being 75%~).
       Because the paper does not split LUVT cleanly into 25% chunks (only T),
        I can only assume that the methodology above is the intended one,
        with the three remaining LUV-folds being freely defined while the
        T-fold is the important one to alternate through.

      Returns a list of dicts, each dict having the classes and the indices
       from the dataset for each class: [{'L':[1,4,5], 'U':[2,3], ...}, ...]
       in the case of 4 folds, there are 4 dicts.
      """
    assert dataset['X'].shape[0] == size
    assert dataset['y'].shape[0] == size
    assert dataset['y'].shape[1] == 1
    assert L + U + V + T == size

    PARTITIONS = []

    indices = np.arange(size)
    np.random.shuffle(indices)
    folds = _create_folds(indices, 4, T)
    for i,fold in enumerate(folds):
        pool = np.hstack([F for j,F in enumerate(folds) if j != i])
        _test = list(fold)
        _labeled = []
        _validation = []
        _unlabeled = []

        used = set()
        # fill up labeled set with one element from each class
        present = []
        for idx in pool:
            if len(_labeled) == L:
                break
            if (dataset['y'][idx] not in present) and (idx not in used):
                _labeled.append(idx)
                present.append(dataset['y'][idx])
                used.add(idx)

        # fill up validation set with one element from each class
        present = []
        for idx in pool:
            if len(_validation) == V:
                break
            if (dataset['y'][idx] not in present) and (idx not in used):
                _validation.append(idx)
                present.append(dataset['y'][idx])
                used.add(idx)

        # remaining training samples
        remaining = [x for x in pool if x not in used]
        current = 0

        labeled_missing = L - len(_labeled)
        _labeled.extend(remaining[current:current + labeled_missing])
        current = current + labeled_missing

        validation_missing = V - len(_validation)
        _validation.extend(remaining[current:current + validation_missing])
        current = current + validation_missing

        _unlabeled.extend(remaining[current:])

        #ascertain that all labels are used and that no label is used twice
        S1,S2,S3,S4 = [set(S_) for S_ in [_labeled, _unlabeled, _validation, _test]]
        assert len(set.union(S1,S2,S3,S4)) == size
        for m,Sx in enumerate([S1,S2,S3,S4]):
          for n,Sy in enumerate([S1,S2,S3,S4]):
            if m == n:
              continue
            assert not set.intersection(Sx,Sy)
        # json does not like np.int64
        partition = {'L':[int(x) for x in _labeled],
                     'U':[int(x) for x in _unlabeled],
                     'V':[int(x) for x in _validation],
                     'T':[int(x) for x in _test]}
        PARTITIONS.append(partition)


    # ascertain that the test sets from the k folds are distinct
    # and that they together form the full dataset
    test_sets = [set(part['T']) for part in PARTITIONS]
    assert len(set.union(*test_sets)) == size
    for m,Sx in enumerate(test_sets):
      for n,Sy in enumerate(test_sets):
        if m == n:
          continue
        assert not set.intersection(Sx,Sy)

    return PARTITIONS


def gen_partitions(mat_path, size, L, U, V, T, repetitions=3):
    """Repeat each fold generation of the 4 test set folds 3 times, as
       mentioned in the paper. This results in a total of 4*3=12 folds,
       where each fold is a dictionary mapping
        {'L':[indices], 'U':[indices], 'V':[indices]', 'T':[indices],
       Where indices index into the dataset in question ( a .mat file,
        one feature per row of its ['X'] and ['y'] matrices), this feature
        being what the indices point to.
    """
    data = load_dataset(mat_path)
    PARTITIONS = []
    for k in range(repetitions):
        P = generate_folds_SS(data, size=size, L=L, U=U, V=V, T=T)
        PARTITIONS.extend(P)
    return PARTITIONS
