import os

tfpath = '.\\optimization_files\\'
textfiles = [ n for n in os.listdir(path=tfpath) if n[-4:] == '.txt' ]

for tf in textfiles:
   with open(f'{tfpath}{tf}', 'w') as file:
      pass