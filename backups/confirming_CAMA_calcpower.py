# old, but more sophisticated CONFIRMING (with factor!) version - CHECK WHICH VERSION WORKS BETTER!!

def CAMA_calcpower(pow, close_val, R4, R3, S3, S4, w3, w4):  
   factor = 1
   if (pow < 0 and close_val > R4) or (pow > 0 and close_val < S4):
      factor += w4/4
   elif (pow < 0 and close_val > R3) or (pow > 0 and close_val < S3):
      factor += w3/4
   elif (pow < 0 and close_val < S4) or (pow > 0 and close_val > R4):
      factor -= w4/6
   elif (pow < 0 and close_val < S3) or (pow > 0 and close_val > R3):
      factor -= w3/6
   if factor < 0.5:  # NEW (+clear): 1 indicator can't decrease power more than make it half
      factor = 0.5
   return factor