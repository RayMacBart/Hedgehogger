old way of doing candlesize to volume impact calc:
   if sizeclass_index in range(10):
      cs2vol_impact = 0.35+0.07*sizeclass_index
   elif sizeclass_index in range(10, 16):
      cs2vol_impact = 1.05+0.09*(sizeclass_index-10)
   elif sizeclass_index in range(16, 19):
      cs2vol_impact = 1.6+0.125*(sizeclass_index-16)
   elif sizeclass_index == 19:
      cs2vol_impact = 2
   else:
      raise Exception('CANDLESIZE CLASS NOT IN VALID RANGE OF 0-19!')