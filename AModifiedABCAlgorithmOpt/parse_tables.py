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

def f(data):
    def isnum(s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def fixed_E(s):
        return ("E+" in s or "E-" in s) and ("+-" not in s) and ("-+" not in s) and ("E0" not in s)

    data = data.strip()
    patt = u'([^\s±]+)\s+±\s+([^\s±]+)'
    lines = [r for r in re.findall(patt, data)]
    #ascertain that the scientific notation has a + or - after E
    #(copying from paper is not perfect)
    assert all([(fixed_E(r1) and fixed_E(r2)) for r1,r2 in lines])
    assert all([(isnum(r1) and isnum(r2)) for r1,r2 in lines])
    numbers = [(float(r1), float(r2)) for r1,r2 in lines]
    return numbers

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

  um_1_sphere = f(u'''7.09E-017 ± 4.11E-017 1.00E-016 ± 4.88E-017 1.01E-016 ± 5.29E-017 9.63E-017 ± 5.01E-017 7.92E-017 ± 4.87E-017 7.04E-017 ± 4.55E-017 8.28E-017 ± 4.95E-017 1.05E-016 ± 5.26E-017 1.44E-016 ± 3.72E-017 1.77E-016 ± 5.48E-017 1.89E-010 ± 6.60E-010 3.00E-012 ± 5.48E-012 2.00E-001 ± 3.24E-001 9.68E-017 ± 5.08E-017 8.33E-017 ± 4.99E-017 9.04E-017 ± 4.81E-017 9.08E-017 ± 4.99E-017 1.21E-016 ± 6.66E-017''')
  experiments.append(  _format_data_1(lines=um_1_sphere, func=functions.Sphere)  )

  um_2_rosenbrock = f(u'''2.08E+000 ± 2.44E+000 1.96E+000 ± 2.22E+000 3.16E+000 ± 2.35E+000 3.20E+000 ± 1.81E+000 5.06E+000 ± 1.69E+000 3.66E+000 ± 1.97E+000 3.97E+000 ± 2.24E+000 2.77E+000 ± 2.26E+000 3.22E+000 ± 2.05E+000 3.79E+000 ± 1.99E+000 3.89E+000 ± 1.49E+000 4.42E-001 ± 8.67E-001 5.28E+000 ± 1.49E+000 1.61E+000 ± 1.93E+000 2.38E+000 ± 2.59E+000 2.15E+000 ± 2.46E+000 2.60E+000 ± 2.61E+000 2.08E+000 ± 2.54E+000''')
  experiments.append(  _format_data_1(lines=um_2_rosenbrock, func=functions.Rosenbrock)  )

  mm_3_ackley = f(u'''4.58E-016 ± 1.76E-016 3.79E-016 ± 9.68E-017 3.65E-016 ± 1.84E-016 3.32E-016 ± 1.84E-016 5.13E-016 ± 6.56E-016 4.21E-013 ± 2.04E-012 4.29E-010 ± 2.31E-009 3.41E-014 ± 1.12E-013 2.93E-008 ± 1.53E-007 4.59E-002 ± 2.10E-001 3.05E+000 ± 4.29E+000 2.70E-006 ± 1.46E-005 1.82E+000 ± 5.62E-001 4.03E-016 ± 1.25E-016 3.92E-016 ± 1.07E-016 4.39E-016 ± 2.22E-016 5.11E-016 ± 1.78E-016 5.87E-001 ± 1.36E+000''')
  experiments.append(  _format_data_1(lines=mm_3_ackley, func=functions.Ackley)  )

  mm_4_griewank = f(u'''1.57E-002 ± 9.06E-003 2.17E-002 ± 1.78E-002 1.93E-002 ± 1.30E-002 2.94E-002 ± 2.47E-002 4.00E-002 ± 3.52E-002 5.65E-002 ± 3.05E-002 5.61E-002 ± 3.26E-002 2.00E-002 ± 1.59E-002 3.87E-002 ± 2.64E-002 7.15E-002 ± 5.92E-002 6.81E-001 ± 8.39E-001 1.14E-001 ± 1.25E-001 4.25E-001 ± 1.43E-001 1.52E-002 ± 1.28E-002 2.10E-002 ± 1.32E-002 2.36E-002 ± 1.98E-002 2.50E-002 ± 1.46E-002 2.59E-002 ± 2.01E-002''')
  experiments.append(  _format_data_1(lines=mm_4_griewank, func=functions.Griewank)  )

  mm_5_weierstrass = f(u'''9.01E-006 ± 4.61E-005 1.15E-007 ± 6.17E-007 1.17E-005 ± 4.90E-005 8.80E-004 ± 2.94E-003 4.45E-004 ± 1.69E-003 1.34E-003 ± 5.62E-003 1.92E-003 ± 6.63E-003 1.18E-016 ± 6.38E-016 6.33E-001 ± 7.00E-001 2.89E+000 ± 1.26E+000 6.08E+000 ± 1.46E+000 3.24E-008 ± 3.06E-008 3.10E-001 ± 1.54E-001 9.41E-007 ± 5.07E-006 0.00E+000 ± 0.00E+000 1.88E-006 ± 1.01E-005 2.37E-016 ± 1.28E-015 1.15E-001 ± 3.79E-001''')
  experiments.append(  _format_data_1(lines=mm_5_weierstrass, func=functions.Weierstrass)  )

  mm_6_rastrigin = f(u'''1.61E-016 ± 5.20E-016 2.54E-013 ± 1.37E-012 9.61E-006 ± 5.17E-005 3.38E-001 ± 6.44E-001 7.31E-001 ± 7.23E-001 2.68E+000 ± 1.95E+000 3.71E+000 ± 1.58E+000 1.29E+000 ± 8.95E-001 1.73E+000 ± 1.18E+000 1.17E+001 ± 4.71E+000 3.94E+001 ± 1.41E+001 1.94E-001 ± 3.85E-001 6.97E+000 ± 1.69E+000 1.14E-007 ± 6.16E-007 3.33E-002 ± 1.79E-001 3.32E-002 ± 1.79E-001 6.63E-002 ± 2.48E-001 2.02E+000 ± 3.35E+000''')
  experiments.append(  _format_data_1(lines=mm_6_rastrigin, func=functions.Rastrigin)  )

  mm_7_ncrastrigin = f(u'''6.64E-017 ± 3.96E-017 1.58E-011 ± 7.62E-011 7.84E-002 ± 2.54E-001 8.00E-001 ± 7.02E-001 1.59E+000 ± 9.59E-001 4.21E+000 ± 1.37E+000 5.89E+000 ± 1.69E+000 9.00E-001 ± 7.00E-001 1.37E+000 ± 6.57E-001 3.17E+000 ± 1.42E+000 2.77E+001 ± 8.45E+000 6.80E-001 ± 7.80E-001 7.33E+000 ± 1.65E+000 1.12E-005 ± 6.04E-005 1.17E-006 ± 5.19E-006 7.22E-004 ± 3.89E-003 1.67E-001 ± 4.53E-001 1.17E+000 ± 3.01E+000''')
  experiments.append(  _format_data_1(lines=mm_7_ncrastrigin, func=functions.Noncontinuous_Rastrigin)  )

  mm_8_schwefel = f(u'''7.91E+000 ± 2.95E+001 3.96E+000 ± 2.13E+001 1.97E+001 ± 4.41E+001 2.25E+001 ± 4.45E+001 5.13E+001 ± 8.31E+001 1.78E+002 ± 1.25E+002 3.69E+002 ± 1.52E+002 3.20E+002 ± 1.36E+002 3.59E+002 ± 1.16E+002 9.49E+002 ± 2.19E+002 1.40E+003 ± 2.61E+002 1.09E+002 ± 8.49E+001 5.16E+002 ± 8.75E+001 1.65E+001 ± 4.01E+001 8.39E+000 ± 2.95E+001 1.30E+001 ± 3.55E+001 4.08E+001 ± 6.42E+001 1.53E+002 ± 1.20E+002''')
  experiments.append(  _format_data_1(lines=mm_8_schwefel, func=functions.Schwefel)  )

  return experiments
