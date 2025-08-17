def DIR_calcpower(dirs, weight):  # there are just two values in this 'dirs': the current and the last
   shift = 0
   if dirs[-1] > 0 and dirs[0] < 0:
      shift += weight
   elif dirs[-1] < 0 and dirs[0] > 0:
      shift -= weight
   return shift