         # DIR_calcpower is for experimental purposes only (not recommended)
         power += DIR_calcpower(T['DIR']['dir'][idx-1:idx+1], T['DIR']['weight'])
         lastpower = detect_impact(impact_counter, power, lastpower, 'DIR')