# -*- coding: utf-8 -*-
import bee
import parse_tables

import numpy as np
import multiprocessing
import time
import copy
import os
import sys
import json
import random

def run(pool, r, run_file, REPRO_number_of_runs=None, counter=0):
    """number of runs is the runs to actually do; the number of runs used in
       the paper are included in the params line of the dump file
       If not provided, run for the same number of runs as the paper.
    """
    __paramdict = r.params_to_dict()
    paramdict = copy.deepcopy(__paramdict)
    paramdict['func'] = paramdict['func'].__name__


    # this might be different from the number of runs per func in the paper,
    # depending on whether the user supplied a different number
    if REPRO_number_of_runs is None:
        REPRO_number_of_runs = paramdict['PAPER_number_of_independent_runs']
    paramdict['REPRO_number_of_independent_runs'] = REPRO_number_of_runs
    print(paramdict)

    # [ (bee_instance, seed_offset), ...]
    swarms = []
    for i in range(REPRO_number_of_runs):
        b = bee.Bee(MCN   = None,
                    MFE   = paramdict['MFE'],
                    SN    = paramdict['SN'],
                    MR    = paramdict['MR'],
                    SF    = paramdict['SF'],
                    limit = paramdict['limit'],
                    dim   = paramdict['dim'],
                    func = r.func) #the paramdict dumps just the name of the func, for reference
        # i is used as a seed offset
        swarms.append((b,i+counter))
    if USE_MULTIPROCESSING:
        runs = list(pool.map(bee.run_helper, swarms))
    else:
        runs = list(map(bee.run_helper, swarms))

    for run,components in runs:
      assert abs(run - r.func(components)) <=  0.00000001

    # contains the mean errors produced by the REPRO_number_of_runs function optimization
    # also has the paramdict with params used for the run
    # (params are shared among each REPRO_number_of_runs on a single line)
    funcvals, all_components = zip(*runs)
    all_components = [list(x) for x in all_components]
    with open(run_file, 'a') as f:
        obj = json.dumps([funcvals, all_components, paramdict])
        f.write(obj + '\n')

    #print(funcvals)
    print(u"repro_mean: {m:1.2E} ± {s:1.2E}  [paper_mean: {me:1.2E} ± {se:1.2E}]".format(
            m=np.mean(funcvals),
            s=np.std(funcvals),
            me=paramdict['PAPER_mean_error'],
            se=paramdict['PAPER_std_dev']))
    print('\n')

def experiment1(pool, REPRO_number_of_runs=None):
    """The optional parameter REPRO_number_of_runs enables running each function a
       different number of times than the (e.g 30) from the paper
    """
    function_runs = parse_tables.experiment_1_tables_2_3()
    timestamp = time.time()
    uniq_filename = "{}.run".format(timestamp)
    run_file = os.path.join("RESULTS", "dumps", uniq_filename)
    print("Dumping output to {}\n".format(run_file))
    counter = 0
    for i,function_run in enumerate(function_runs, start=1):
        for j,param_run in enumerate(function_run, start=1):
            print("func {}/{} ({}) -- param {}/{}".format(i, len(function_runs),
                                                          param_run.func.__name__,
                                                          j, len(function_run)))
            run(pool, param_run, run_file, REPRO_number_of_runs, counter)
            #make the seed of each param run different
            counter += len(function_runs)*len(function_run)


# change this to False to force singleprocessor-mode. The setting of random
# seeds should cause repeated main.py invocations to give the same sequences,
# of course with the possibility that the (e.g) 30 invocations for one set of
# parameters might be made in a different order, so the resulting list might be
# shuffled.
# In case of issues with this, or to be certain, setting this to False might help
# although the program will very likely be slower if the system has multiple processors.
USE_MULTIPROCESSING = True
if __name__ == '__main__':
    random.seed(64)
    np.random.seed(64)
    try:
        os.nice(10)
    except AttributeError:
        print("OS does not support setting process niceness")
        pass

    processor_count = multiprocessing.cpu_count()
    if USE_MULTIPROCESSING:
        print("Using {} processors".format(processor_count))
        pool = multiprocessing.Pool(processor_count)
    else:
        print("Using single-processor mode")
        pool = None

    if len(sys.argv) > 1:
        experiment1(pool, int(sys.argv[1]))
    else:
        experiment1(pool)
