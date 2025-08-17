                  maximize = objective,
                  maximize = lambda stats: (stats["Expectancy [%]"]-expec_mean)/expec_std + \
                                           (stats["Profit Factor"]-profac_mean)/profac_std + \
                                           (stats["SQN"]-sqn_mean)/sqn_std,
                  if stats['# Trades'] >= 100 else -np.inf,