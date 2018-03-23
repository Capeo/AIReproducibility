from multiprocessing import pool
import random
import b

def run():
  inp = list(range(5))
  list(mp_pool.map(b.helper, inp))
  #list(map(b.helper, inp))

if __name__ == "__main__":
  random.seed(64)
  #use 2 regardless of number of cores for testing purposes
  print("Pool of 4:")
  mp_pool = pool.Pool(4)
  run()
  mp_pool.close()

  print("\nPool of 1:")
  mp_pool = pool.Pool(1)
  run()
  mp_pool.close()
