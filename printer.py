import value_dumper as valdump

def print_results(results):
   for r in results:
      print('____________________________________________________________')
      print(f"\t::: {r['asset']} || {r['candlesize']} || {r['pastshift']} :::\n")
      for k, v in r['stats']._strategy._params.items():
         if k != 'outvars':
            print(f"    {k}: {v}")
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
      # print("r['stats']._strategy._maximize:\n", r['stats']._strategy._maximize)
      # print('____________________________________________________________')

      # print('POWER IMPACT COUNTER:')
      # for k, v in impact_counter.items():
      #    print(f"{k}: {v}")


def dump_results(results):
   for r in results:
      with open('.\\optimization_files\\params.txt', 'a') as paramfile:
         for k, v in r['stats']._strategy._params.items():
            paramfile.write(f"{k}: {v} | ")
         paramfile.write('\n')
      # valdump.dump_return(r['stats']["Return [%]"])
      # valdump.dump_sharpe(r['stats']["Sharpe Ratio"])
      # valdump.dump_sortino(r['stats']["Sortino Ratio"])
      # valdump.dump_calmar(r['stats']["Calmar Ratio"])
      # valdump.dump_profac(r['stats']["Profit Factor"])
      valdump.dump_expectancy(r['stats']["Expectancy [%]"])
      # valdump.dump_avgtrade(r['stats']["Avg. Trade [%]"])
      # valdump.dump_SQN(r['stats']["SQN"])

      