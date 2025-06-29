import helpers

def get_Min_Amount_Candle_Cama_Basis(candlesize):
   MACB = None
   match candlesize:
      case 'M1':
         MACB = 1200
      case 'M5':
         MACB = 240
      case 'M15':
         MACB = 80
      case 'M30':
         MACB = 40
      case 'H1':
         MACB = 20
   return MACB


def get_cama_startidx(timestamps, candlesize):
   indx = -1
   daystart_indexes = []
   MACB = get_Min_Amount_Candle_Cama_Basis(candlesize)
   initday_usable = False
   for ts in timestamps:
      indx += 1
      if all(t == 0 for t in [ts.second, ts.minute]) and ts.hour == 22:
         if not daystart_indexes:
            if indx >= MACB:
               initday_usable = True
         daystart_indexes.append(indx)
   return daystart_indexes, initday_usable


def get_cama_dailydata(timestamps, High, Low, Close, starts, initday_usable):
   dailydata = []
   beginwith = 0 if initday_usable else starts[0]
   for s in starts:
      if not initday_usable and s == starts[0]:
         continue
      dayhigh, daylow = 0, 9999999
      for idx in range(beginwith, s):
         if High[idx] > dayhigh:
            dayhigh = High[idx]
         if Low[idx] < daylow:
            daylow = Low[idx]
      dailydata.append({'High': dayhigh, 'Low': daylow, 'Close': Close[s]})
      beginwith = s
   return dailydata


def create_cama(Close, dailydata, starts, initday_usable, func, initval_factor, name):
   camas = []
   initvalue_filled = False
   dayidx = 0
   for s in starts:
      if not initday_usable and s == starts[0]:
         continue
      if not initvalue_filled:
         for i in range(s):
            camas.append(Close[i]*(initval_factor))
            initvalue_filled = True
      else:
         current_R4_cama = func(dailydata[dayidx]['High'], dailydata[dayidx]['Low'], dailydata[dayidx]['Close'])
         for i in range(len(camas), s):
            camas.append(current_R4_cama)
         dayidx += 1
   while dayidx > len(dailydata)-1:
      dayidx -= 1
   last_R4_cama = func(dailydata[dayidx]['High'], dailydata[dayidx]['Low'], dailydata[dayidx]['Close'])
   for i in range(len(camas), len(Close)):
      camas.append(last_R4_cama)
   camas = helpers.trans_list_to_BT_array(camas, name)
   return camas


def cama_R4(Close, dailydata, starts, initday_usable):
   def calc_R4(high, low, close):
      return ((high - low) * 1.1 / 2 + close)
   cama_R4 = create_cama(Close, dailydata, starts, initday_usable, calc_R4, 1.0025,  'Cama R4')
   return cama_R4

def cama_R3(Close, dailydata, starts, initday_usable):
   def calc_R3(high, low, close):
      return ((high - low) * 1.1 / 4 + close)
   cama_R3 = create_cama(Close, dailydata, starts, initday_usable, calc_R3, 1.002,  'Cama R3')
   return cama_R3

def cama_S3(Close, dailydata, starts, initday_usable):
   def calc_S3(high, low, close):
      return (close - (high - low) * 1.1 / 4)
   cama_S3 = create_cama(Close, dailydata, starts, initday_usable, calc_S3, 0.998,  'Cama S3')
   return cama_S3

def cama_S4(Close, dailydata, starts, initday_usable):
   def calc_S4(high, low, close):
      return (close - (high - low) * 1.1 / 2)
   cama_S4 = create_cama(Close, dailydata, starts, initday_usable, calc_S4, 0.9975,  'Cama S4')
   return cama_S4

