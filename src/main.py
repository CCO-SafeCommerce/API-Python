import os
from psutil import cpu_percent, cpu_count, cpu_freq, virtual_memory, disk_usage, disk_io_counters, process_iter, net_connections, CONN_LISTEN
import platform
import getmac
import mysql.connector
from getpass import getpass
import bcrypt
from dashing import HSplit, VSplit, Text
from time import sleep
import requests
import json
import datetime
import issue_notifier

HOST = "localhost"
USER = "aluno"
PASS = "sptech"
DB = "safecommerce"

SLA_AVISO = 120
SLA_EMERGENCIA = 60
TIPO_SLA = ""

if os.name == 'nt':
    limpar = "cls"
else:
    limpar = "clear"

def transformar_bytes_em_gigas(value):
    return value / 1024**3

def verificar_servidor_cadastrado():
    resultado = False

    global mac_add
    mac_add = getmac.get_mac_address()

    conexao = mysql.connector.connect(host=HOST, user=USER, password=PASS, database=DB)
    cursor = conexao.cursor()

    cursor.execute(f"select idServidor from Servidor where enderecoMac = '{mac_add}'")
    servidores_encontrados = cursor.fetchall()

    cursor.close()
    conexao.close()

    if len(servidores_encontrados) > 0:
        print("Servidor já está cadastrado e foi encontrado.")
        resultado = True
    else:
        print("Servidor não está cadastrado.")    

    return resultado

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
            conexao = mysql.connector.connect(host=HOST, user=USER, password=PASS, database=DB)
            cursor = conexao.cursor()

            cursor.execute(f"select email, senha, fkEmpresa from Usuario where email = '{email}'")
            usuarios = cursor.fetchall()

            cursor.close()
            conexao.close()           

            if len(usuarios) > 0:
                is_senha_correta = bcrypt.checkpw(senha.encode('UTF-8'), usuarios[0][1].encode('UTF-8'))

                if is_senha_correta:
                    global fk_empresa                    
                    fk_empresa = usuarios[0][2]
                    print("Login realizado com sucesso.")
                    resultado = True
                    deseja_continuar = False
                else:
                    print("Email e/ou Senha incorreto(s)!")
            else:
                print("Email e/ou Senha incorreto(s)!")
    
    return resultado

def cadastrar_servidor():
    servidor_foi_cadastrado = False

    print("Inicando cadastro do servidor")
    print("Informações:")
    print("\nEndereço MAC: {}".format(mac_add))

    so = platform.system()
    print("Sistema Operacional: {}".format(so))

    modelo = input("Modelo: ")

    conexao = mysql.connector.connect(host=HOST, user=USER, password=PASS, database=DB)
    cursor = conexao.cursor()

    cursor.execute(f"INSERT INTO Servidor (modelo, so, enderecoMac, fkEmpresa) VALUES ('{modelo}', '{so}', '{mac_add}', {fk_empresa})")
    conexao.commit()

    if cursor.rowcount == 0:
        print("ERRO: Falha ao cadastrar servidor")
        return servidor_foi_cadastrado
    else:
        cursor.execute(f"INSERT INTO Parametro VALUES ((SELECT idServidor FROM Servidor WHERE enderecoMac = '{mac_add}'), 2), ((SELECT idServidor FROM Servidor WHERE enderecoMac = '{mac_add}'), 5), ((SELECT idServidor FROM Servidor WHERE enderecoMac = '{mac_add}'), 7);")
        conexao.commit()

    servidor_foi_cadastrado = True

    cursor.close()
    conexao.close()

    print("Servidor cadastrado com sucesso!")
    return servidor_foi_cadastrado

def lidar_cadastrar_servidor():
    resultado = False

    print("CADASTRO DE SERVIDOR")
    print("Para cadastrar servidor é necessário realizar login")

    is_login_feito = login()

    if not is_login_feito:
        return resultado
    
    is_cadastro_finalizado = cadastrar_servidor()

    if is_cadastro_finalizado:
        resultado = True
        
    return resultado

