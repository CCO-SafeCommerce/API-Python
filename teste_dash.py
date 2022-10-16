
from matplotlib.pyplot import title
from psutil import cpu_percent, cpu_count, cpu_freq, virtual_memory, disk_usage, disk_io_counters, process_iter
from dashing import VSplit, Text, HSplit
from time import sleep
import os

interface = HSplit(
    VSplit( # CPU
        Text(
            '',
            title="Medidas da CPU",
            border_color =4,
            color= 7)   
    ),

    VSplit( #RAM
        Text(
            '',
            title="Medidas da RAM",
            border_color=3,
            color=7
        ),


        Text(
            '',
            title="Medidas do Disco",
            border_color=1,
            color=7
        )
    ),
    


    VSplit( #PROCESSOS
        Text(
            '',
            title="Listagem de Processos",
            border_color=2,
            color=7
        )
    )
)


while True:
    os.system('cls')
    
    
    

    #Porcentagem de Uso da CPU
    teste = interface.items[0].items[0]
    teste.text = f''
    teste.text += f'\nPorcentagem de uso: {cpu_percent()}%\n'

    #Quantidade de cpu logica
    teste.text += f'\nQuantidade de cpus logicas: {cpu_count()}u\n'

    #Porcentagem de uso de Core por CPU
    ps_cpu_percent = cpu_percent(percpu=True)
    for i in range(len(ps_cpu_percent)):
       
        teste.text += f'\nUso da CPU {i + 1}: {ps_cpu_percent[i]}%\n'

    # #Frequencia de CPU
    teste.text += f'\nFrequência de uso da CPU:\n{cpu_freq(percpu=False)}Mhz\n'

    #Total de memória RAM
    ram = interface.items[1].items[0]
    ram.text = f''
    ram.text += f'\nTotal de memória RAM: {round(virtual_memory().total)} Gb\n'


    # Frequencia de uso da RAM
    ram.text += f'\nTotal de uso de memória RAM: {virtual_memory().percent}%\n'

    #Total de Disco
    disco= interface.items[1].items[1]
    disco.text = f''
    disco.text += f'\nTotal de Disco: {disk_usage("/").total} Tb\n'

    #Uso de Disco
    disco.text += f'\nTotal de uso de Disco: {disk_usage("/").percent}%\n'

    #Lidos Pelo Disco
    disco.text += f'\nTotal Lido Pelo Disco: {disk_io_counters(perdisk=False, nowrap=True).read_time} ms\n'

    #Escrito Pelo Disco
    disco.text += f'\nTotal Escrito Pelo Disco: {disk_io_counters(perdisk=False, nowrap=True).write_time} ms'

    #Listagem de Processos
    processos = interface.items[2].items[0]
    proc = process_iter(['pid', 'name', 'username'])
    for p in proc:
        processos.text = f''
        processos.text += str(p)
        processos.text += f''
    
    

        


    try:
        interface.display()
        sleep(2)
    except KeyboardInterrupt:
        os.system('cls')
        break