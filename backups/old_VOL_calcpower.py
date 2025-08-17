   # with the new z score normalized version, the below defusing/adjusting isn't necessary anymore
   dePDFM = helpers.defuse(abs(PDFM), defuse_lvl)
   maxval = helpers.defuse(1000, defuse_lvl)
   if ZSDFM > 0:
      factor += 0.2*(deZSDFM/maxval)*weight
   elif ZSDFM < 0:
      factor -= 0.16666*(deZSDFM/maxval)*weight

    normdev = (PDFM - VMMTs['mean']) / VMMTs['std'] # z score normalization --> nice, but not really helping here
   # old idea with surpass treshold:
   vpdf = get_volume_peak_defusing_factor(TS)
   if rises(vols, vols[0]+(vols[0]*(mtcp/100))):
      grown_to_percentage = vols[-1]/(vols[0]/100)
      factor *= ((grown_to_percentage/100)/5)*weight*vpdf
   return factor