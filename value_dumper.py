
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

def dump_score(SQN, expec, calmar, sortino, profac):
   sqn_mean = -0.3785497274953901
   sqn_std = 4.747979983466789
   expec_mean = 0.004989103069792843
   expec_std = 0.01702601309891024
   calmar_mean = -2.69410745786783
   calmar_std = 9.168788078754021
   sortino_mean = -4.2496372733703796
   sortino_std = 3.8935756666689505
   profac_mean = 2.2252850374777347
   profac_std = 4.455342645663837
   SCORE = ((SQN-sqn_mean)/sqn_std)*38 + \
           ((expec-expec_mean)/expec_std)*22 + \
           ((calmar-calmar_mean)/calmar_std)*16 + \
           ((sortino-sortino_mean)/sortino_std)*13 + \
           ((profac-profac_mean)/profac_std)*11
   with open('.\\optimization_files\\SCORES.txt', 'a') as scores:
      scores.write(str(SCORE)+"\n")

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