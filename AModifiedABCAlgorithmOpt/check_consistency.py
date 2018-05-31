import numpy as np
import sys
import json
from collections import OrderedDict
import parse_tables

PADSYMB = ' '*8

def assertation(lines0):
  run,components,paramdict = json.loads(lines0)
  assert len(run) == paramdict['REPRO_number_of_independent_runs']

def gen_consistency(runfile, other_results):
  def cmp(query, other):
    if query < other:
      return -1
    elif query == other:
      return 0
    else:
      return 1

  funcmap = {}
  # although the funcmap above still needs to be constructed below even if
  # printing the table values is not necessary.
  print("Below are the means and standard deviations of the alternative")
  print("9 methods from tables 2 and 3 (e.g PSO), in the order they appear,")
  print("for each function (shown here purely for reference):")
  for __results,__func in other_results:
    name = __func.__name__
    funcmap[name] = __results
    print("{} (PSO+OTHER VARIANTS):".format(name))
    tab = ["{:1.2E} ± {:1.2E}".format(m,s) for m,s in __results]
    print("\n".join(tab))
    print("")

  with open(runfile) as f:
    lines = [x.strip() for x in f.readlines()]

  function_results = {}
  for line in lines:
    assertation(line)
    runs,components,paramdict = json.loads(line)
    # the function that the reproduction runs line (parameter configuration) used
    func = paramdict['func']
    assert func in funcmap
    if func not in function_results:
      function_results[func] = ([],[])

    paper_mean = paramdict['PAPER_mean_error']
    paper_std = paramdict['PAPER_std_dev']
    this_mean = np.mean(runs)
    this_std = np.std(runs)

    # for each parameter configuration, separately compute the CMP between means:
    #   (paper_result, pso_variant_1), (paper_result, pso_variant_2), ...
    # and also separately computer the CMP between
    #   (repr_result, pso_variant_1), (repr_result, pso_variant_2), ...
    # Consistency is then defined as whether the paper and the reproduction has
    # the same CMP with respect to the PSO variants
    # (CMP is simply -1 if LT, 0 if EQ, and 1 if GT)
    FEATURE_VEC_PAPER = []
    FEATURE_VEC_THIS = []
    for other_mean, other_std in funcmap[func]:
      FEATURE_VEC_PAPER.append(cmp(paper_mean, other_mean))
      FEATURE_VEC_THIS.append(cmp(this_mean, other_mean))

    similarity = [x==y for x,y in zip(FEATURE_VEC_PAPER, FEATURE_VEC_THIS)]
    all_true = all(similarity)
    degree = sum(similarity)/float(len(similarity))
    function_results[func][0].append(all_true)
    function_results[func][1].append(degree)

  print("=== CONSISTENCY RESULTS BETWEEN PAPER AND REPRODUCTION ===")
  for __res,__func in other_results:
    name = __func.__name__
    all_trues, degrees = function_results[name]
    print("{}: ".format(name))
    print(("  All: {:>5}\n" +
           "  deg: {:4.2f}").format(str(all(all_trues)),
                                          sum(degrees)/float(len(degrees))))
    print("")

if __name__ == '__main__':
  if len(sys.argv) == 2:
    runfile = sys.argv[1]
    other_results = parse_tables.experiment_1_tables_2_3_CONSISTENCY()
    opt = "include"
  else:
    print("Usage:")
    print("  Given a .run-file of results, check consistency between the")
    print("  paper results, the .run-file results, and the other method results (e.g PSO)")
    print("    python3 check_consistency.py dumps/runfile_produced_by_main_invocation.run")
    exit()

  print("Finding consistency of runfile:")
  print("File: {}\n".format(runfile))
  gen_consistency(runfile, other_results)