def obter_dados_servidor():
    conexao = mysql.connector.connect(host=HOST, user=USER, password=PASS, database=DB)
    cursor = conexao.cursor()

    cursor.execute(f"SELECT idServidor, ultimoRegistro FROM visaoGeralServidores WHERE enderecoMac = '{mac_add}'")

    servidores = cursor.fetchall()

    cursor.close()
    conexao.close() 

    return {
        "idServidor": servidores[0][0],
        "ultimoRegistro": servidores[0][1]
    }

def obter_parametros_coleta(id_servidor):
    conexao = mysql.connector.connect(host=HOST, user=USER, password=PASS, database=DB)
    cursor = conexao.cursor()

    cursor.execute(f"SELECT fk_Metrica FROM Parametro WHERE fk_Servidor = {id_servidor}")

    parametros = cursor.fetchall()

    cursor.close()
    conexao.close() 

    return parametros

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
            "summary": "Uso de {TIPO_SLA} acima de 95%",
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

def obter_aplicacoes(id_servidor):
    conexao = mysql.connector.connect(host=HOST, user=USER, password=PASS, database=DB)
    cursor = conexao.cursor()

    cursor.execute(f"SELECT nome, porta FROM Aplicacao WHERE fkServidor = {id_servidor}")

    aplicacoes = cursor.fetchall()

    cursor.close()
    conexao.close() 

    return aplicacoes

