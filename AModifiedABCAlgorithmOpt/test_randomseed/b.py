import random
import math
random.seed(64)
def helper(i):
  random.seed(64+i)
  r = random.random()
  for j in range(100):
    xyz = (math.sqrt(r**10)**0.1)**3
  print("{}, {:3.3f}".format(i,r))