import os
from psutil import cpu_percent, cpu_count, cpu_freq, virtual_memory, disk_usage, disk_io_counters, process_iter, net_connections, CONN_LISTEN
import platform
import getmac
from getpass import getpass
from time import sleep
import requests
import datetime
import pytz
import database
import notifier
import requests

if os.name == 'nt':
    limpar = "cls"
else:
    limpar = "clear"

def transformar_bytes_em_gigas(value):
    return value / 1024**3

def verificar_servidor_cadastrado():
    global mac_add
    mac_add = getmac.get_mac_address()

    servidor_cadastrado = database.is_servidor_cadastrado(mac_add)

    if servidor_cadastrado:
        print('Servidor já está cadastrado e foi encontrado.')
    else:
        print('Servidor não está cadastrado')

    return servidor_cadastrado

def encerrarProcessos(id_servidor):
    pids = database.capturarPids(id_servidor)
    if os.name == "nt":
        for pid in pids:
            os.system('taskkill /PID ' + str(pid[0])+" /F")
            database.deletarPids(id_servidor, pid[0])
    else:
        for pid in pids:
            os.system('kill '+str(pid[0]))
            database.deletarPids(id_servidor, pid[0])


def login():
    resultado = False
    deseja_continuar = True

    while deseja_continuar:
        print("Login - Informe email e senha vazios caso deseje cancelar o login.")
        print("Email:")
        email = input()
        print("Senha:")
        senha = getpass(prompt="")

        if email == "" and senha == "":
            print("Email e Senha vazios. Consideramos que você não deseja se logar.")
            deseja_continuar = False
        else:
            global fk_empresa
            fk_empresa = database.obter_fk_empresa_via_login(email, senha)

            if fk_empresa == 0:
                print("Email e/ou Senha incorreto(s)!")
            else:
                print("Login realizado com sucesso.")
                resultado = True
                deseja_continuar = False

    return resultado

def cadastrar_servidor():
    servidor_foi_cadastrado = False

    print("Inicando cadastro do servidor")
    print("Informações:")
    print("\nEndereço MAC: {}".format(mac_add))

    so = platform.system()
    print("Sistema Operacional: {}".format(so))

    modelo = input("Modelo: ")
    response = requests.get('https://api64.ipify.org?format=json').json()    
    ip = response["ip"]
    
    servidor_foi_cadastrado = database.cadastrar_servidor(
        modelo, so, mac_add, fk_empresa, ip)

    if servidor_foi_cadastrado:
        parametros_definidos = database.definir_parametros_obrigatorios(
            mac_add)
        if parametros_definidos:
            print("Servidor cadastrado com sucesso!")

        else:
            print("ERRO: Falha ao definir os parametros")
    else:
        print("ERRO: Falha ao cadastrar servidor")

    return servidor_foi_cadastrado

def lidar_cadastrar_servidor():
    print("CADASTRO DE SERVIDOR")
    print("Para cadastrar servidor é necessário realizar login")

    is_login_feito = login()

    if not is_login_feito:
        return is_login_feito

    is_cadastro_finalizado = cadastrar_servidor()

    return is_cadastro_finalizado

def pegarTemperaturaServidor():
    temperaturaCPU = 0
    if platform.system() == 'Windows':
        import wmi
        w = wmi.WMI(namespace="root\OpenHardwareMonitor")
        temperature_infos = w.Sensor()
        for sensor in temperature_infos:
            if sensor.SensorType==u'Temperature':
                print(sensor.Name)
                print(sensor.Value)
                temperaturaCPU = sensor.Value
    else:
        import psutil
        temperaturas = psutil.sensors_temperatures()
        temperaturaCPU = temperaturas['coretemp'][0][1]
       
    return temperaturaCPU