def lidar_coleta_dados():
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

    monitorando = True
    dados = obter_dados_servidor()
    id_servidor = dados["idServidor"]
    ultimo_insert = dados["ultimoRegistro"]

    conexao = mysql.connector.connect(host=HOST, user=USER, password=PASS, database=DB)
    cursor = conexao.cursor()

    os.system(limpar)                
    while monitorando:
        try:
            #Textos CPU
            CPU_L = interface.items[0].items[0]
            CPU_L.text = ''            

            #Textos RAM
            RAM = interface.items[1].items[0]
            RAM.text = ''

            #Textos DISCO
            DISCO = interface.items[1].items[1]
            DISCO.text = ''

            PROCESSOS = interface.items[2].items[0]
            PROCESSOS.text = ''

            parametros_coleta = obter_parametros_coleta(id_servidor)

            leituras = []

            for parametro in parametros_coleta:
                metrica = parametro[0]

                if metrica == 1:
                    # Porcentagem de uso da CPU (%)

                    TIPO_SLA = "CPU"

                    valor_lido = cpu_percent(interval=0.5)
                    componente = "CPU"
                    situacao = 'n'
                    CPU_L.text += f'\nPorcentagem de uso: {valor_lido}%\n'

                    # if(valor_lido >= 85 and valor_lido < 95):
                    #     situacao = 'a'
                    #     enviar_mensagem_slack()
                    # elif(valor_lido > 95):
                    #     situacao = 'e'
                    #     abrir_issue_jira()

                    leituras.append((id_servidor, metrica, valor_lido, situacao, componente))

                elif metrica == 2:
                    # Quatidade de CPU logica (vCPU)

                    valor_lido = cpu_count(logical=True)
                    componente = "vCPU"
                    situacao = 'n'
                    CPU_L.text += f'\nQuantidade de CPU lógica: {valor_lido}\n'
                    leituras.append((id_servidor, metrica, valor_lido, situacao, componente))
                
                elif metrica == 3:
                    # Porcentagem de uso da CPU por CPU (%)

                    coleta = cpu_percent(interval=0.5, percpu=True)

                    for index in range(len(coleta)):
                        valor_lido = coleta[index]
                        componente = f"CPU {index + 1}"
                        situacao = 'n'
                        CPU_L.text += f'\nUso da {componente}: {valor_lido}%\n'
                        leituras.append((id_servidor, metrica, valor_lido, situacao, componente))

                elif metrica == 4:
                    # Frequência de uso da CPU (MHz)

                    valor_lido = cpu_freq().current
                    componente = "CPU"
                    situacao = 'n'
                    CPU_L.text += f'\nFrequência de uso da CPU: {valor_lido}MHz\n'
                    leituras.append((id_servidor, metrica, valor_lido, situacao, componente))

                elif metrica == 5:
                    # Total de Memoria Ram (GB)

                    valor_lido_bruto = virtual_memory().total
                    valor_lido = transformar_bytes_em_gigas(valor_lido_bruto)
                    componente = "RAM"
                    situacao = 'n'
                    RAM.text += f'\nTotal de memória RAM: {round(valor_lido)} GB\n'
                    leituras.append((id_servidor, metrica, valor_lido, situacao, componente))

                elif metrica == 6: 
                    # Porcentagem de uso da Memoria Ram (%)

                    TIPO_SLA = "RAM"

                    valor_lido = virtual_memory().percent
                    componente = "RAM"
                    situacao = 'n'
                    RAM.text += f'\nTotal de uso de memória RAM: {valor_lido}%\n'
                    leituras.append((id_servidor, metrica, valor_lido, situacao, componente))

                    # if(cpu_percent >= 85 and cpu_percent < 95):
                    #     enviar_mensagem_slack()
                    # elif(cpu_percent > 95):
                    #     abrir_issue_jira()

                elif metrica == 7:
                    # Total de Disco (GB)

                    valor_lido_bruto = disk_usage('/').total
                    valor_lido = transformar_bytes_em_gigas(valor_lido_bruto)
                    componente = "DISCO"
                    situacao = 'n'
                    DISCO.text += f'\nTotal de Disco: {round(valor_lido)} GB\n'
                    leituras.append((id_servidor, metrica, valor_lido, situacao, componente))

                elif metrica == 8:
                    # Porcentagem de uso de Disco (%)

                    TIPO_SLA = "DISCO"

                    valor_lido_bruto = disk_usage('/').percent
                    componente = "DISCO"
                    situacao = 'n'
                    DISCO.text += f'\nTotal de uso de Disco: {valor_lido}%\n'
                    leituras.append((id_servidor, metrica, valor_lido, situacao, componente))

                    # if(cpu_percent >= 85 and cpu_percent < 95):
                    #     enviar_mensagem_slack()
                    # elif(cpu_percent > 95):
                    #     abrir_issue_jira()

                elif metrica == 9:
                    # Lido pelo Disco (ms)

                    valor_lido = disk_io_counters().read_time
                    componente = "DISCO"
                    situacao = 'n'
                    DISCO.text += f'\nTotal Lido Pelo Disco: {valor_lido} ms\n'
                    leituras.append((id_servidor, metrica, valor_lido, situacao, componente))

                elif metrica == 10:
                    # Escrito pelo Disco (ms)

                    valor_lido = disk_io_counters().write_time
                    componente = "DISCO"
                    situacao = 'n'
                    DISCO.text += f'\nTotal Escrito Pelo Disco: {valor_lido} ms'
                    leituras.append((id_servidor, metrica, valor_lido, situacao, componente))

                elif metrica == 11:
                    # Temperatura da CPU
                    print('TÁ PEGANDO FOGO BICHO')

                elif metrica == 12:
                    # Processos

                    #Listagem de Processos
                    cont = 0                
                    for proc in process_iter(['pid', 'name', 'username']):
                        if cont < 5:
                            PROCESSOS.text += f'\nNome: {proc.name()}   Pid: {proc.pid} \n'

                        cont += 1

                elif metrica == 13:
                    # Conexões ativas TCP
                    aplicacoes = obter_aplicacoes(id_servidor)
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
            diferenca_segundos = abs((horario - ultimo_insert).seconds)

            if len(leituras) > 0 and (diferenca_segundos >= 10):
                horario_formatado = horario.strftime('%Y-%m-%d %X.%f')[:-5]

                cursor.executemany("INSERT INTO Leitura VALUES (%s, %s, '" + horario_formatado +"', %s, %s, %s)", leituras)
                conexao.commit()

                ultimo_insert = horario
                print(f'Enviado para o banco às {horario_formatado}')

                leituras.clear()

            # interface.display()
            print('Monitorando...')
            sleep(0.5)
            
        except KeyboardInterrupt:
            monitorando = False
    
    cursor.close()
    conexao.close()

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