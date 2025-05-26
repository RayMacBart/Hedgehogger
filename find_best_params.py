import sys

# parameter: input filename

if __name__ == '__main__':
   lines = []
   for file in range(1, len(sys.argv)):
      with open(f'.\\optimization_files\\{sys.argv[file]}.txt', 'r') as paramfile:
         for line in paramfile.readlines():
            lines.append(str(line))
   linelist = lines[0].strip().split('|')
   linelist = [i for i in linelist if i]
   pardict = {}
   for paridx in range(len(linelist)):
      pardict[linelist[paridx].split(':')[0]] = []
   for line in lines:
      for parstr in line.split('|'):
         if len(parstr) >= 4:
            parpair = parstr.split(':')
            pardict[parpair[0]].append(int(parpair[1]))
   resultdict = {}
   for parname in pardict:
      max_amount_count = 0
      max_amount_value = None
      for num in set(pardict[parname]):
         if pardict[parname].count(num) >= max_amount_count:
            max_amount_value = (max_amount_value, num) if (pardict[parname].count(num) == max_amount_count and 
                                                           max_amount_value) else num
            max_amount_count = pardict[parname].count(num)
      resultdict[parname] = max_amount_value
   print('The parameter values with the highest counts are:')
   for par in resultdict:
      print(f'{par}: {resultdict[par]}')
   