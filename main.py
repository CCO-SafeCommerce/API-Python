from datetime import datetime
from time import sleep
from dashing import HSplit, VSplit, VGauge, HGauge, Text
import psutil
import os
import mysql.connector
import matplotlib.pyplot as plt

bdsql = mysql.connector.connect(host="localhost", user="root", password="@Pedrinho1", database="safecommerce")

mycursor = bdsql.cursor()

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
    os.system('cls')
    print(f"Olá, Escolha uma das opções abaixo para prosseguir!")
    print("1. Cadastrar servidor.")
    print("2. Ver monitoramento.")
    print("3. Ver gráfico.")
    print("4. Sair.")
    escolha = int(input("Digite aqui:"))

    if escolha == 1:
        os.system('cls')
        qtdServers = int(input("Quantos servidores você deseja cadastrar?\nDigite aqui:"))
        i = 1   
        while i <= qtdServers :
            mycursor.execute("INSERT INTO servidor VALUES()")

            bdsql.commit()

            i += 1

        print("Cadastro realizado com sucesso!")
        sleep(3)

    elif escolha == 2:

        mycursor.execute("SELECT * FROM servidor")

        resposta = mycursor.fetchall()

        if len(resposta) > 0:
            os.system("cls")
            print("Escolha um dos servidores cadastrados: ")

            for row in resposta :
                print(f"{row[0]}° Servidor")

            servidor = int(input("Qual o servidor você quer monitorar?\nDigite aqui:"))

            os.system('cls')
            print("Aperte CTRL + C para sair do monitoramento!")

            sleep(2)

            while True:
                processos_tui = interface_usuario.items[0].items[0] # tui é terminal user interface
                for processos in psutil.process_iter():
                    processos_info = processos.as_dict(['name', 'cpu_percent'])
                    if processos_info['cpu_percent'] > 0:
                        nome = processos_info['name']
                        porcentagemProcesso = processos_info['cpu_percent'] 
                        sql = "INSERT INTO processo(nome, porcentagemCpu, fkServidor, horario) VALUES(%s, %s, %s, now())"
                        val = (nome, porcentagemProcesso, servidor, )
                        mycursor.execute(sql, val)

                        bdsql.commit()

                sql = "SELECT nome, max(porcentagemCpu) FROM processo WHERE fkServidor = %s AND DAY(horario) >= DAY(now()) AND MINUTE(horario) >= MINUTE(now()) GROUP BY nome ORDER BY max(porcentagemCpu) DESC LIMIT 10"
                val = (servidor, )

                mycursor.execute(sql, val)

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
                sql = "INSERT INTO ram(totalMemoria, porcentagemUso, fkServidor, horario) VALUES(%s, %s, %s, now())" 
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
                    break #encerra o loop ao pressionar Ctrl+C

        else:
            print("Nenhuma resposta encontrada!")
            sleep(3)
    
    elif escolha == 3:
        mycursor.execute("SELECT * FROM servidor")

        resposta = mycursor.fetchall()

        if len(resposta) > 0:
            os.system("cls")
            print("Você deseja ver os gráficos de qual servidor?")

            for row in resposta :
                print(f"{row[0]}° Servidor")

            servidor = int(input("Digite aqui:"))

            os.system('cls')
            print("Você deseja ver o gráfico de qual componente?")
            print("1. Processos")
            print("2. RAM")
            print("3. SWAP")
            print("4. CPU")
            print("5. Disco")
            
            escolhaGrafico = int(input("Digite aqui:"))

            if escolhaGrafico == 1:
                sql = "SELECT porcentagemCpu, nome, DATE_FORMAT(horario, '%e %b, %H:%i') AS horario FROM processo WHERE fkServidor = %s AND day(horario) >= day(now()) GROUP BY nome ORDER BY porcentagemCpu DESC LIMIT 5"
                parametros = (servidor, )

                mycursor.execute(sql, parametros)

                resposta = mycursor.fetchall()

                porCpu = []
                horarioProcesso = []

                for row in resposta:
                    porCpu.append(row[0])
                    horarioProcesso.append(row[1] + "\n" + row[2])


                plt.bar(horarioProcesso, porCpu, color="green")

                plt.xticks(horarioProcesso)

                plt.xlabel('Nome e horario do processo')

                plt.ylabel('Porcentagem de uso do processo')

                plt.title('Quantidade de uso da cpu dos processos por horario do dia atual')

                plt.show()
            
            elif escolhaGrafico == 2:
                sql = "SELECT porcentagemUso, DATE_FORMAT(horario, '%e %b, %H:%i') AS horario FROM ram WHERE fkServidor = %s AND day(horario) >= day(now()) GROUP BY porcentagemUso ORDER BY porcentagemUso DESC LIMIT 5"
                parametros = (servidor, )

                mycursor.execute(sql, parametros)

                resposta = mycursor.fetchall()

                porCpu = []
                horarioProcesso = []

                for row in resposta:
                    porCpu.append(row[0])
                    horarioProcesso.append(str(row[0]) +  "%\n" + row[1])

                
                plt.bar(horarioProcesso, porCpu, color="red")

                plt.xticks(horarioProcesso)

                plt.ylim([0, 100])

                plt.xlabel('Porcentagem e horario da memoria ram')

                plt.ylabel('Porcentagem total da memoria ram')

                plt.title('Porcentagem de uso da RAM e seus horarios do dia atual')

                plt.show()

            elif escolhaGrafico == 3:
                sql = "SELECT porcentagemUso, DATE_FORMAT(horario, '%e %b, %H:%i') AS horario FROM swap WHERE fkServidor = %s AND day(horario) >= day(now()) GROUP BY porcentagemUso ORDER BY porcentagemUso DESC LIMIT 5"
                parametros = (servidor, )

                mycursor.execute(sql, parametros)

                resposta = mycursor.fetchall()

                porCpu = []
                horarioProcesso = []

                for row in resposta:
                    porCpu.append(row[0])
                    horarioProcesso.append(str(row[0]) +  "%\n" + row[1])

                
                plt.bar(horarioProcesso, porCpu, color="blue")

                plt.xticks(horarioProcesso)

                plt.ylim([0, 100])

                plt.xlabel('Porcentagem e horario da memoria swap')

                plt.ylabel('Porcentagem total de memoria swap')

                plt.title('Porcentagem de uso da swap e seus horarios do dia atual')

                plt.show()

            elif escolhaGrafico == 4:
                sql = "SELECT porcentagemUso, qtdProcessos, DATE_FORMAT(horario, '%e %b, %H:%i') AS horario FROM HistoricoCpu WHERE fkServidor = %s GROUP BY porcentagemUso ORDER BY porcentagemUso DESC LIMIT 5;"
                parametros = (servidor, )

                mycursor.execute(sql, parametros)

                resposta = mycursor.fetchall()

                porCpu = []
                horarioProcesso = []

                for row in resposta:
                    porCpu.append(row[0])
                    horarioProcesso.append(str(row[0]) + "%\nProcessos: " + str(row[1]) + "\n" + row[2])


                plt.bar(horarioProcesso, porCpu, color="purple")

                plt.xticks(horarioProcesso)

                plt.ylim([0, 100])

                plt.xlabel('Porcentagem de uso, quantidade de processos, e data da CPU')

                plt.ylabel('Porcentagem de uso total da CPU')

                plt.title('Quantidade de uso da CPU dos processos por horario')

                plt.show()

            elif escolhaGrafico == 5:
                sql = "SELECT porcentagemUso, lido, escreveu, DATE_FORMAT(horario, '%e %b, %H:%i') AS horario FROM disco WHERE fkServidor = %s AND day(horario) >= day(now()) GROUP BY porcentagemUso ORDER BY porcentagemUso DESC LIMIT 4"
                parametros = (servidor, )

                mycursor.execute(sql, parametros)

                resposta = mycursor.fetchall()

                porCpu = []
                horarioProcesso = []

                for row in resposta:
                    porCpu.append(row[0])
                    horarioProcesso.append(str(row[0]) + "%, Lido:" + str(row[1]) + "\nEscrito:" + str(row[2]) + "\n" + row[3])


                plt.bar(horarioProcesso, porCpu, color="gold")

                plt.xticks(horarioProcesso)

                plt.xlabel('Porcentagem de uso, lido, escrito e horario do disco')

                plt.ylabel('Porcentagem de uso total do disco')

                plt.title('Dados sobre o disco no dia de hoje')

                plt.show()
            else:
                print("Digite algo valido, por favor!")

        else:
            print("Nenhum resultado encontrado!")
            sleep(3)
    elif escolha == 4:
        os.system('cls')
        break

    else:
        print("Digite um comando valido!")