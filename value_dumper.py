
def dump_results(params):
   with open('.\\optimization_files\\result_values.txt', 'a') as paramfile:
      for k, v in params.items():
         paramfile.write(f"{k}:{v}|")
      paramfile.write('\n')

def dump_paramlog(loop_id, logdict, resultdict):
   with open('.\\optimization_files\\param_log.txt', 'a') as logfile:
      logfile.write(f'Optimization Loop ID:  "{loop_id}"\n')
      for k, v in logdict.items():
         logfile.write(f'{k}: range={v}, results={resultdict[k]}\n')
      logfile.write('---------------------------------\n')

def dump_datachoices(obj, asset, cs, span, past, rand):
   nature = 'SYNTHETIC' if rand else 'normal'
   with open('.\\optimization_files\\datachoice_log.txt', 'a') as choicefile:
      choicefile.write(f"{obj} | {asset}  {cs} | {span}  (-{past}) | {nature}\n")

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

def dump_expectancy(expec):
   with open('.\\optimization_files\\expectancies.txt', 'a') as expectancies:
      expectancies.write(str(expec)+"\n")

def dump_avgtrade(avgtrade):
   with open('.\\optimization_files\\avg_trades.txt', 'a') as avg_trades:
      avg_trades.write(str(avgtrade)+"\n")

def dump_winrate(winrate):
   with open('.\\optimization_files\\winrates.txt', 'a') as win_rates:
      win_rates.write(str(winrate)+"\n")

def dump_SQN(SQN):
   with open('.\\optimization_files\\SQNs.txt', 'a') as SQNs:
      SQNs.write(str(SQN)+"\n")

def tradelog(typ, action, price):
   with open('.\\tradelog.txt', 'a') as logs:
      logs.write(f"{typ} Trade {action} @ {price}\n")