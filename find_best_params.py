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
   




   #    resultdict = {}
   # rescountdict = {}
   # for parname in pardict:
   #    max_amount_count = 0
   #    max_amount_value = None
   #    for num in set(pardict[parname]):
   #       if pardict[parname].count(num) >= max_amount_count:
   #          max_amount_value = (max_amount_value, num) if (pardict[parname].count(num) == max_amount_count and 
   #                                                         max_amount_value) else num
   #          max_amount_count = pardict[parname].count(num)
   #    resultdict[parname] = max_amount_value
   #    rescountdict[parname] = max_amount_count
   
   # dict_2nds = {}
   # count2nds_dict = {}
   # for parname in pardict:
   #    secmax_amount_count = 0
   #    secmax_amount_value = None
   #    for num in set(pardict[parname]):
   #       if num != resultdict[parname]:
   #          if pardict[parname].count(num) >= secmax_amount_count:
   #             secmax_amount_value = (secmax_amount_value, num) if (pardict[parname].count(num) == secmax_amount_count and 
   #                                                          secmax_amount_value) else num
   #             secmax_amount_count = pardict[parname].count(num)
   #    dict_2nds[parname] = secmax_amount_value
   #    count2nds_dict[parname] = secmax_amount_count
   
   # dict_3rds = {}
   # count3rds_dict = {}
   # for parname in pardict:
   #    thimax_amount_count = 0
   #    thimax_amount_value = None
   #    for num in set(pardict[parname]):
   #       if num not in [resultdict[parname], dict_2nds[parname]]:
   #          if pardict[parname].count(num) >= thimax_amount_count:
   #             thimax_amount_value = (thimax_amount_value, num) if (pardict[parname].count(num) == thimax_amount_count and 
   #                                                          thimax_amount_value) else num
   #             thimax_amount_count = pardict[parname].count(num)
   #    dict_3rds[parname] = thimax_amount_value
   #    count3rds_dict[parname] = thimax_amount_count

   # dict_4ths = {}
   # count4ths_dict = {}
   # for parname in pardict:
   #    foumax_amount_count = 0
   #    foumax_amount_value = None
   #    for num in set(pardict[parname]):
   #       if num not in [resultdict[parname], dict_2nds[parname], dict_3rds[parname]]:
   #          if pardict[parname].count(num) >= foumax_amount_count:
   #             foumax_amount_value = (foumax_amount_value, num) if (pardict[parname].count(num) == foumax_amount_count and 
   #                                                          foumax_amount_value) else num
   #             foumax_amount_count = pardict[parname].count(num)
   #    dict_4ths[parname] = foumax_amount_value
   #    count4ths_dict[parname] = foumax_amount_count

   # dict_5ths = {}
   # count5ths_dict = {}
   # for parname in pardict:
   #    fifmax_amount_count = 0
   #    fifmax_amount_value = None
   #    for num in set(pardict[parname]):
   #       if num not in [resultdict[parname], dict_2nds[parname], dict_3rds[parname], dict_4ths[parname]]:
   #          if pardict[parname].count(num) >= fifmax_amount_count:
   #             fifmax_amount_value = (fifmax_amount_value, num) if (pardict[parname].count(num) == fifmax_amount_count and 
   #                                                          fifmax_amount_value) else num
   #             fifmax_amount_count = pardict[parname].count(num)
   #    dict_5ths[parname] = fifmax_amount_value
   #    count5ths_dict[parname] = fifmax_amount_count