def lidar_coleta_dados():
    monitorando = True
    dados = database.obter_dados_servidor(mac_add)

    if len(dados) == 0:
        return

    id_servidor = dados[0]
    ultimo_insert = dados[1]
    modelo = dados[2]

    os.system(limpar)                
    while monitorando:
        try:
            parametros_coleta = database.obter_parametros_coleta(id_servidor)

            if len(parametros_coleta) == 0:
                print("Não há parametros de coleta")

            leituras = []
            processos = []

            for parametro in parametros_coleta:
                metrica = parametro[0]

                if metrica == 1:
                    # Porcentagem de uso da CPU (%)

                    valor_lido = cpu_percent(interval=0.5)
                    componente = "CPU"
                    situacao = 'n'                    

                    mensagem = "O uso de CPU do servidor de modelo {} e endereço mac {} atingiu niveis de uso de {}%. Por favor verifique o que está ocasinando este nivel de uso antes que a situação do componente se agrave.".format(modelo, mac_add, valor_lido)
                    summary = "CPU acima de 95 de uso"
                    description = "O uso de CPU do servidor de modelo {} e endereço mac {} atingiu niveis de uso de {}%. Recomendamos uma verificação do motivo deste nivel de uso elevado.".format(modelo, mac_add, valor_lido)

                    if(valor_lido >= 85 and valor_lido < 95):
                        situacao = 'a'
                        notifier.enviar_mensagem_slack(mensagem)
                        
                    elif(valor_lido >= 95):
                        situacao = 'e'
                        notifier.create_issue(summary, description)
                        notifier.enviar_mensagem_slack(mensagem)

                    leituras.append((id_servidor, metrica, valor_lido, situacao, componente))

                elif metrica == 2:
                    # Quatidade de CPU logica (vCPU)

                    valor_lido = cpu_count(logical=True)
                    componente = "vCPU"
                    situacao = 'n'                   
                    leituras.append((id_servidor, metrica, valor_lido, situacao, componente))
                
                elif metrica == 3:
                    # Porcentagem de uso da CPU por CPU (%)

                    coleta = cpu_percent(interval=0.5, percpu=True)

                    qtd_acima_a = 0
                    qtd_acima_e = 0

                    for index in range(len(coleta)):                        
                        valor_lido = coleta[index]
                        componente = f"CPU {index + 1}"
                        situacao = 'n'

                        if(valor_lido >= 85 and valor_lido < 95):
                            situacao = 'a'
                            qtd_acima_a = qtd_acima_a + 1
                        elif(valor_lido >= 95):
                            situacao = 'e'
                            qtd_acima_e = qtd_acima_e + 1

                        leituras.append((id_servidor, metrica, valor_lido, situacao, componente))

                        # verificar SLAs de alertas

                    summary = "Mais de 75% das CPUs acima de 95 de uso"
                    description = "Mais de 75% das CPUs do servidor de modelo {} e endereço mac {} atingiu elevados niveis de uso. Recomendamos uma verificação do motivo deste nivel de uso elevado.".format(modelo, mac_add)
                    mensagem = "Mais de 75% das CPUs do servidor de modelo {} e endereço mac {} atingiram elevados niveis de uso de 85%. Por favor verifique o que está ocasinando este nivel de uso antes que a situação do componente se agrave.".format(modelo, mac_add)


                    if (qtd_acima_e + qtd_acima_a)/len(coleta) >= 0.75:
                        notifier.enviar_mensagem_slack(mensagem)

                        if qtd_acima_e > qtd_acima_a:
                            notifier.create_issue(summary, description)

                elif metrica == 4:
                    # Frequência de uso da CPU (MHz)

                    coleta = cpu_freq()
                    valor_lido = coleta.current
                    componente = "CPU"
                    situacao = 'n'

                    leituras.append((id_servidor, metrica, valor_lido, situacao, componente))

                elif metrica == 5:
                    # Total de Memoria Ram (GB)

                    valor_lido_bruto = virtual_memory().total
                    valor_lido = transformar_bytes_em_gigas(valor_lido_bruto)
                    componente = "RAM"
                    situacao = 'n'                    
                    leituras.append((id_servidor, metrica, valor_lido, situacao, componente))

                elif metrica == 6: 
                    # Porcentagem de uso da Memoria Ram (%)

                    valor_lido = virtual_memory().percent
                    componente = "RAM"
                    situacao = 'n'
                    leituras.append((id_servidor, metrica, valor_lido, situacao, componente))

                    summary = "Uso de memória RAM em %s%".format(valor_lido)
                    description = "A memória RAM do servidor de modelo {} e endereço mac {} atingiu um uso de {}%. Recomendamos uma verificação do motivo deste nivel de uso elevado.".format(modelo, mac_add, valor_lido)
                    mensagem = "A memória RAM do servidor de modelo {} e endereço mac {} atingiram elevados niveis de uso acima de 85%. Por favor verifique o que está ocasinando este nivel de uso antes que a situação do componente se agrave.".format(modelo, mac_add)

                    if(valor_lido >= 85 and valor_lido < 95):
                        situacao = "a"
                        notifier.enviar_mensagem_slack(mensagem)

                    elif(valor_lido >= 95):
                        situacao = "e"
                        notifier.enviar_mensagem_slack(summary, description)
                        notifier.create_issue(mensagem)

                elif metrica == 7:
                    # Total de Disco (GB)

                    valor_lido_bruto = disk_usage('/').total
                    valor_lido = transformar_bytes_em_gigas(valor_lido_bruto)
                    componente = "DISCO"
                    situacao = 'n'
                    leituras.append((id_servidor, metrica, valor_lido, situacao, componente))

                elif metrica == 8:
                    # Porcentagem de uso de Disco (%)

                    valor_lido_bruto = disk_usage('/').percent
                    componente = "DISCO"
                    situacao = 'n'
                    leituras.append((id_servidor, metrica, valor_lido, situacao, componente))

                    summary = "Uso de memória em DISCO atingiu uso de {}%".format(valor_lido)
                    description = "A memória em DISCO do servidor de modelo {} e endereço mac {} atingiu um uso de {}%. Recomendamos uma verificação do motivo deste nivel de uso elevado.".format(modelo, mac_add, valor_lido)
                    mensagem = "A memória em DISCO do servidor de modelo {} e endereço mac {} atingiram elevados niveis de uso acima de 85%. Por favor verifique o que está ocasinando este nivel de uso antes que a situação do componente se agrave.".format(modelo, mac_add)

                    if(valor_lido >= 85 and valor_lido < 95):
                        situacao = "a"
                        notifier.enviar_mensagem_slack(mensagem)

                    elif(valor_lido >= 95):
                        situacao = "e"
                        notifier.enviar_mensagem_slack(mensagem)
                        notifier.create_issue(summary,description)

                elif metrica == 9:
                    # Lido pelo Disco (ms)

                    valor_lido = disk_io_counters().read_bytes
                    componente = "DISCO"
                    situacao = 'n'
                    leituras.append((id_servidor, metrica, valor_lido, situacao, componente))

                elif metrica == 10:
                    # Escrito pelo Disco (ms)

                    valor_lido = disk_io_counters().write_bytes
                    componente = "DISCO"
                    situacao = 'n'
                    leituras.append((id_servidor, metrica, valor_lido, situacao, componente))

                elif metrica == 11:
                    # Temperatura da CPU
                    temperaturaCPU = pegarTemperaturaServidor()

                    valor_lido = temperaturaCPU
                    situacao = 'n'
                    componente = "TEMP CPU"

                    if (temperaturaCPU >= 65 and temperaturaCPU < 75):
                        situacao = "a"  # alerta
                    elif (temperaturaCPU >= 75):
                        situacao = "e"  # emergencia

                    leituras.append(
                        (id_servidor, metrica, valor_lido, situacao, componente))

                elif metrica == 12:
                    encerrarProcessos(id_servidor)
                    useCpu = 0
                    memoryRam = 0
                    nomes = []
                    situacaoCpu = 'n'
                    situacaoRam = 'n'
                    i = 0
                    while i < 5:
                        for proc in process_iter(['pid', 'name', 'username']):
                            if proc.pid != 0 and proc.name != 'Idle' and proc.name() != 'System' and nomes.__contains__(proc.name()) == False:
                                useCpu = proc.cpu_percent()
                                memoryRam = proc.memory_percent()
                                if useCpu > 0:
                                    nomes.append(proc.name())
                                    if useCpu > 70 and useCpu < 90:
                                        situacaoCpu = 'a'
                                    elif useCpu >= 90:
                                        situacaoCpu = 'e'
                                    if memoryRam > 75 and memoryRam < 85:
                                        situacaoRam = 'a'
                                    elif memoryRam >= 85:
                                        situacaoRam = 'e'
                                    processos.append(( id_servidor, proc.pid, proc.name(), useCpu, situacaoCpu, memoryRam, situacaoRam))
                                
                        i+=1         
                                                          
                elif metrica == 13:
                    # Conexões ativas TCP
                    aplicacoes = database.obter_aplicacoes(id_servidor)
                    network = net_connections(kind='inet')

                    for app in aplicacoes:
                        valor_lido = 0
                        situacao = 'n'
                        componente = f'{app[0]}:{app[1]}'

                        raddrs = set()
                        already_listen = False

                        for conn in network:
                            raddr = ''
                            if (len(conn.raddr) > 2):
                                raddr = f'{conn.raddr.ip}:{conn.raddr.port}'

                            if (
                                conn.laddr.port == app[1]  
                                and (conn.status != CONN_LISTEN 
                                    or (conn.status == CONN_LISTEN 
                                    and not already_listen)) 
                                and raddrs.issuperset(set(raddr))                               
                            ):
                                if (raddr != ''):
                                    raddrs.add(raddr)

                                if (conn.status == CONN_LISTEN):
                                    already_listen = True
                                
                                valor_lido += 1   

                        if (valor_lido == 0):
                            situacao = 'a'

                        leituras.append((id_servidor, metrica, valor_lido, situacao, componente))  

                elif metrica == 14:
                    processos_desejaveis = database.obter_processos_desejaveis(id_servidor)
                    nomes = []
                    x = 0
                    i = 0
                    while i < 5:
                        for proc in process_iter(['pid', 'name', 'username']):
                            if proc.pid != 0 and proc.name != 'Idle' and proc.name() != 'System' and nomes.__contains__(proc.name()) == False:
                                for x in range(len(processos_desejaveis)):
                                    if(proc.name == processos_desejaveis[x]):
                                        print("oi") 
      
            horario = datetime.datetime.now(pytz.utc)
            horario = horario.replace(tzinfo=None)

            if ultimo_insert != None:
                diferenca_segundos = abs((horario - ultimo_insert).seconds)
            else:
                diferenca_segundos = 10

            if len(leituras) > 0  and (diferenca_segundos >= 10):
                horario_formatado = horario.strftime('%Y-%m-%d %X.%f')[:-5]

                ok = database.registrar_leituras(leituras, horario_formatado, processos)

                if ok:
                    ultimo_insert = horario
                    print(f'Leituras enviadas às {horario_formatado}')

            leituras.clear()
            processos.clear()
            print('Monitorando...')
            sleep(0.5)
          
        except KeyboardInterrupt:
            monitorando = False

def main():
    print("SafeCommerce - API Coleta de Dados\n")

    print("Verificando se servidor está cadastrado..")
    is_servidor_cadastrado = verificar_servidor_cadastrado()

    if not is_servidor_cadastrado:
        is_servidor_cadastrado = lidar_cadastrar_servidor()

    if is_servidor_cadastrado:
        print("Servidor identificado e validado, preparando coleta de dados...")
        lidar_coleta_dados()
    else:
        print("Servidor precisa estar cadastrado para que haja monitoramento.")

    print("Obrigado por utilizar nossos serviços!")

if __name__ == "__main__":
    main()