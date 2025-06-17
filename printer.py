import value_dumper as valdump

def print_results(results):
   for r in results:
      print('____________________________________________________________\n')
      print(f"\t::: {r['asset']} || {r['candlesize']} || {r['pastshift']} :::\n")
      for k, v in r['stats']._strategy._params.items():
         if k != 'outvars':
            print(f"     {k}: {v}")
      print('____________________________________________________________')
      # print("r['stats']:\n", r['stats'])
      # print('____________________________________________________________')
      print("Return:", r['stats']["Return [%]"])
      print("Avg. Trade:", r['stats']["Avg. Trade [%]"])
      print("Expectancy:", r['stats']["Expectancy [%]"])
      print("SQN:", r['stats']["SQN"])
      print("Sharpe Ratio:", r['stats']["Sharpe Ratio"])
      print("Sortino Ratio:", r['stats']["Sortino Ratio"])
      print("Calmar Ratio:", r['stats']["Calmar Ratio"])
      print("Profit Factor:", r['stats']["Profit Factor"])
      print('____________________________________________________________')
      # print("stopdist:", r['stats']._strategy.stopdist)
      # print('r['stats']._trades:\n', r['stats']._trades)
      print("optimized objective: ", r['objective'])
      print('____________________________________________________________')

      print('POWER IMPACT COUNTER:')
      for k, v in r['stats']._strategy.impact_counter.items():
         print(f"{k}: {v}")


def dump_results(results):
   resultdict = {}
   for k in results[0]['stats']._strategy._params.keys():
      resultdict[k] = []
   for r in results:
      for k, v in r['stats']._strategy._params.items():
         resultdict[k].append(v)
      valdump.dump_results(r['stats']._strategy._params)
      valdump.dump_datachoices(r['objective'], r['asset'], r['candlesize'], r['dataspan'],r['pastshift'], r['randomized'])
      valdump.dump_expectancy(r['stats']["Expectancy [%]"])
      valdump.dump_profac(r['stats']["Profit Factor"])
      valdump.dump_SQN(r['stats']["SQN"])
      # valdump.dump_return(r['stats']["Return [%]"])
      valdump.dump_sharpe(r['stats']["Sharpe Ratio"])
      valdump.dump_sortino(r['stats']["Sortino Ratio"])
      valdump.dump_calmar(r['stats']["Calmar Ratio"])
      # valdump.dump_avgtrade(r['stats']["Avg. Trade [%]"])
   with open('.\\optimization_files\\datachoice_log.txt', 'a') as choicefile:
      choicefile.write("-----------------------------------\n")
   valdump.dump_paramlog(results[0]['param_opt_log_dict'], resultdict)

      