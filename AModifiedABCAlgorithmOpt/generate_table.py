import numpy as np
import sys
import json
from collections import OrderedDict

PADSYMB = ' '*8

def assertation(lines0):
  run,components,paramdict = json.loads(lines0)
  assert len(run) == paramdict['REPRO_number_of_independent_runs']

def print_table(consts, functions):
  result = ''
  result += 'Results marked with a trailing * have a difference in errors of\n' \
            'less than 10^(-7), which the paper considers insignificant.\n'
  result += 'In the case where the printed values are followed by bracketed\n' \
            'values, the bracketed values are the values from the paper.\n' \
            ' (their display is toggled via function param)\n\n'
  result += 'Params shared across all runs:\n'
  result += repr(consts) + '\n'

  runs = OrderedDict()
  function_numbers = {func:i for i,func in enumerate(functions)}

  longests = [len(func) for func in functions]
  longest_param = 0
  for func in functions:
    function_number = function_numbers[func]
    for p,s in functions[func]:
      if p not in runs:
        runs[p] = ['' for x in functions]
        runs[p][function_number] = s
      else:
        assert runs[p][function_number] == ''
        runs[p][function_number] = s
      longests[function_number] = max(longests[function_number],  len(s))
      longest_param = max(longest_param, len(p))

  paddeds = [''.ljust(longest_param)] + [x.ljust(longests[i]) for i,x in enumerate(functions)]
  result += PADSYMB.join(paddeds) + '\n'
  for param in runs:
    paddeds = [param.ljust(longest_param)] + [x.ljust(longests[i]) for i,x in enumerate(runs[param])]
    s = PADSYMB.join(paddeds)
    result += s + '\n'
  print(result)

def gen_table(runfile, include_paper=True):
  functions = OrderedDict()
  if include_paper:
    result_format = "{repr_mean:1.2E} ± {repr_std:1.2E} [{paper_mean:1.2E} ± {paper_std:1.2E}]{s}"
  else:
    result_format = "{repr_mean:1.2E} ± {repr_std:1.2E}{s}"
  consts = {}
  const_names = ['SN', 'MFE', 'PAPER_number_of_independent_runs',
                 'REPRO_number_of_independent_runs', 'dim']
  var_names = ['SF', 'MR', 'limit']
  with open(runfile) as f:
    lines = [x.strip() for x in f.readlines()]

  for line in lines:
    assertation(line)
    runs,components,paramdict = json.loads(line)
    func = paramdict['func']

    paper_mean = paramdict['PAPER_mean_error']
    paper_std = paramdict['PAPER_std_dev']
    this_mean = np.mean(runs)
    this_std = np.std(runs)

    if abs(paper_mean - this_mean) < 10**(-7):
        lowlim = "*"
    else:
        lowlim = ""
    if include_paper:
      s = result_format.format(s=lowlim,
                               repr_mean=this_mean,
                               repr_std=this_std,
                               paper_mean=paper_mean,
                               paper_std=paper_std)
    else:
      s = result_format.format(s=lowlim,
                               repr_mean=this_mean,
                               repr_std=this_std)

    p = ', '.join('{}: {}'.format(key,paramdict[key]) for key in sorted(var_names))
    if func in functions:
      functions[func].append((p,s))
    else:
      functions[func] = [(p,s)]
    for c in const_names:
      if c not in consts:
        consts[c] = paramdict[c]
      else:
        assert consts[c] == paramdict[c]

  print_table(consts, functions)

if __name__ == '__main__':
  if len(sys.argv) == 2:
    runfile = sys.argv[1]
    opt = "include"
  else:
    print("Usage:")
    print("  Generate a table similar to in the paper, given a runfile:")
    print("    python3 generate_table.py dumps/runfile_produced_by_main_invocation.run")
    exit()

  print("Generating a table like in paper from a runfile, including paper values:".format(opt))
  print("File: {}\n".format(runfile))
  gen_table(runfile, True)
  print("\n_____\nGenerating a table like in paper from a runfile, excluding paper values:".format(opt))
  print("File: {}\n".format(runfile))
  gen_table(runfile, False)
