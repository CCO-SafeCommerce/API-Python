import graph
import os
import platform

so = platform.system()

if so == 'Linux':
    clear = 'clear'
else:
    clear = 'cls'

isWorking = True

while isWorking:
    os.system(clear)
    print('='*30 + '\n'
        '[1] Ver gráfico de uso da CPU\n' +
        '[2] Ver gráfico de uso da memória\n' +
        '[3] Ver gráfico de uso do disco\n' +
        '[4] Sair\n' +
        '='*30
    )
    opt = int(input('Escolha uma opção: '))

    if opt == 1:
        try:
            graph.showCPU()
        except KeyboardInterrupt:
            pass
    elif opt == 2:
        try:
            graph.showMEMO()
        except KeyboardInterrupt:
            pass
    elif opt == 3:
        try:
            graph.showDISK()
        except KeyboardInterrupt:
            pass
    elif opt == 4:
        isWorking = False







