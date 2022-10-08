import os
import platform
import getmac
import mysql.connector
from getpass import getpass
import bcrypt
from dashing import HSplit, VSplit, VGauge, HGauge, Text
import psutil
from time import sleep
import requests

HOST = "localhost"
USER = "aluno"
PASS = "sptech"
DB = "safecommerce"

SLA_AVISO = 120
SLA_EMERGENCIA = 60

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

    conexao = mysql.connector.connect(host="localhost", user="aluno", password="sptech", database="safecommerce")
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
                    print("Login realizado com sucesso.")
                    resultado = True
                    deseja_continuar = False

                    global fk_empresa                    
                    fk_empresa = usuarios[0][2]

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

    cursor.execute(f"INSERT INTO Servidor VALUES (null, '{modelo}', '{so}', '{mac_add}', {fk_empresa})")
    conexao.commit()

    if cursor.rowcount == 0:
        print("ERRO: Falha ao cadastrar servidor")
        return servidor_foi_cadastrado

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

def obter_id_servidor():
    conexao = mysql.connector.connect(host=HOST, user=USER, password=PASS, database=DB)
    cursor = conexao.cursor()

    cursor.execute(f"SELECT idServidor FROM Servidor WHERE enderecoMac = '{mac_add}'")

    servidores = cursor.fetchall()

    cursor.close()
    conexao.close() 

    return servidores[0][0]

def obter_parametros_coleta(id_servidor):
    conexao = mysql.connector.connect(host=HOST, user=USER, password=PASS, database=DB)
    cursor = conexao.cursor()

    cursor.execute(f"SELECT fkMetrica FROM Parametro WHERE fkServidor = {id_servidor}")

    parametros = cursor.fetchall()

    cursor.close()
    conexao.close() 

    return parametros

def enviar_mensagem_slack(mensagem):
    #Variável que define o tipo de dados que estamos enviando. E que envie a solicitação e poste está mensagem
    payload = '{"text":"%s"}' % mensagem
    
    # Variável que irá obter reposta que iremos receber da API. Logo depois do sinal de igual tem a chamada da bilioteca de solicitaçao. 
    # E também o link do bot criado para o envio de mensagens
    resposta = requests.post('https://hooks.slack.com/services/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', data=payload)

def lidar_coleta_dados():
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

    monitorando = True
    controle_insert = 0
    id_servidor = obter_id_servidor()

    conexao = mysql.connector.connect(host=HOST, user=USER, password=PASS, database=DB)
    cursor = conexao.cursor()

    while monitorando:
        try:
            print("Monitorando...")
            parametros_coleta = obter_parametros_coleta(id_servidor)

            leituras = []

            for parametro in parametros_coleta:
                metrica = parametro[0]

                if metrica == 1:
                    # Porcentagem de uso da CPU (%)

                    valor_lido = psutil.cpu_percent(interval=0.5)
                    componente = "CPU"
                    leituras.append((id_servidor, metrica, valor_lido, componente))

                elif metrica == 2:
                    # Quatidade de CPU logica (vCPU)

                    valor_lido = psutil.cpu_count(logical=True)
                    componente = "vCPU"
                    leituras.append((id_servidor, metrica, valor_lido, componente))
                
                elif metrica == 3:
                    # Porcentagem de uso da CPU por CPU (%)

                    coleta = psutil.cpu_percent(interval=0.5, percpu=True)

                    for index in range(len(coleta)):
                        valor_lido = coleta[index]
                        componente = f"CPU {index + 1}"
                        leituras.append((id_servidor, metrica, valor_lido, componente))

                elif metrica == 4:
                    # Frequência de uso da CPU (MHz)

                    valor_lido = psutil.cpu_freq().current
                    componente = "CPU"
                    leituras.append((id_servidor, metrica, valor_lido, componente))

                elif metrica == 5:
                    # Total de Memoria Ram (GB)

                    valor_lido_bruto = psutil.virtual_memory().total
                    valor_lido = transformar_bytes_em_gigas(valor_lido_bruto)
                    componente = "RAM"
                    leituras.append((id_servidor, metrica, valor_lido, componente))

                elif metrica == 6: 
                    # Porcentagem de uso da Memoria Ram (%)

                    valor_lido = psutil.virtual_memory().percent
                    componente = "RAM"
                    leituras.append((id_servidor, metrica, valor_lido, componente))

                elif metrica == 7:
                    # Total de Disco (TB)

                    valor_lido_bruto = psutil.disk_usage('/').total
                    valor_lido = transformar_bytes_em_gigas(valor_lido_bruto)
                    componente = "DISCO"
                    leituras.append((id_servidor, metrica, valor_lido, componente))

                elif metrica == 8:
                    # Porcentagem de uso de Disco (%)

                    valor_lido_bruto = psutil.disk_usage('/').percent
                    componente = "DISCO"
                    leituras.append((id_servidor, metrica, valor_lido, componente))

                elif metrica == 9:
                    # Lido pelo Disco (ms)

                    valor_lido_bruto = psutil.disk_io_counters('/').read_time
                    componente = "DISCO"
                    leituras.append((id_servidor, metrica, valor_lido, componente))

                elif metrica == 10:
                    # Escrito pelo Disco (ms)

                    valor_lido_bruto = psutil.disk_io_counters('/').write_time
                    componente = "DISCO"
                    leituras.append((id_servidor, metrica, valor_lido, componente))

            if len(leituras) > 0 and controle_insert % 10 == 0:
                cursor.executemany("INSERT INTO Leitura VALUES (%s, %s, now(), %s, %s)", leituras)
                conexao.commit()

                leituras.clear()

            controle_insert += 1
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