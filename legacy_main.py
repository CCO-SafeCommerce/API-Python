from datetime import datetime
from time import sleep
from dashing import HSplit, VSplit, VGauge, HGauge, Text
import psutil
import os
import mysql.connector
import getmac
import platform
import bcrypt



bdsql = mysql.connector.connect(host="localhost", user="root", password="Vitor@2003", database="safecommerce")

mycursor = bdsql.cursor()

if os.name == 'nt':
    limpar = "cls"

else:
    limpar = "clear"

def tranformar_bytes_em_gigas(value):
    return value / 1024**3


interface_usuario = HSplit(  # Aqui tem a interface do usuario onde HSPLIT é a divisão horizontal e VSPLIT é a divisão vertical
    VSplit( # interface_usuario.items[0]
        Text( # interface_usuario.items[0].items[0]
            ' ',
            border_color=9, # cor da borda
            color=4, # cor do texto
            title='Processos' # titulo
        ),
        HSplit(  # interface_usuario.items[0].items[1]
            VGauge(title='RAM'),  # interface_usuario.items[0].items[0] - RAM - VGauge é um medidor vertical
            VGauge(title='SWAP'),  # interface_usuario.items[0].items[1], Onde items[0] é o primeiro item e items[1] é o segundo item da divisão horizontal
            title='Memória',
            border_color=3
        ),
    ),
    VSplit(  # interface_usuario.items[1]
        HGauge(title='CPU %'),
        HGauge(title='CPU_0'),
        HGauge(title='CPU_1'),
        HGauge(title='CPU_2'),
        HGauge(title='CPU_3'),
        HGauge(title='CPU_4'),
        HGauge(title='CPU_5'),
        HGauge(title='CPU_'),
        HGauge(title='CPU_'),
        title='CPU',
        color=4,
        border_color=5,
    ),
    VSplit(  # interface_usuario.items[2]
        Text(
            ' ',
            title='Outros',
            color=4,
            border_color=4
        ),
        Text(
            ' ',
            title='Disco',
            color=4,
            border_color=6
        ),
        Text(
            ' ',
            title='Rede',
            color=4,
            border_color=7
        ),
    ),
)


