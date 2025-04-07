def is_falling_below(S, B): # S=Series, B=Boundary
   if len(S) == 3:
      if ((S[-1]<=B and (S[-2]>B or S[-2]<=B) and S[-3]>B) and
          (B-S[-1] >= B-S[-2] >= B-S[-3])):
         return True
   elif len(S) == 4:
      if ((S[-1]<=B and 
         (((S[-2]>B or S[-2]<=B) and S[-3]>B) or 
            ((S[-2]<=B) and (S[-3]>B or S[-3]<=B))) and 
            S[-4]>B) and 
            (B-S[-1] >= B-S[-2] >= B-S[-3] >= B-S[-4])):
         return True
   elif len(S) == 5:
      if ((S[-1]<=B and 
         (((S[-2]>B or S[-2]<=B) and S[-3]>B and S[-4]>B) or 
            ((S[-2]<=B) and (S[-3]>B or S[-3]<=B) and S[-4]>B) or
            ((S[-2]<=B) and (S[-3]<=B) and (S[-4]>B or S[-4]<=B))) and 
            S[-5]>B) and 
            (B-S[-1] >= B-S[-2] >= B-S[-3] >= B-S[-4] >= B-S[-5])):
         return True
   elif len(S) == 6:
      if ((S[-1]<=B and 
           (((S[-2]>B or S[-2]<=B) and S[-3]>B and S[-4]>B and S[-5]>B) or 
            ((S[-2]<=B) and (S[-3]>B or S[-3]<=B) and S[-4]>B and S[-5]>B) or
            ((S[-2]<=B) and (S[-3]<=B) and (S[-4]>B or S[-4]<=B) and S[-5]>B) or
            ((S[-2]<=B) and (S[-3]<=B) and (S[-4]<=B) and (S[-5]>B or S[-5]<=B))) and 
            S[-6]>B) and 
            (B-S[-1] >= B-S[-2] >= B-S[-3] >= B-S[-4] >= B-S[-5] >= B-S[-6])):
         return True
   elif len(S) == 7:
      if ((S[-1]<=B and 
           (((S[-2]>B or S[-2]<=B) and S[-3]>B and S[-4]>B and S[-5]>B and S[-6]>B) or 
            ((S[-2]<=B) and (S[-3]>B or S[-3]<=B) and S[-4]>B and S[-5]>B and S[-6]>B) or
            ((S[-2]<=B) and (S[-3]<=B) and (S[-4]>B or S[-4]<=B) and S[-5]>B and S[-6]>B) or
            ((S[-2]<=B) and (S[-3]<=B) and (S[-4]<=B) and (S[-5]>B or S[-5]<=B) and S[-6]>B) or
            ((S[-2]<=B) and (S[-3]<=B) and (S[-4]<=B) and (S[-5]<=B) and (S[-6]>B or S[-6]<=B))) and 
            S[-7]>B) and 
            (B-S[-1] >= B-S[-2] >= B-S[-3] >= B-S[-4] >= B-S[-5] >= B-S[-6] >= B-S[-7])):
         return True
   elif len(S) == 8:
      if ((S[-1]<=B and 
           (((S[-2]>B or S[-2]<=B) and S[-3]>B and S[-4]>B and S[-5]>B and S[-6]>B and S[-7]>B) or 
            ((S[-2]<=B) and (S[-3]>B or S[-3]<=B) and S[-4]>B and S[-5]>B and S[-6]>B and S[-7]>B) or
            ((S[-2]<=B) and (S[-3]<=B) and (S[-4]>B or S[-4]<=B) and S[-5]>B and S[-6]>B and S[-7]>B) or
            ((S[-2]<=B) and (S[-3]<=B) and (S[-4]<=B) and (S[-5]>B or S[-5]<=B) and S[-6]>B and S[-7]>B) or
            ((S[-2]<=B) and (S[-3]<=B) and (S[-4]<=B) and (S[-5]<=B) and (S[-6]>B or S[-6]<=B) and S[-7]>B) or
            ((S[-2]<=B) and (S[-3]<=B) and (S[-4]<=B) and (S[-5]<=B) and (S[-6]<=B) and (S[-7]>B or S[-7]<=B))) and 
            S[-8]>B) and 
            (B-S[-1] >= B-S[-2] >= B-S[-3] >= B-S[-4] >= B-S[-5] >= B-S[-6] >= B-S[-7] >= B-S[-8])):
         return True
   else:
      print(f'ERROR: invalid Series length given to function "is_falling_below": must be between 3 and 8 (given: {len(S)})')
   return False


