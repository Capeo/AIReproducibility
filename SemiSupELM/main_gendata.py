import os
import time
import random
import numpy as np

import datasets

# CHANGE THESE PATHS TO PATHS OF THE .mat DATASETS DESCRIBED IN THE PAPER
mat_path_coil20 = os.path.expanduser("~/Documents/datasets/elm/coil20.mat")
mat_path_g50c = os.path.expanduser("~/Documents/datasets/elm/g50c.mat")
mat_path_uspst = os.path.expanduser("~/Documents/datasets/elm/uspst.mat")

# SET UNDESIRED DATASETS TO FALSE
# e.g to not generate a json file for them
do_coil20 = True
do_coil20b = True
do_g50c = True
do_uspst = True
do_uspstb = True

# place to store generated indices (folds)
#  support for changing this might be flaky, so it is best to leave it as is.
json_output_directory = os.path.expanduser("./idx_datasets/")

def gen():
    seed = 32
    random.seed(seed)
    np.random.seed(seed)

    print("Generating k-fold partitions")

    t = str(time.time()).split('.')[0]
    unique_subdir = os.path.join(json_output_directory, t)
    os.mkdir(unique_subdir)
    print("Storing json files in directory {}".format(unique_subdir))

    # coil20
    if do_coil20:
        d = datasets.gen_partitions(mat_path_coil20, size=1440, L=40, U=1000, V=40, T=360)
        finalpath = os.path.join(unique_subdir, "coil20.json")
        datasets.dump_json(d, finalpath)

    # coil20b, strictly speaking generated the same way as coil20
    # (the binarization is done when the coil20 set is loaded for use with
    #  the model, as the indices are the same with just the classes changed
    #  to [1,2] -- but using a different shuffle seemed appropriate)
    if do_coil20b:
        d = datasets.gen_partitions(mat_path_coil20, size=1440, L=40, U=1000, V=40, T=360)
        finalpath = os.path.join(unique_subdir, "coil20b.json")
        datasets.dump_json(d, finalpath)

    # G50C
    if do_g50c:
        d = datasets.gen_partitions(mat_path_g50c, size=550, L=50, U=314, V=50, T=136)
        finalpath = os.path.join(unique_subdir, "g50c.json")
        datasets.dump_json(d, finalpath)

    # USPST
    if do_uspst:
        d = datasets.gen_partitions(mat_path_uspst, size=2007, L=50, U=1409, V=50, T=498)
        finalpath = os.path.join(unique_subdir, "uspst.json")
        datasets.dump_json(d, finalpath)

    # USPST(B)
    if do_uspstb:
        d = datasets.gen_partitions(mat_path_uspst, size=2007, L=50, U=1409, V=50, T=498)
        finalpath = os.path.join(unique_subdir, "uspstb.json")
        datasets.dump_json(d, finalpath)


if __name__ == '__main__':
    gen()