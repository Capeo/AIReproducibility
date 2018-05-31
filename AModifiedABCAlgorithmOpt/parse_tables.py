# -*- coding: utf-8 -*-
import functions
import re

# this file has the results from the first experiment of the actual paper hardcoded as
# strings, and parses it into a list of parameters + expected results that other modules
# (largely main.py, the experiment code) then in turn pass to e.g bee.py (the implemented method)

class Parameters(object):
    def __init__(self, dataline, MR, SF, limit, SN, dim, MFE, PAPER_number_of_independent_runs, func):
        self.MR = MR
        self.SF = SF
        self.limit = limit
        self.dim = dim
        self.MFE = MFE
        self.SN = SN

        self.PAPER_number_of_independent_runs = PAPER_number_of_independent_runs
        self.PAPER_mean_error = dataline[0]
        self.PAPER_std_dev = dataline[1]

        self.func = func

    def params_to_dict(self):
        return {key:self.__dict__[key] for key in ['MR', 'SF', 'limit', 'dim', 'MFE', 'SN',
                                          'PAPER_number_of_independent_runs', 'PAPER_mean_error', 'PAPER_std_dev',
                                          'func']}

def f(data, num_elements):
    def isnum(s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def fixed_E(s):
        return s=="0" or (("E+" in s or "E-" in s) and ("+-" not in s) and ("-+" not in s) and ("E0" not in s))

    data = data.strip()
    # the symbol ± surrounded by any number of spaces on both sides
    # and preceded/succeded by any number of nonspace/non± symbols (e.g E, numbers, period)
    patt = u'([^\s±]+)\s*±\s*([^\s±]+)'
    lines = [r for r in re.findall(patt, data)]
    assert len(lines) == num_elements

    #ascertain that the scientific notation has a + or - after E
    #(copying from paper is not perfect)
    assert all([(fixed_E(r1) and fixed_E(r2)) for r1,r2 in lines])
    assert all([(isnum(r1) and isnum(r2)) for r1,r2 in lines])
    numbers = [(float(r1), float(r2)) for r1,r2 in lines]
    return numbers

def f2(data, num_elements):
  """uppercase the e in the scientific notation as the other methods use lowercase"""
  newdata = data.replace('e', 'E')
  return f(newdata, num_elements)

# - - - - - - - - - -
def _format_data_1(lines, func):
    assert len(lines) == 18
    #Interpreting the intent to be 6 entries per parameter group;
    #the limit in table 3 is misaligned down one row (starting at 200 rather
    #than the 10 above). 

    #first part of column, top 6 entries, MR varies, SF=1, limit=200
    GROUP_A = [{'MR':0, 'SF':1, 'limit':200},
               {'MR':0.1, 'SF':1, 'limit':200},
               {'MR':0.3, 'SF':1, 'limit':200},
               {'MR':0.5, 'SF':1, 'limit':200},
               {'MR':0.7, 'SF':1, 'limit':200},
               {'MR':0.9, 'SF':1, 'limit':200}]

    #second part of column, middle 6 entries, SF varies, MR=0, limit=200
    GROUP_B = [{'MR':0, 'SF':1.0, 'limit':200},
               {'MR':0, 'SF':0.7, 'limit':200},
               {'MR':0, 'SF':0.5, 'limit':200},
               {'MR':0, 'SF':0.3, 'limit':200},
               {'MR':0, 'SF':0.1, 'limit':200},
               {'MR':0, 'SF':'ASF', 'limit':200}]

    #third part of column, last 6 entries, limit varies, MR=1, SF=1
    GROUP_C = [{'MR':1, 'SF':1, 'limit':10},
               {'MR':1, 'SF':1, 'limit':200},
               {'MR':1, 'SF':1, 'limit':500},
               {'MR':1, 'SF':1, 'limit':1000},
               {'MR':1, 'SF':1, 'limit':3000},
               {'MR':1, 'SF':1, 'limit':5000}]

    GROUPS = GROUP_A + GROUP_B + GROUP_C
    assert len(GROUPS) == 18

    zipped = list(zip(GROUPS,lines))
    assert len(zipped) == 18

    runs = []
    for PTT,dataline in zipped:
        params = Parameters(dataline = dataline,
                            SF = PTT['SF'],
                            MR = PTT['MR'],
                            limit = PTT['limit'],
                            dim = 10,
                            SN = 10, # as described in the paper section experiment
                            MFE = 30000,
                            PAPER_number_of_independent_runs=30,
                            func=func)
        runs.append(params)
    assert len(runs) == 18
    return runs

def experiment_1_tables_2_3():
  experiments = []

  um_1_sphere = f(u'''7.09E-017 ± 4.11E-017 1.00E-016 ± 4.88E-017 1.01E-016 ± 5.29E-017 9.63E-017 ± 5.01E-017 7.92E-017 ± 4.87E-017 7.04E-017 ± 4.55E-017 8.28E-017 ± 4.95E-017 1.05E-016 ± 5.26E-017 1.44E-016 ± 3.72E-017 1.77E-016 ± 5.48E-017 1.89E-010 ± 6.60E-010 3.00E-012 ± 5.48E-012 2.00E-001 ± 3.24E-001 9.68E-017 ± 5.08E-017 8.33E-017 ± 4.99E-017 9.04E-017 ± 4.81E-017 9.08E-017 ± 4.99E-017 1.21E-016 ± 6.66E-017''',
                  num_elements=18)
  experiments.append(  _format_data_1(lines=um_1_sphere, func=functions.Sphere)  )

  um_2_rosenbrock = f(u'''2.08E+000 ± 2.44E+000 1.96E+000 ± 2.22E+000 3.16E+000 ± 2.35E+000 3.20E+000 ± 1.81E+000 5.06E+000 ± 1.69E+000 3.66E+000 ± 1.97E+000 3.97E+000 ± 2.24E+000 2.77E+000 ± 2.26E+000 3.22E+000 ± 2.05E+000 3.79E+000 ± 1.99E+000 3.89E+000 ± 1.49E+000 4.42E-001 ± 8.67E-001 5.28E+000 ± 1.49E+000 1.61E+000 ± 1.93E+000 2.38E+000 ± 2.59E+000 2.15E+000 ± 2.46E+000 2.60E+000 ± 2.61E+000 2.08E+000 ± 2.54E+000''',
                     num_elements=18)
  experiments.append(  _format_data_1(lines=um_2_rosenbrock, func=functions.Rosenbrock)  )

  mm_3_ackley = f(u'''4.58E-016 ± 1.76E-016 3.79E-016 ± 9.68E-017 3.65E-016 ± 1.84E-016 3.32E-016 ± 1.84E-016 5.13E-016 ± 6.56E-016 4.21E-013 ± 2.04E-012 4.29E-010 ± 2.31E-009 3.41E-014 ± 1.12E-013 2.93E-008 ± 1.53E-007 4.59E-002 ± 2.10E-001 3.05E+000 ± 4.29E+000 2.70E-006 ± 1.46E-005 1.82E+000 ± 5.62E-001 4.03E-016 ± 1.25E-016 3.92E-016 ± 1.07E-016 4.39E-016 ± 2.22E-016 5.11E-016 ± 1.78E-016 5.87E-001 ± 1.36E+000''',
                  num_elements=18)
  experiments.append(  _format_data_1(lines=mm_3_ackley, func=functions.Ackley)  )

  mm_4_griewank = f(u'''1.57E-002 ± 9.06E-003 2.17E-002 ± 1.78E-002 1.93E-002 ± 1.30E-002 2.94E-002 ± 2.47E-002 4.00E-002 ± 3.52E-002 5.65E-002 ± 3.05E-002 5.61E-002 ± 3.26E-002 2.00E-002 ± 1.59E-002 3.87E-002 ± 2.64E-002 7.15E-002 ± 5.92E-002 6.81E-001 ± 8.39E-001 1.14E-001 ± 1.25E-001 4.25E-001 ± 1.43E-001 1.52E-002 ± 1.28E-002 2.10E-002 ± 1.32E-002 2.36E-002 ± 1.98E-002 2.50E-002 ± 1.46E-002 2.59E-002 ± 2.01E-002''',
                    num_elements=18)
  experiments.append(  _format_data_1(lines=mm_4_griewank, func=functions.Griewank)  )

  mm_5_weierstrass = f(u'''9.01E-006 ± 4.61E-005 1.15E-007 ± 6.17E-007 1.17E-005 ± 4.90E-005 8.80E-004 ± 2.94E-003 4.45E-004 ± 1.69E-003 1.34E-003 ± 5.62E-003 1.92E-003 ± 6.63E-003 1.18E-016 ± 6.38E-016 6.33E-001 ± 7.00E-001 2.89E+000 ± 1.26E+000 6.08E+000 ± 1.46E+000 3.24E-008 ± 3.06E-008 3.10E-001 ± 1.54E-001 9.41E-007 ± 5.07E-006 0.00E+000 ± 0.00E+000 1.88E-006 ± 1.01E-005 2.37E-016 ± 1.28E-015 1.15E-001 ± 3.79E-001''',
                       num_elements=18)
  experiments.append(  _format_data_1(lines=mm_5_weierstrass, func=functions.Weierstrass)  )

  mm_6_rastrigin = f(u'''1.61E-016 ± 5.20E-016 2.54E-013 ± 1.37E-012 9.61E-006 ± 5.17E-005 3.38E-001 ± 6.44E-001 7.31E-001 ± 7.23E-001 2.68E+000 ± 1.95E+000 3.71E+000 ± 1.58E+000 1.29E+000 ± 8.95E-001 1.73E+000 ± 1.18E+000 1.17E+001 ± 4.71E+000 3.94E+001 ± 1.41E+001 1.94E-001 ± 3.85E-001 6.97E+000 ± 1.69E+000 1.14E-007 ± 6.16E-007 3.33E-002 ± 1.79E-001 3.32E-002 ± 1.79E-001 6.63E-002 ± 2.48E-001 2.02E+000 ± 3.35E+000''',
                     num_elements=18)
  experiments.append(  _format_data_1(lines=mm_6_rastrigin, func=functions.Rastrigin)  )

  mm_7_ncrastrigin = f(u'''6.64E-017 ± 3.96E-017 1.58E-011 ± 7.62E-011 7.84E-002 ± 2.54E-001 8.00E-001 ± 7.02E-001 1.59E+000 ± 9.59E-001 4.21E+000 ± 1.37E+000 5.89E+000 ± 1.69E+000 9.00E-001 ± 7.00E-001 1.37E+000 ± 6.57E-001 3.17E+000 ± 1.42E+000 2.77E+001 ± 8.45E+000 6.80E-001 ± 7.80E-001 7.33E+000 ± 1.65E+000 1.12E-005 ± 6.04E-005 1.17E-006 ± 5.19E-006 7.22E-004 ± 3.89E-003 1.67E-001 ± 4.53E-001 1.17E+000 ± 3.01E+000''',
                       num_elements=18)
  experiments.append(  _format_data_1(lines=mm_7_ncrastrigin, func=functions.Noncontinuous_Rastrigin)  )

  mm_8_schwefel = f(u'''7.91E+000 ± 2.95E+001 3.96E+000 ± 2.13E+001 1.97E+001 ± 4.41E+001 2.25E+001 ± 4.45E+001 5.13E+001 ± 8.31E+001 1.78E+002 ± 1.25E+002 3.69E+002 ± 1.52E+002 3.20E+002 ± 1.36E+002 3.59E+002 ± 1.16E+002 9.49E+002 ± 2.19E+002 1.40E+003 ± 2.61E+002 1.09E+002 ± 8.49E+001 5.16E+002 ± 8.75E+001 1.65E+001 ± 4.01E+001 8.39E+000 ± 2.95E+001 1.30E+001 ± 3.55E+001 4.08E+001 ± 6.42E+001 1.53E+002 ± 1.20E+002''',
                    num_elements=18)
  experiments.append(  _format_data_1(lines=mm_8_schwefel, func=functions.Schwefel)  )

  return experiments

def experiment_1_tables_2_3_CONSISTENCY():
  """Retrieve the results of the other methods (e.g PSO) to check for consistency"""
  other = []
  um_1_sphere      = f2(u'''7.96e-051 ± 3.56e-050 9.84e-105 ± 4.21e-104 2.13e-035 ± 6.17e-035 1.37e-079 ± 5.60e-079 9.84e-118 ± 3.56e-117 2.21e-090 ± 9.88e-090 3.15e-030 ± 4.56e-030 4.98e-045 ± 1.00e-044 5.15e-029 ± 2.16e-028''',
                        num_elements=9)
  other.append( [um_1_sphere, functions.Sphere] )

  um_2_rosenbrock  = f2(u'''3.08e+000 ± 7.69e-001 6.98e-001 ± 1.46e+000 3.92e+000 ± 1.19e+000 8.60e-001 ± 1.56e+000 1.40e+000 ± 1.88e+000 8.67e-001 ± 1.63e+000 2.78e+000 ± 2.26e-001 1.53e+000 ± 1.70e+000 2.46e+000 ± 1.70e+000''',
                        num_elements=9)
  other.append( [um_2_rosenbrock, functions.Rosenbrock] )

  mm_3_ackley      = f2(u'''1.58e-014 ± 1.60e-014 9.18e-001 ± 1.01e+000 6.04e-015 ± 1.67e-015 5.78e-002 ± 2.58e-001 1.33e+000 ± 1.48e+000 3.18e-014 ± 6.40e-014 3.75e-015 ± 2.13e-014 1.49e-014 ± 6.97e-015 4.32e-10 ± 2.55e-014''',
                        num_elements=9)
  other.append( [mm_3_ackley, functions.Ackley] )

  mm_4_griewank    = f2(u'''9.69e-002 ± 5.01e-002 1.19e-001 ± 7.11e-002 7.80e-002 ± 3.79e-002 2.80e-002 ± 6.34e-002 1.04e-001 ± 7.10e-002 9.24e-002 ± 5.61e-002 1.31e-001 ± 9.32e-002 4.07e-002 ± 2.80e-002 4.56e-003 ± 4.81e-003''',
                        num_elements=9)
  other.append( [mm_4_griewank, functions.Griewank] )

  mm_5_weierstrass = f2(u'''2.28e-003 ± 7.04e-003 6.69e-001 ± 7.17e-001 1.41e-006 ± 6.31e-006 7.85e-002 ± 5.16e-002 1.14e+000 ± 1.17e+000 3.01e-003 ± 7.20e-003 2.02e-003 ± 6.40e-003 1.07e-015 ± 1.67e-015 0±0''',
                        num_elements=9)
  other.append( [mm_5_weierstrass, functions.Weierstrass] )

  mm_6_rastrigin   = f2(u'''5.82e+000 ± 2.96e+000 1.25e+001 ± 5.17e+000 3.88e+000 ± 2.30e+000 9.05e+000 ± 3.48e+000 1.17e+001 ± 6.11e+000 7.51e+000 ± 3.05e+000 2.12e+000 ± 1.33e+000 0±0 0±0''',
                        num_elements=9)
  other.append( [mm_6_rastrigin, functions.Rastrigin] )

  mm_7_ncrastrigin = f2(u'''4.05e+000 ± 2.58e+000 1.20e+001 ± 4.99e+000 4.77e+000 ± 2.84e+000 5.95e+000 ± 2.60e+000 5.85e+000 ± 3.15e+000 3.35e+000 ± 2.01e+000 4.35e+000 ± 2.80e+000 2.00e-001 ± 4.10e-001 0±0''',
                        num_elements=9)
  other.append( [mm_7_ncrastrigin, functions.Noncontinuous_Rastrigin] )

  mm_8_schwefel    = f2(u'''3.20e+002 ± 1.85e+002 9.87e+002 ± 2.76e+002 3.26e+002 ± 1.32e+002 8.78e+002 ± 2.93e+002 1.08e+003 ± 2.68e+002 8.51e+002 ± 2.76e+002 7.10e+001 ± 1.50e+002 2.13e+002 ± 1.41e+002 0±0''',
                        num_elements=9)
  other.append( [mm_8_schwefel, functions.Schwefel] )
  return other
