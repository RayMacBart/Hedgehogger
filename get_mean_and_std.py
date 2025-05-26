import sys
import numpy as np

# parameter: input filename

if __name__ == '__main__':
   results = []
   with open(f'.\\optimization_files\\{sys.argv[1]}.txt', 'r') as paramfile:
      for line in paramfile.readlines():
         results.append(float(line))
   print('MEAN:', np.mean(results))
   print('STD:', np.std(results))
