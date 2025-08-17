def change_to_diffs2prior(vmmts):
   return [ (lambda prior, current: (current/(prior/100)-100) if not (np.isnan(current) or np.isnan(prior)) else 0)\
           (vmmts[(m-1) if (m > 0) else len(vmmts)-1], vmmts[m]) for m in range(len(vmmts)) ]