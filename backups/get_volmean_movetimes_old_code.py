hourly_list = {}
hourly_averages = {}
hourly_maxs = {}
hourly_mins = {}
for h in range(24):
   hourly_list[h] = []

for h in range(24):
   for m in range(0,60,5):
      hourly_list[h].append(time_mean_dict[h][m])
for h in hourly_list:
   hourly_averages[h] = np.mean(hourly_list[h])
   hourly_maxs[h] = max(hourly_list[h])
   hourly_mins[h] = min(hourly_list[h])

for h in range(24):
   print('_____________________')
   print('')
   print('HOUR:', h)
   for m in range(0,60,5):
      print(f'   min {m}:', time_mean_dict[h][m])
   print('AV:', hourly_averages[h])
   print('MAX:', hourly_maxs[h])
   print('MIN:', hourly_mins[h])

overall_av = np.mean(list(hourly_averages.values()))
print('overall average:', overall_av)