import pymssql
import mysql.connector
import bcrypt

AMBIENTE = "desenvolvimento"
DATABASE = "safecommmerce"

HOST_MYSQL = "localhost"
USER_MYSQL = "aluno"
PASS_MYSQL = "sptech"

HOST_MSSQL = "grupo0-1cco.database.windows.net"
USER_MSSQL = "grupo01cco"
PASS_MSSQL = "1cco#grupo4"

def is_servidor_cadastrado(mac_add):
    resultado = False

    if AMBIENTE == "producao":
        with pymssql.connect(server=HOST_MSSQL, user=USER_MSSQL, password=PASS_MSSQL, database=DATABASE) as conexao_ms:
            with conexao_ms.cursor() as cursor_ms:                
                cursor_ms.execute(f"select idServidor from Servidor where enderecoMac = '{mac_add}'")
                servidores_encontrados = cursor_ms.fetchall()

                if len(servidores_encontrados) > 0:
                    resultado = True

    if not resultado:
        with mysql.connector.connect(host=HOST_MYSQL, user=USER_MYSQL, password=PASS_MYSQL, database=DATABASE) as conexao_my:
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
        with pymssql.connect(server=HOST_MSSQL, user=USER_MSSQL, password=PASS_MSSQL, database=DATABASE) as conexao_ms:
            with conexao_ms.cursor() as cursor_ms:
                cursor_ms.execute(f"select email, senha, fkEmpresa from Usuario where email = '{email}'")
                usuarios = cursor_ms.fetchall()

    if len(usuarios) == 0:
        with mysql.connector.connect(host=HOST_MYSQL, user=USER_MYSQL, password=PASS_MYSQL, database=DATABASE) as conexao_my:
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
        with pymssql.connect(server=HOST_MSSQL, user=USER_MSSQL, password=PASS_MSSQL, database=DATABASE) as conexao_ms:
            with conexao_ms.cursor() as cursor_ms:
                cursor_ms.execute(f"INSERT INTO Servidor (modelo, so, enderecoMac, fkEmpresa) VALUES ('{modelo}', '{so}', '{mac_add}', {fk_empresa})")
                conexao_ms.commit()

                if cursor_ms.rowcount > 0:
                    resultado_ms = True

    with mysql.connector.connect(host=HOST_MYSQL, user=USER_MYSQL, password=PASS_MYSQL, database=DATABASE) as conexao_my:
        with conexao_my.cursor() as cursor_my:
            cursor_my.execute(f"INSERT INTO Servidor (modelo, so, enderecoMac, fkEmpresa) VALUES ('{modelo}', '{so}', '{mac_add}', {fk_empresa})")
            conexao_my.commit()

            if cursor_my.rowcount > 0:
                resultado_my = True

    return resultado_my or resultado_ms

def definir_parametros_obrigatorios(mac_add):
    resultado_ms = False
    resultado_my = False

    if AMBIENTE == "producao":
        with pymssql.connect(server=HOST_MSSQL, user=USER_MSSQL, password=PASS_MSSQL, database=DATABASE) as conexao_ms:
            with conexao_ms.cursor() as cursor_ms:
                cursor_ms.execute(f"INSERT INTO Parametro VALUES ((SELECT idServidor FROM Servidor WHERE enderecoMac = '{mac_add}'), 2), ((SELECT idServidor FROM Servidor WHERE enderecoMac = '{mac_add}'), 5), ((SELECT idServidor FROM Servidor WHERE enderecoMac = '{mac_add}'), 7), ((SELECT idServidor FROM Servidor WHERE enderecoMac = '{mac_add}'), 12);")
                conexao_ms.commit()

                if cursor_ms.rowcount > 0:
                    resultado_ms = True

    with mysql.connector.connect(host=HOST_MYSQL, user=USER_MYSQL, password=PASS_MYSQL, database=DATABASE) as conexao_my:
        with conexao_my.cursor() as cursor_my:
            cursor_my.execute(f"INSERT INTO Parametro VALUES ((SELECT idServidor FROM Servidor WHERE enderecoMac = '{mac_add}'), 2), ((SELECT idServidor FROM Servidor WHERE enderecoMac = '{mac_add}'), 5), ((SELECT idServidor FROM Servidor WHERE enderecoMac = '{mac_add}'), 7), ((SELECT idServidor FROM Servidor WHERE enderecoMac = '{mac_add}'), 12);")
            conexao_my.commit()

            if cursor_my.rowcount > 0:
                resultado_my = True

    return resultado_my or resultado_ms

