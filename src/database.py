import pymssql
import mysql.connector
import bcrypt

AMBIENTE="desenvolvimento"

HOST_MYSQL = "localhost"
USER_MYSQL = "aluno"
PASS_MYSQL = "sptech"
DB = "safecommerce"

HOST_MSSQL = "safecommerce.database.windows.net"
USER_MSSQL = "adm-safecommerce"
PASS_MSSQL = "1cco#grupo4"

def is_servidor_cadastrado(mac_add):
    resultado = False

    if AMBIENTE == "desenvolvimento":
        conexao = mysql.connector.connect(host=HOST_MYSQL, user=USER_MYSQL, password=PASS_MYSQL, database=DB)
        
    else:
        conexao = pymssql.connect(server=HOST_MSSQL, user=USER_MSSQL, password=PASS_MSSQL, database=DB)

    cursor = conexao.cursor()
    cursor.execute(f"select idServidor from Servidor where enderecoMac = '{mac_add}'")
    servidores_encontrados = cursor.fetchall()

    cursor.close()
    conexao.close()

    if len(servidores_encontrados) > 0:
        resultado = True
    
    return resultado

def obter_fk_empresa_via_login(email, senha):
    if AMBIENTE == "desenvolvimento":
        conexao = mysql.connector.connect(host=HOST_MYSQL, user=USER_MYSQL, password=PASS_MYSQL, database=DB)
        
    else:
        conexao = pymssql.connect(server=HOST_MSSQL, user=USER_MSSQL, password=PASS_MSSQL, database=DB)

    cursor = conexao.cursor()

    cursor.execute(f"select email, senha, fkEmpresa from Usuario where email = '{email}'")
    usuarios = cursor.fetchall()

    cursor.close()
    conexao.close()

    fk_empresa = 0

    if len(usuarios) > 0:
        is_senha_correta = bcrypt.checkpw(senha.encode('UTF-8'), usuarios[0][1].encode('UTF-8'))

        if is_senha_correta:
            fk_empresa = usuarios[0][2]

    return fk_empresa

def cadastrar_servidor(modelo, so, mac_add, fk_empresa):
    resultado = False

    if AMBIENTE == "desenvolvimento":
        conexao = mysql.connector.connect(host=HOST_MYSQL, user=USER_MYSQL, password=PASS_MYSQL, database=DB)
        
    else:
        conexao = pymssql.connect(server=HOST_MSSQL, user=USER_MSSQL, password=PASS_MSSQL, database=DB)

    cursor = conexao.cursor()

    cursor.execute(f"INSERT INTO Servidor (modelo, so, enderecoMac, fkEmpresa) VALUES ('{modelo}', '{so}', '{mac_add}', {fk_empresa})")
    conexao.commit()

    if cursor.rowcount > 0:        
        cursor.execute(f"INSERT INTO Parametro VALUES ((SELECT idServidor FROM Servidor WHERE enderecoMac = '{mac_add}'), 2), ((SELECT idServidor FROM Servidor WHERE enderecoMac = '{mac_add}'), 5), ((SELECT idServidor FROM Servidor WHERE enderecoMac = '{mac_add}'), 7);")
        conexao.commit()

    cursor.close()
    conexao.close()

    resultado = True
    return resultado

def obter_dados_servidor(mac_add):
    if AMBIENTE == "desenvolvimento":
        conexao = mysql.connector.connect(host=HOST_MYSQL, user=USER_MYSQL, password=PASS_MYSQL, database=DB)
        
    else:
        conexao = pymssql.connect(server=HOST_MSSQL, user=USER_MSSQL, password=PASS_MSSQL, database=DB)

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
    if AMBIENTE == "desenvolvimento":
        conexao = mysql.connector.connect(host=HOST_MYSQL, user=USER_MYSQL, password=PASS_MYSQL, database=DB)
        
    else:
        conexao = pymssql.connect(server=HOST_MSSQL, user=USER_MSSQL, password=PASS_MSSQL, database=DB)

    cursor = conexao.cursor()

    cursor.execute(f"SELECT fk_Metrica FROM Parametro WHERE fk_Servidor = {id_servidor}")

    parametros = cursor.fetchall()

    cursor.close()
    conexao.close() 

    return parametros

def obter_aplicacoes(id_servidor):
    if AMBIENTE == "desenvolvimento":
        conexao = mysql.connector.connect(host=HOST_MYSQL, user=USER_MYSQL, password=PASS_MYSQL, database=DB)
        
    else:
        conexao = pymssql.connect(server=HOST_MSSQL, user=USER_MSSQL, password=PASS_MSSQL, database=DB)

    cursor = conexao.cursor()

    cursor.execute(f"SELECT nome, porta FROM Aplicacao WHERE fkServidor = {id_servidor}")

    aplicacoes = cursor.fetchall()

    cursor.close()
    conexao.close() 

    return aplicacoes

def registrar_leituras(leituras, horario_formatado):
    if AMBIENTE == "desenvolvimento":
        conexao = mysql.connector.connect(host=HOST_MYSQL, user=USER_MYSQL, password=PASS_MYSQL, database=DB)
        
    else:
        conexao = pymssql.connect(server=HOST_MSSQL, user=USER_MSSQL, password=PASS_MSSQL, database=DB)

    cursor = conexao.cursor()

    cursor.executemany("INSERT INTO Leitura VALUES (%s, %s, '" + horario_formatado +"', %s, %s, %s)", leituras)
    conexao.commit()

    cursor.close()
    conexao.close()
