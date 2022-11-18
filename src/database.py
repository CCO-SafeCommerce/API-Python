import pymssql
import mysql.connector
import bcrypt

AMBIENTE="producao"

HOST_MYSQL = "localhost"
USER_MYSQL = "root"
PASS_MYSQL = "Vitor@2003"
DB = "safecommerce"

HOST_MSSQL = "safecommerce.database.windows.net"
USER_MSSQL = "adm-safecommerce"
PASS_MSSQL = "1cco#grupo4"

def is_servidor_cadastrado(mac_add):
    resultado = False

    if AMBIENTE == "producao":
        with pymssql.connect(server=HOST_MSSQL, user=USER_MSSQL, password=PASS_MSSQL, database=DB) as conexao_ms:
            with conexao_ms.cursor() as cursor_ms:                
                cursor_ms.execute(f"select idServidor from Servidor where enderecoMac = '{mac_add}'")
                servidores_encontrados = cursor_ms.fetchall()

                if len(servidores_encontrados) > 0:
                    resultado = True

    if not resultado:
        with mysql.connector.connect(host=HOST_MYSQL, user=USER_MYSQL, password=PASS_MYSQL, database=DB) as conexao_my:
            with conexao_my.cursor() as cursor_my:
                cursor_my.execute(f"select idServidor from Servidor where enderecoMac = '{mac_add}'")
                servidores_encontrados = cursor_my.fetchall()

                if len(servidores_encontrados) > 0:
                    resultado = True
        
    return resultado

def obter_fk_empresa_via_login(email, senha):
    usuarios = []
    fk_empresa = 0

    if AMBIENTE == "producao":
        with pymssql.connect(server=HOST_MSSQL, user=USER_MSSQL, password=PASS_MSSQL, database=DB) as conexao_ms:
            with conexao_ms.cursor() as cursor_ms:
                cursor_ms.execute(f"select email, senha, fkEmpresa from Usuario where email = '{email}'")
                usuarios = cursor_ms.fetchall()

    if len(usuarios) == 0:
        with mysql.connector.connect(host=HOST_MYSQL, user=USER_MYSQL, password=PASS_MYSQL, database=DB) as conexao_my:
            with conexao_my.cursor() as cursor_my:
                cursor_my.execute(f"select email, senha, fkEmpresa from Usuario where email = '{email}'")
                usuarios = cursor_my.fetchall()

    if len(usuarios) > 0:
        is_senha_correta = bcrypt.checkpw(senha.encode('UTF-8'), usuarios[0][1].encode('UTF-8'))

        if is_senha_correta:
            fk_empresa = usuarios[0][2]

    return fk_empresa

def cadastrar_servidor(modelo, so, mac_add, fk_empresa):
    resultado_ms = False
    resultado_my = False

    if AMBIENTE == "producao":
        with pymssql.connect(server=HOST_MSSQL, user=USER_MSSQL, password=PASS_MSSQL, database=DB) as conexao_ms:
            with conexao_ms.cursor() as cursor_ms:
                cursor_ms.execute(f"INSERT INTO Servidor (modelo, so, enderecoMac, fkEmpresa) VALUES ('{modelo}', '{so}', '{mac_add}', {fk_empresa})")
                cursor_ms.commit()

                if cursor_ms.rowcount > 0:
                    resultado_ms = True

    with mysql.connector.connect(host=HOST_MYSQL, user=USER_MYSQL, password=PASS_MYSQL, database=DB) as conexao_my:
        with conexao_my.cursor() as cursor_my:
            cursor_my.execute(f"INSERT INTO Servidor (modelo, so, enderecoMac, fkEmpresa) VALUES ('{modelo}', '{so}', '{mac_add}', {fk_empresa})")
            cursor_my.commit()

            if cursor_my.rowcount > 0:
                resultado_my = True

    return resultado_my or resultado_ms

def definir_parametros_obrigatorios(mac_add):
    resultado_ms = False
    resultado_my = False

    if AMBIENTE == "producao":
        with pymssql.connect(server=HOST_MSSQL, user=USER_MSSQL, password=PASS_MSSQL, database=DB) as conexao_ms:
            with conexao_ms.cursor() as cursor_ms:
                cursor_ms.execute(f"INSERT INTO Parametro VALUES ((SELECT idServidor FROM Servidor WHERE enderecoMac = '{mac_add}'), 2), ((SELECT idServidor FROM Servidor WHERE enderecoMac = '{mac_add}'), 5), ((SELECT idServidor FROM Servidor WHERE enderecoMac = '{mac_add}'), 7), ((SELECT idServidor FROM Servidor WHERE enderecoMac = '{mac_add}'), 12);")
                cursor_ms.commit()

                if cursor_ms.rowcount > 0:
                    resultado_ms = True

    with mysql.connector.connect(host=HOST_MYSQL, user=USER_MYSQL, password=PASS_MYSQL, database=DB) as conexao_my:
        with conexao_my.cursor() as cursor_my:
            cursor_my.execute(f"INSERT INTO Parametro VALUES ((SELECT idServidor FROM Servidor WHERE enderecoMac = '{mac_add}'), 2), ((SELECT idServidor FROM Servidor WHERE enderecoMac = '{mac_add}'), 5), ((SELECT idServidor FROM Servidor WHERE enderecoMac = '{mac_add}'), 7), ((SELECT idServidor FROM Servidor WHERE enderecoMac = '{mac_add}'), 12);")
            cursor_my.commit()

            if cursor_my.rowcount > 0:
                resultado_my = True

    return resultado_my or resultado_ms