def obter_dados_servidor(mac_add):
    resultado = []

    if AMBIENTE == 'producao':
        with pymssql.connect(server=HOST_MSSQL, user=USER_MSSQL, password=PASS_MSSQL, database=DATABASE) as conexao_ms:
            with conexao_ms.cursor() as cursor_ms:    
    
                cursor_ms.execute(f"SELECT idServidor, ultimoRegistro, modelo FROM visaoGeralServidores WHERE enderecoMac = '{mac_add}'")
                servidores = cursor_ms.fetchall()

                resultado.append(servidores[0][0])
                resultado.append(servidores[0][1])
                resultado.append(servidores[0][2])

    if len(resultado) == 0:
        with mysql.connector.connect(host=HOST_MYSQL, user=USER_MYSQL, password=PASS_MYSQL, database=DATABASE) as conexao_my:
            with conexao_my.cursor() as cursor_my:
                cursor_my.execute(f"SELECT idServidor, ultimoRegistro, modelo FROM visaoGeralServidores WHERE enderecoMac = '{mac_add}'")
                servidores = cursor_my.fetchall()

                resultado.append(servidores[0][0])
                resultado.append(servidores[0][1])
                resultado.append(servidores[0][2])

    return resultado

def obter_parametros_coleta(id_servidor):
    parametros = []

    if AMBIENTE == "producao":
        with pymssql.connect(server=HOST_MSSQL, user=USER_MSSQL, password=PASS_MSSQL, database=DATABASE) as conexao_ms:
            with conexao_ms.cursor() as cursor_ms:
                cursor_ms.execute(f'select fk_Metrica from Parametro where fk_Servidor = {id_servidor}')
                parametros = cursor_ms.fetchall()

    if len(parametros) == 0:
        with mysql.connector.connect(host=HOST_MYSQL, user=USER_MYSQL, password=PASS_MYSQL, database=DATABASE) as conexao_my:
            with conexao_my.cursor() as cursor_my:
                cursor_my.execute(f'select fk_Metrica from Parametro where fk_Servidor = {id_servidor}')
                parametros = cursor_my.fetchall()

    return parametros

def obter_aplicacoes(id_servidor):
    aplicacoes = []

    if AMBIENTE == 'producao':
        with pymssql.connect(server=HOST_MSSQL, user=USER_MSSQL, password=PASS_MSSQL, database=DATABASE) as conexao_ms:
            with conexao_ms.cursor() as cursor_ms:                
                cursor_ms.execute(f"SELECT nome, porta FROM Aplicacao WHERE fkServidor = {id_servidor}")
                aplicacoes = cursor_ms.fetchall()

    if len(aplicacoes) == 0:
        with mysql.connector.connect(host=HOST_MYSQL, user=USER_MYSQL, password=PASS_MYSQL, database=DATABASE) as conexao_my:
            with conexao_my.cursor() as cursor_my:
                cursor_my.execute(f"SELECT nome, porta FROM Aplicacao WHERE fkServidor = {id_servidor}")
                aplicacoes = cursor_my.fetchall()

    return aplicacoes

def registrar_leituras(leituras, horario_formatado, processos):
    resultado_ms = False
    resultado_my = False

    if AMBIENTE == 'producao':
        with pymssql.connect(server=HOST_MSSQL, user=USER_MSSQL, password=PASS_MSSQL, database=DATABASE) as conexao_ms:
            with conexao_ms.cursor() as cursor_ms:                
                cursor_ms.executemany("INSERT INTO Leitura VALUES (%s, %s, '" + horario_formatado +"', %s, %s, %s)", leituras)
                cursor_ms.executemany("INSERT INTO Processo VALUES (%i, %i, '" + horario_formatado +"', %s, %.2f, %s, %.2f, %s)", processos)
                conexao_ms.commit()

                if cursor_ms.rowcount > 0:
                    resultado_ms = True

    with mysql.connector.connect(host=HOST_MYSQL, user=USER_MYSQL, password=PASS_MYSQL, database=DATABASE) as conexao_my:
        with conexao_my.cursor() as cursor_my:
            cursor_my.executemany("INSERT INTO Leitura VALUES (%s, %s, '" + horario_formatado +"', %s, %s, %s)", leituras)
            cursor_my.executemany("INSERT INTO Processo VALUES (%s, %s, '" + horario_formatado +"', %s, %s, %s, %s, %s)", processos)
            conexao_my.commit()

            if cursor_my.rowcount > 0:
                resultado_my = True

    return resultado_my or resultado_ms
