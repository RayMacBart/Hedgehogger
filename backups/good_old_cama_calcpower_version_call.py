# old confirming CAMA-version:
# (CHECK IF IT WORKS BETTER THAN THE CAMA VERSION ABOVE, WHICH USES SHIFT!)
         power *= CAMA_calcpower(power, Data.Close[idx-1], T['CAMA']['R4'][idx], T['CAMA']['R3'][idx], T['CAMA']['S3'][idx],
                                 T['CAMA']['S4'][idx], T['CAMA']['3weight'], T['CAMA']['4weight'])
         lastpower = detect_impact(impact_counter, power, lastpower, 'CAMA')