import sys
# parameter: input filename


def get_max_parval(pardict, filterlist=[]):
   maxvaldict = {}
   maxcountdict = {}
   for parname in pardict:
      max_amount_count = 0
      max_amount_value = None
      filtervals = []
      for filterdict in filterlist:
         filtervals.append(filterdict[parname])
      for num in set(pardict[parname]):
         if num not in filtervals:
            if pardict[parname].count(num) >= max_amount_count:
               max_amount_value = num
               max_amount_count = pardict[parname].count(num)
      maxvaldict[parname] = max_amount_value
      maxcountdict[parname] = max_amount_count
   return maxvaldict, maxcountdict


if __name__ == '__main__':
   lines = []
   for file in range(1, len(sys.argv)):
      with open(f'.\\optimization_files\\{sys.argv[file]}.txt', 'r') as paramfile:
         for line in paramfile.readlines():
            lines.append(str(line))
   print('total lines:', len(lines), '\n--------------')
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


   val_1st, count_1st = get_max_parval(pardict)
   val_2nd, count_2nd = get_max_parval(pardict, [val_1st,])
   val_3rd, count_3rd = get_max_parval(pardict, [val_1st, val_2nd])
   val_4th, count_4th = get_max_parval(pardict, [val_1st, val_2nd, val_3rd])
   val_5th, count_5th = get_max_parval(pardict, [val_1st, val_2nd, val_3rd, val_4th])

   print('The parameter values highest count rankings:')
   for parname in pardict:
      print(f'{parname}:')
      print(f'   Rank 1:  {val_1st[parname]}  ({count_1st[parname]} counts)')
      print(f'   Rank 2:  {val_2nd[parname]}  ({count_2nd[parname]} counts)')
      print(f'   Rank 3:  {val_3rd[parname]}  ({count_3rd[parname]} counts)')
      print(f'   Rank 4:  {val_4th[parname]}  ({count_4th[parname]} counts)')
      print(f'   Rank 5:  {val_5th[parname]}  ({count_5th[parname]} counts)')
      print('- - - - - - -')
   

   #(old)[backups/find_best_params_old.txt]