def obter_dados_servidor(mac_add):
    resultado = []

    if AMBIENTE == 'producao':
        with pymssql.connect(server=HOST_MSSQL, user=USER_MSSQL, password=PASS_MSSQL, database=DB) as conexao_ms:
            with conexao_ms.cursor() as cursor_ms:                
                cursor_ms.execute(f"SELECT idServidor, ultimoRegistro FROM visaoGeralServidores WHERE enderecoMac = '{mac_add}'")
                servidores = cursor_ms.fetchall()

                resultado.append(servidores[0][0], servidores[0][1])

    if len(resultado) == 0:
        with mysql.connector.connect(host=HOST_MYSQL, user=USER_MYSQL, password=PASS_MYSQL, database=DB) as conexao_my:
            with conexao_my.cursor() as cursor_my:
                cursor_my.execute(f"SELECT idServidor, ultimoRegistro FROM visaoGeralServidores WHERE enderecoMac = '{mac_add}'")
                servidores = cursor_my.fetchall()

                resultado.append(servidores[0][0], servidores[0][1])

    return resultado

def obter_parametros_coleta(id_servidor):
    parametros = []

    if AMBIENTE == "producao":
        with pymssql.connect(server=HOST_MSSQL, user=USER_MSSQL, password=PASS_MSSQL, database=DB) as conexao_ms:
            with conexao_ms.cursor() as cursor_ms:
                cursor_ms.execute(f'select fk_metricas from parametro where fk_servidor = {id_servidor}')
                parametros = cursor_ms.fetchall()

    if len(parametros) == 0:
        with  mysql.connector.connect(host=HOST_MYSQL, user=USER_MYSQL, password=PASS_MYSQL, database=DB) as conexao_my:
            with conexao_my.cursor() as cursor_my:
                cursor_my.execute(f'select fk_metricas from parametro where fk_servidor = {id_servidor}')
                parametros = cursor_my.fetchall()

    return parametros

def obter_aplicacoes(id_servidor):
    aplicacoes = []

    if AMBIENTE == 'producao':
        with pymssql.connect(server=HOST_MSSQL, user=USER_MSSQL, password=PASS_MSSQL, database=DB) as conexao_ms:
            with conexao_ms.cursor() as cursor_ms:                
                cursor_ms.execute(f"SELECT nome, porta FROM Aplicacao WHERE fkServidor = {id_servidor}")
                aplicacoes = cursor_ms.fetchall()

    if len(aplicacoes) == 0:
        with mysql.connector.connect(host=HOST_MYSQL, user=USER_MYSQL, password=PASS_MYSQL, database=DB) as conexao_my:
            with conexao_my.cursor() as cursor_my:
                cursor_my.execute(f"SELECT nome, porta FROM Aplicacao WHERE fkServidor = {id_servidor}")
                aplicacoes = cursor_my.fetchall()

    return aplicacoes

def registrar_leituras(leituras, horario_formatado):
    resultado_ms = False
    resultado_my = False

    if AMBIENTE == 'producao':
        with pymssql.connect(server=HOST_MSSQL, user=USER_MSSQL, password=PASS_MSSQL, database=DB) as conexao_ms:
            with conexao_ms.cursor() as cursor_ms:                
                cursor_ms.executemany("INSERT INTO Leitura VALUES (%s, %s, '" + horario_formatado +"', %s, %s, %s)", leituras)
                conexao_ms.commit()

                if cursor_ms.rowcount > 0:
                    resultado_ms = True

    with mysql.connector.connect(host=HOST_MYSQL, user=USER_MYSQL, password=PASS_MYSQL, database=DB) as conexao_my:
        with conexao_my.cursor() as cursor_my:
            cursor_my.executemany("INSERT INTO Leitura VALUES (%s, %s, '" + horario_formatado +"', %s, %s, %s)", leituras)
            conexao_my.commit()

            if cursor_my.rowcount > 0:
                resultado_my = True

    return resultado_my or resultado_ms
