from scipy import stats
import numpy as np
import math
import sys
import json
from collections import OrderedDict
import time
import os

def assertation(lines0):
  run,components,paramdict = json.loads(lines0)
  assert len(run) == paramdict['REPRO_number_of_independent_runs']

def find_t(X1, X2, S1, S2, N1, N2):
  """X1 and X2 are means, S1 and S2 std devs, N1 and N2 are
     population sizes (and not degrees of freedom)
  """
  #with this, the result between scipy and manual is the same
  N1 = N1 - 1
  N2 = N2 - 1
  above = (X1 - X2)
  below = math.sqrt(  ((S1**2)/N1)  +  ((S2**2)/N2)  )
  return above/below

def find_v(S1, S2, N1, N2):
    vx1 = N1-1
    vx2 = N2-1
    above = (  ((S1**2)/N1)  +  ((S2**2)/N2)  )**2
    below = (S1**4)/((N1**2)*vx1)  +  (S2**4)/((N2**2)*vx2)
    return above/below

def scipy_t_test(X1, X2):
    """X1 and X2 are arrays of samples
       returns t,p
    """
    return stats.ttest_ind(X1, X2, equal_var=False)

def manual_t_test(paper_mean, this_mean, paper_std, this_std, paper_runs, this_runs, cmp_dataset_name="expected"):
    """prints stats and returns t,v,p
       The parameter cmp_dataset_name has no effect except label the expected result in the printed output
    """
    print("[manual ttest]")
    error_diff = abs(paper_mean - this_mean)
    insig = False
    if error_diff < 10**(-7): # or this_mean < 10**(-7):
        insig = True
        pprint = lambda s: print("*{:^72}*".format(s))
        print("*"*(72+2))
        pprint("Difference of error rates < 10^(-7)")
        pprint("the paper treats this as insignificant")
        pprint("(error difference was: {:1.2E})".format(error_diff))
        print("*"*(72+2))

    try:
        t = find_t(X1=paper_mean, X2=this_mean, S1=paper_std, S2=this_std, N1=paper_runs, N2=this_runs)
        v = find_v(S1=paper_std, S2=this_std, N1=paper_runs, N2=this_runs)
        p_value = stats.t.sf(np.abs(t), v)*2 #survival function
    except ZeroDivisionError:
        print("  ZeroDivisionError (paper: {}±{})".format(paper_mean, paper_std))
        print("")
        return -1, -1, -1
    else:
        print("  {tmean:1.4G} ± {tstd:1.4G}    [{pmean:1.4G} ± {pstd:1.4G} <-- {cmp_set}]".format(
                tmean=this_mean,
                tstd=this_std,
                pmean=paper_mean,
                pstd=paper_std,
                cmp_set=cmp_dataset_name))
        print("  t: {t:3.4f}  v: {v:3.4f}".format(t=t,v=v))
        print("  p-value: {p:1.4G}".format(p=p_value))
        print("")
        return t,v,p_value,insig


def write_file_jsonlines(L):
  s = '\n'.join(L)
  filename = str(time.time()).split('.')[0] + '.json_lines'

  path = os.path.join('RESULTS', 'output_json_list', filename)
  if os.path.exists(path):
    print("Filepath '{}' already exists, not overwriting; printing instead:".format(path))
    print(s)
  else:
    print("Writing final jsonlines-output to '{}'".format(path))
    with open(path,'w') as f:
      f.write(s)

def compare_with_paper(runfile):
  with open(runfile) as f:
    lines = [x.strip() for x in f.readlines()]

  json_lines_output = []

  for line in lines:
    assertation(line)
    runs,components,paramdict = json.loads(line)

    paper_mean = paramdict['PAPER_mean_error']
    paper_std = paramdict['PAPER_std_dev']
    this_mean = np.mean(runs)
    this_std = np.std(runs)

    paper_runs = paramdict['PAPER_number_of_independent_runs']
    this_runs = paramdict['REPRO_number_of_independent_runs']

    t,v,p,insig = manual_t_test(paper_mean=paper_mean,
                                paper_std=paper_std,
                                paper_runs=paper_runs,
                                this_mean=this_mean,
                                this_std=this_std,
                                this_runs=this_runs,
                                cmp_dataset_name="paper_results")
    print('\n')

    #dump the results to one final file
    newdict = OrderedDict()
    newdict['stat_runs'] = runs
    newdict['stat_components'] = components
    newdict['stat_t'] = t
    newdict['stat_v'] = v
    newdict['stat_p'] = p
    newdict['stat_insignificant_error_diff'] = insig
    newdict['REPRO_mean_error'] = this_mean
    newdict['REPRO_std_dev'] = this_std
    for key in sorted(paramdict):
      newdict[key] = paramdict[key]
    json_lines_output.append(json.dumps(newdict))
  write_file_jsonlines(json_lines_output)

def compare_two_runs(runfile1, runfile2):
  with open(runfile1) as f:
    lines1 = [x.strip() for x in f.readlines()]
  with open(runfile2) as f:
    lines2 = [x.strip() for x in f.readlines()]

  for line1,line2 in zip(lines1,lines2):
    assertation(line1)
    assertation(line2)
    run1,components1,paramdict1 = json.loads(line1)
    run2,components2,paramdict2 = json.loads(line2)

    print('Params1:', paramdict1)
    if paramdict2 != paramdict1:
      print('Params2:', paramdict2)
    else:
      print('Params2: <same as above>')

    t,p = scipy_t_test(run1, run2)
    print("[scipy ttest]\n  t: {t:3.4f}    p: {p:1.4G}".format(t=t,p=p))

    # treat run1 as the paper and run2 as the reproduction attempt
    # this is to investigate the implementation of the t-test and how
    # it performs on two populations generated the same way
    manual_t_test(paper_mean=np.mean(run1),
                  this_mean=np.mean(run2),
                  paper_std=np.std(run1),
                  this_std=np.std(run2),
                  paper_runs=len(run1),
                  this_runs=len(run2),
                  cmp_dataset_name=runfile1)

    print('\n\n\n')

if __name__ == '__main__':
  if len(sys.argv) == 2:
    runfile = sys.argv[1]
    print("Comparing a run to the results from the paper")
    print("File: {}\n".format(runfile))
    compare_with_paper(runfile)

  elif len(sys.argv) == 3:
    runfile1, runfile2 = sys.argv[1], sys.argv[2]
    print("Comparing two runs made using the same implementation")
    print("Files: {}  {}\n".format(runfile1, runfile2))
    compare_two_runs(runfile1, runfile2)
  else:
    print("Usage:")
    print("  Compare own run to paper results (and also write a final result-file):")
    print("    python3 t_test.py dumps/runfile_produced_by_main_invocation.run")
    print("")
    print("  Compare two own runs:")
    print("    python3 t_test.py dumps/runfile1_produced_by_1st_main_invocation.run dumps/runfile2_produced_by_2nd_main_invocation.run")
