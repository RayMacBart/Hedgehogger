   floats = 0
   ints = 0
   elses = 0

   for p in powers:
      print(p)
      if type(p) == float:
         floats += 1
      elif type(p) == int:
         ints += 1
      else:
         elses += 1
         if isinstance(p, _Indicator):
            print('Indicator type found:', type(p), '  value:', p)
   print('--------------\ntypes found:')
   print('floats:', floats, '  ints:', ints, '  elses:', elses)
   print('--------------')