while True :
    os.system(limpar)
    print(f"Olá, Escolha uma das opções abaixo para prosseguir!")
    print("1. Cadastrar servidor.")
    print("2. Ver monitoramento.")
    print("3. Sair.")
    escolha = int(input("Digite aqui: "))

    if escolha == 1:
        os.system(limpar)
        print("Seu servidor esta sendo cadastrado...")
        sleep(0.8)

        mac_add = getmac.get_mac_address()
        mycursor.execute(f"select * from Servidor where enderecoMac = '{mac_add}'")

        teste = mycursor.fetchall()

        if len(teste) > 0:
            print("Esse servidor já possui cadastro!")
            sleep(2)

        else:
            os.system(limpar)
            modelo = input("Insira o nome do modelo do servidor: ")
            mac_add = getmac.get_mac_address()  
            so = platform.system()
            mycursor.execute(f"INSERT INTO Servidor VALUES(NULL, '{modelo}', '{so}', '{mac_add}', NULL)")
    
            bdsql.commit()

            os.system(limpar)
            print("Cadastro realizado com sucesso!")
            sleep(3)

    elif escolha == 2:

        mycursor.execute(f"SELECT * FROM Servidor WHERE enderecoMac = '{mac_add}'")

        resposta = mycursor.fetchall()

        if len(resposta) > 0:
            os.system(limpar)
            print("Escolha um dos servidores cadastrados: ")

            for row in resposta :
                print(f"{row[0]}° Servidor")

            servidor = int(input("Qual o servidor você quer monitorar?\nDigite aqui:"))

            os.system(limpar)
            print("Aperte CTRL + C para sair do monitoramento!")

            sleep(2)

            while True:
                processos_tui = interface_usuario.items[0].items[0] # tui é terminal user interface
                for processos in psutil.process_iter():
                    processos_info = processos.as_dict(['name', 'cpu_percent'])
                    if processos_info['cpu_percent'] > 0:
                        nome = processos_info['name']
                        porcentagemProcesso = processos_info['cpu_percent'] 
                        componente = "CPU"
                        metrica_cpu = 1
                        # sql = f"INSERT INTO Parametro VALUES({servidor}, {metrica_cpu})"
                        sql= f"INSERT INTO Leitura VALUES({servidor}, {metrica_cpu}, now(), {porcentagemProcesso}, {componente}"
                        # val = (nome, porcentagemProcesso, servidor, )
                        mycursor.execute(sql)

                        bdsql.commit()
                    
                    else:
                        print("Servidor invalido")
                    

                sql = f"SELECT * FROM LeituraCPU WHERE l.fkServidor = {servidor}" #Testando para ver se a view funciona


                mycursor.execute(sql)

                resposta = mycursor.fetchall()
                
                ordenados = []
                for row in resposta:
                    ordenados.append({'name': row[0], 'cpu_percent': row[1]})



                processos_tui.text = f"{'Nome':<30}CPU"

                for processos in ordenados:
                    processos_tui.text += f"\n{processos['name']:<30} {processos['cpu_percent']}"

                
                # nesse parte do codigo estou pegando a informação da memória RAM e SWAP e cadastrando no banco de dados

                
                
                memoria_tui = interface_usuario.items[0].items[1] # aqui estou dizendo que a memoria está na primeira posição da vertical ou seja no
                # primeiro bloco da divisão vertical e que ele está na segunda posição da horizontal ou seja no segundo bloco da divisão horizontal
                ram_tui = memoria_tui.items[0]
                totalRam = tranformar_bytes_em_gigas(psutil.virtual_memory().total)
                porcentagemRam = psutil.virtual_memory().percent
                ram_tui.value = porcentagemRam # aqui estou mostrando a porcentagem de cpu da dashboard
                ram_tui.title = f'RAM {ram_tui.value} %' # Aqui estou dando um titulo para a dash, e o f é para formatar o texto
                sql = f"INSERT INTO leitura values()" 
                val = (totalRam, porcentagemRam, servidor, )
                mycursor.execute(sql, val)
                bdsql.commit()
                
                # Essas ultimas 3 linhas são para fazer a query no banco, nesse caso os inserts da ram


                swap_tui = memoria_tui.items[1]
                totalSwap = tranformar_bytes_em_gigas(psutil.swap_memory().total)
                porcentagemSwap = psutil.swap_memory().percent
                swap_tui.value = porcentagemSwap
                swap_tui.title = f'SWAP {swap_tui.value} %'

                sql = "INSERT INTO swap(totalMemoria, porcentagemUso, fkServidor, horario) VALUES(%s, %s, %s, now())"
                val = (totalSwap, porcentagemSwap, servidor, )
                mycursor.execute(sql, val)
                bdsql.commit()


                cpu_tui = interface_usuario.items[1]

                cpu_porcentagem_tui = cpu_tui.items[0]
                porcentagemCpu = psutil.cpu_percent(interval=1)
                qtd_processos = len(psutil.Process().cpu_affinity())
                cpu_porcentagem_tui.value = porcentagemCpu
                cpu_porcentagem_tui.title = f'CPU {porcentagemCpu}%'

                sql = "INSERT INTO HistoricoCpu(porcentagemUso, qtdProcessos, fkServidor, horario) VALUES(%s, %s, %s, now())"
                val = (porcentagemCpu, qtd_processos, servidor, )
                mycursor.execute(sql, val)
                bdsql.commit()


                cores_tui = cpu_tui.items[1:9]
                ps_cpu_porcentagem = psutil.cpu_percent(percpu=True)
                for i, (core, valor) in enumerate(zip(cores_tui, ps_cpu_porcentagem)):
                    core.value = valor
                    core.title = f'CPU_{i+1} {valor}%'


                outros_tui = interface_usuario.items[2].items[0]
                outros_tui.text = f'\nUsuário: {psutil.users()[0].name}'
                boot = datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
                outros_tui.text += f'\nHorário do boot: {boot}'
                outros_tui.text += f'\nProcessos: {len(psutil.pids())}'

                disk_tui = interface_usuario.items[2].items[1]

                disk_tui.text = f"{'Partição':<10}{'Uso':<10}{'Lido':<10}{'Escrito'}"

                particao = 'C:'
                porcentagem = psutil.disk_usage('/').percent
                discoLido = tranformar_bytes_em_gigas(psutil.disk_io_counters().read_bytes)
                discoEscrito = tranformar_bytes_em_gigas(psutil.disk_io_counters().write_bytes)

                sql = "INSERT INTO disco(porcentagemUso, lido, escreveu, fkServidor, horario) VALUES(%s, %s, %s, %s, now())"
                val = (porcentagem, discoLido, discoEscrito, servidor, )
                mycursor.execute(sql, val)

                bdsql.commit()
                
                
                disk_tui.text += f'\n{particao:<10}{porcentagem:<10}{round(discoLido, 2):<10}{round(discoEscrito,2)}'
                
                network_tui = interface_usuario.items[2].items[2]

                network_tui.text = f'Enviado: {tranformar_bytes_em_gigas(psutil.net_io_counters().bytes_sent):.2f}GB\n'
                network_tui.text += f'Recebido: {tranformar_bytes_em_gigas(psutil.net_io_counters().bytes_recv):.2f}GB\n'
                
                try:
                    interface_usuario.display() #mostra a interface
                    sleep(1) #espera 1 segundo para mostrar a proxima informação
                except KeyboardInterrupt:
                    sql = mycursor.execute(f"")
        
        
                    break #encerra o loop ao pressionar Ctrl+C

       




        else:
         os.system(limpar)
         sleep(0.8)
         print("Nehum Servidor cadastrado")
         sleep(0.8)
         print("Realizando pré-cadastro")
         sleep(0.8)
         os.system(limpar)
         modelo = input("Insira o nome do modelo do servidor: ")
         mac_add = getmac.get_mac_address()  
         mycursor.execute(f"INSERT INTO Servidor VALUES(NULL, '{modelo}', '{so}', '{mac_add}', NULL)")
    
         bdsql.commit()

         os.system(limpar)
         print("Cadastro realizado com sucesso!")
         sleep(3)
    

    elif escolha == 3:
        os.system(limpar)
        break

    else:
        print("Digite um comando valido!")