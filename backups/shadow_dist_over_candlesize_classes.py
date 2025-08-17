# old way for distributing shadows over candlesize classes (needed sidiras in function!):
shacos = [0 for i in range(SCG)] # shadow counts
for row in sorted_copieddf.itertuples():
   rowidx += 1
   bullish = True if row.Close - row.Open >= 0 else False  # candlesizes of 0 ("Dojis") will be in bullish records
   for idx in range(SCG):
      # if (int(abs(row.Close - row.Open)*100000) in range(int(sidiras[idx][0]*100000), int(sidiras[idx][1]*100000)) or
      #     (int(sidiras[idx][0]*100000) == int(sidiras[idx][1]*100000) == int(abs(row.Close - row.Open)*100000))):
      if shacos[idx] < datasize // SCG:
         print(f'row {rowidx},  sizeclass {idx}:')
         print(f'shacos[{idx}]={shacos[idx]}  <  datasize={datasize} // SCG={SCG}  (--> = {datasize // SCG})')
         if bullish:
            bullup_shadows[idx].append(row.High - row.Close)
            bulldown_shadows[idx].append(row.Open - row.Low)
         else:
            bearup_shadows[idx].append(row.High - row.Open)
            beardown_shadows[idx].append(row.Close - row.Low)
         shacos[idx] += 1
         break
      else:
         print(f'shacos[{idx}] = {shacos[idx]} (is full)')
         continue