def is_rising_above(S, B): # S=Series, B=Boundary
   if len(S) == 3:
      if ((S[-1]>=B and (S[-2]<B or S[-2]>=B) and S[-3]<B) and
          (B-S[-1] <= B-S[-2] <= B-S[-3])):
         return True
   elif len(S) == 4:
      if ((S[-1]>=B and 
         (((S[-2]<B or S[-2]>=B) and S[-3]<B) or 
            ((S[-2]>=B) and (S[-3]<B or S[-3]>=B))) and 
            S[-4]<B) and 
            (B-S[-1] <= B-S[-2] <= B-S[-3] <= B-S[-4])):
         return True
   elif len(S) == 5:
      if ((S[-1]>=B and 
         (((S[-2]<B or S[-2]>=B) and S[-3]<B and S[-4]<B) or 
            ((S[-2]>=B) and (S[-3]<B or S[-3]>=B) and S[-4]<B) or
            ((S[-2]>=B) and (S[-3]>=B) and (S[-4]<B or S[-4]>=B))) and 
            S[-5]<B) and 
            (B-S[-1] <= B-S[-2] <= B-S[-3] <= B-S[-4] <= B-S[-5])):
         return True
   elif len(S) == 6:
      if ((S[-1]>=B and 
           (((S[-2]<B or S[-2]>=B) and S[-3]<B and S[-4]<B and S[-5]<B) or 
            ((S[-2]>=B) and (S[-3]<B or S[-3]>=B) and S[-4]<B and S[-5]<B) or
            ((S[-2]>=B) and (S[-3]>=B) and (S[-4]<B or S[-4]>=B) and S[-5]<B) or
            ((S[-2]>=B) and (S[-3]>=B) and (S[-4]>=B) and (S[-5]<B or S[-5]>=B))) and 
            S[-6]<B) and 
            (B-S[-1] <= B-S[-2] <= B-S[-3] <= B-S[-4] <= B-S[-5] <= B-S[-6])):
         return True
   elif len(S) == 7:
      if ((S[-1]>=B and 
           (((S[-2]<B or S[-2]>=B) and S[-3]<B and S[-4]<B and S[-5]<B and S[-6]<B) or 
            ((S[-2]>=B) and (S[-3]<B or S[-3]>=B) and S[-4]<B and S[-5]<B and S[-6]<B) or
            ((S[-2]>=B) and (S[-3]>=B) and (S[-4]<B or S[-4]>=B) and S[-5]<B and S[-6]<B) or
            ((S[-2]>=B) and (S[-3]>=B) and (S[-4]>=B) and (S[-5]<B or S[-5]>=B) and S[-6]<B) or
            ((S[-2]>=B) and (S[-3]>=B) and (S[-4]>=B) and (S[-5]>=B) and (S[-6]<B or S[-6]>=B))) and 
            S[-7]<B) and 
            (B-S[-1] <= B-S[-2] <= B-S[-3] <= B-S[-4] <= B-S[-5] <= B-S[-6] <= B-S[-7])):
         return True
   elif len(S) == 8:
      if ((S[-1]>=B and 
           (((S[-2]<B or S[-2]>=B) and S[-3]<B and S[-4]<B and S[-5]<B and S[-6]<B and S[-7]<B) or 
            ((S[-2]>=B) and (S[-3]<B or S[-3]>=B) and S[-4]<B and S[-5]<B and S[-6]<B and S[-7]<B) or
            ((S[-2]>=B) and (S[-3]>=B) and (S[-4]<B or S[-4]>=B) and S[-5]<B and S[-6]<B and S[-7]<B) or
            ((S[-2]>=B) and (S[-3]>=B) and (S[-4]>=B) and (S[-5]<B or S[-5]>=B) and S[-6]<B and S[-7]<B) or
            ((S[-2]>=B) and (S[-3]>=B) and (S[-4]>=B) and (S[-5]>=B) and (S[-6]<B or S[-6]>=B) and S[-7]<B) or
            ((S[-2]>=B) and (S[-3]>=B) and (S[-4]>=B) and (S[-5]>=B) and (S[-6]>=B) and (S[-7]<B or S[-7]>=B))) and 
            S[-8]<B) and 
            (B-S[-1] <= B-S[-2] <= B-S[-3] <= B-S[-4] <= B-S[-5] <= B-S[-6] <= B-S[-7] <= B-S[-8])):
         return True
   else:
      print(f'ERROR: invalid Series length given to function "is_rising_above": must be between 3 and 8 (given: {len(S)})')
   return False