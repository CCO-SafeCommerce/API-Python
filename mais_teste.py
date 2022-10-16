from psutil import process_iter
from time import sleep
# for proc in psutil.process_iter():
    
#         # Get process name & pid from process object.
      
#             processName = proc.name()
#             processID = proc.pid
#             print('Nome: ', processName, '  ' , 'Pid: ' , processID)
            
cont = 0
for proc in process_iter(['pid', 'name', 'username']):

    if cont < 5:
        print(f'Nome: {proc.name()}   Pid: {proc.pid} \n')
    cont += 1

# from psutil import process_iter
# from random import randrange

# cont = 0
# a = process_iter()
# list = []
# for x in range(0, 5):
#     list.append(0, process_iter[randrange(0, len(process_iter))])
#     print(list)