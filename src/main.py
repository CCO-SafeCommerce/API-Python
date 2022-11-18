import os
from psutil import cpu_percent, cpu_count, cpu_freq, virtual_memory, disk_usage, disk_io_counters, process_iter, net_connections, CONN_LISTEN
import platform
import geocoder
import chaves
import getmac
from getpass import getpass
from time import sleep
import requests
import json
import datetime
import database

TIPO_SLA = ""

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

    servidor_foi_cadastrado = database.cadastrar_servidor(modelo, so, mac_add, fk_empresa)

    if servidor_foi_cadastrado:
        parametros_definidos = database.definir_parametros_obrigatorios(mac_add)
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

def enviar_mensagem_slack(mensagem):
    #Variável que define o tipo de dados que estamos enviando. E que envie a solicitação e poste está mensagem
    payload = '{"text":"%s"}' % mensagem
    
    # Variável que irá obter reposta que iremos receber da API. Logo depois do sinal de igual tem a chamada da bilioteca de solicitaçao. 
    # E também o link do bot criado para o envio de mensagens
    requests.post('https://hooks.slack.com/services/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', data=payload)

def abrir_issue_jira():
    url = "https://safe-commercefr.atlassian.net/rest/api/2/issue"

    headers={
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload=json.dumps(
        {
        "fields": {
            "project":
            {
                "key": "SAF"
            },
            "summary": "Uso de CPU acima de 95%",
            "description": "A CPU desta maquina atingiu niveis elevados de uso, recomendamos fazer verificar o que está causando está lentidão.",
            "issuetype": {
                "name": "Task"
            }
        }
    }
    )
    response=requests.post(
        url,
        data=payload,
        headers=headers,
        auth=("pedrogustavofr000@gmail.com", "")
    )

    print(response.text)

def lidar_coleta_dados():
    monitorando = True
    dados = database.obter_dados_servidor(mac_add)

    if len(dados) == 0:
        return

    id_servidor = dados[0]
    ultimo_insert = dados[1]

    os.system(limpar)                
    while monitorando:
        try:
            parametros_coleta = database.obter_parametros_coleta(id_servidor)

            if len(parametros_coleta) == 0:
                print("Não há parametros de coleta")

            leituras = []

            for parametro in parametros_coleta:
                metrica = parametro[0]

                if metrica == 1:
                    # Porcentagem de uso da CPU (%)

                    valor_lido = cpu_percent(interval=0.5)
                    componente = "CPU"
                    situacao = 'n'

                    # verificar SLAs de alertas

                    leituras.append((id_servidor, metrica, valor_lido, situacao, componente))

                elif metrica == 2:
                    # Quatidade de CPU logica (vCPU)

                    valor_lido = cpu_count(logical=True)
                    componente = "vCPU"
                    situacao = 'n'
                    
                    # verificar SLAs de alertas

                    leituras.append((id_servidor, metrica, valor_lido, situacao, componente))
                
                elif metrica == 3:
                    # Porcentagem de uso da CPU por CPU (%)
                    # verificar SLAs de alertas

                    coleta = cpu_percent(interval=0.5, percpu=True)

                    for index in range(len(coleta)):
                        valor_lido = coleta[index]
                        componente = f"CPU {index + 1}"
                        situacao = 'n'
                        leituras.append((id_servidor, metrica, valor_lido, situacao, componente))

                elif metrica == 4:
                    # Frequência de uso da CPU (MHz)

                    valor_lido = cpu_freq().current
                    componente = "CPU"
                    situacao = 'n'
                    
                    # verificar SLAs de alertas

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

                    # verificar SLAs de alertas

                    leituras.append((id_servidor, metrica, valor_lido, situacao, componente))

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
                    
                    # verificar SLAs de alertas
                    
                    leituras.append((id_servidor, metrica, valor_lido, situacao, componente))

                elif metrica == 9:
                    # Lido pelo Disco (ms)

                    valor_lido = disk_io_counters().read_time
                    componente = "DISCO"
                    situacao = 'n'
                    leituras.append((id_servidor, metrica, valor_lido, situacao, componente))

                elif metrica == 10:
                    # Escrito pelo Disco (ms)

                    valor_lido = disk_io_counters().write_time
                    componente = "DISCO"
                    situacao = 'n'
                    leituras.append((id_servidor, metrica, valor_lido, situacao, componente))

                elif metrica == 11:
                    # Temperatura da CPU                    
                    temperaturaCPU = pegarTemperaturaServidor()
                    if(temperaturaCPU >= 65 and temperaturaCPU<75):
                        flag = "a" #alerta                        
                    elif(temperaturaCPU > 75):
                        flag = "e"    #emergencia
                    else:
                        flag = "n"
                    
                    valor_lido = temperaturaCPU
                    situacao = flag
                    componente = "TEMP CPU"
                    leituras.append((id_servidor, metrica, valor_lido, situacao, componente))


                elif metrica == 12:
                    # Processos
                    #Listagem de Processos
                    print('Processos')

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
                        
            horario = datetime.datetime.now()

            if ultimo_insert != None:
                diferenca_segundos = abs((horario - ultimo_insert).seconds)
            else:
                diferenca_segundos = 10

            if len(leituras) > 0 and (diferenca_segundos >= 10):
                horario_formatado = horario.strftime('%Y-%m-%d %X.%f')[:-5]

                ok = database.registrar_leituras(leituras, horario_formatado)

                if ok:
                    ultimo_insert = horario
                    print(f'Enviado para o banco às {horario_formatado}')
                else:
                    print(f'Falha ao enviar as leituras às {horario_formatado}')

            leituras.clear()
            print('Monitorando...')
            sleep(0.5)
            
        except KeyboardInterrupt:
            monitorando = False

def pegarTemperaturaCidade():
    API_KEY = chaves.API_KEY
    cidade = geocoder.ip("me")
    cidadeMid = str(cidade[0]).split(',')
    cidade = cidadeMid[0].replace("[","")
    link = f"https://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={API_KEY}&lang=pt_br"
    requisicao = requests.get(link)
    requisicao_dic = requisicao.json()
    temperaturaCidade = round(requisicao_dic['main']['temp'] - 273.15,2)
    print(temperaturaCidade)
    return temperaturaCidade

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