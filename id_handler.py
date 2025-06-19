import os

def get_and_increment_loop_id():
   loop_id_filepath = '.\\optimization_files\\optimization_loop_id.txt'
   if not 'optimization_loop_id.txt' in os.listdir('.\\optimization_files'):
      with open(loop_id_filepath, 'w') as idfile:
         idfile.write('A')
   current_loop_id = None
   with open(loop_id_filepath, 'r') as idfile:
      current_loop_id = idfile.read(1)
   if not current_loop_id:
      raise Exception(f'NO OPTIMIZATION LOOP ID COULD BE READ FROM FILE: {loop_id_filepath}')
   loop_ids = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
   next_id_idx = loop_ids.find(current_loop_id) + 1
   next_id_idx = 0 if next_id_idx > 25 else next_id_idx
   next_loop_id = loop_ids[next_id_idx]
   with open(loop_id_filepath, 'w') as idfile:
      idfile.write(next_loop_id)
   return current_loop_id


# following is not used yet:
def get_and_increment_single_opt_id():
   single_opt_id_filepath = '.\\optimization_files\\single_optimization_id.txt'
   if not 'single_optimization_id.txt' in os.listdir('.\\optimization_files'):
      with open(single_opt_id_filepath, 'w') as idfile:
         idfile.write('1')
   current_id = None
   with open(single_opt_id_filepath, 'r') as idfile:
      current_id = int(idfile.read(1))
   if not current_id:
      raise Exception(f'NO SINGLE OPTIMIZATION ID COULD BE READ FROM FILE: {single_opt_id_filepath}')
   next_id = current_id + 1
   with open(single_opt_id_filepath, 'w') as idfile:
      idfile.write(str(next_id))
   return current_id