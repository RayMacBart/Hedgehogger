
def dump_return(returnval):
   with open('.\\optimization_files\\returns.txt', 'a') as returns:
      returns.write(str(returnval)+"\n")

def dump_sharpe(sharpe):
   with open('.\\optimization_files\\sharpes.txt', 'a') as sharpes:
      sharpes.write(str(sharpe)+"\n")

def dump_sortino(sortino):
   with open('.\\optimization_files\\sortinos.txt', 'a') as sortinos:
      sortinos.write(str(sortino)+"\n")

def dump_calmar(calmar):
   with open('.\\optimization_files\\calmars.txt', 'a') as calmars:
      calmars.write(str(calmar)+"\n")

def dump_profac(profac):
   with open('.\\optimization_files\\profitfactors.txt', 'a') as profitfactors:
      profitfactors.write(str(profac)+"\n")