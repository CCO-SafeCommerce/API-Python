# lista = [10, 25, 30, 45, 50, 60, 70, 80, 90, 100, 75, 65, 55, 40, 35, 20, 15, 5, 0]

# for i in range(len(lista)):
#   for j in range(len(lista)):
#     if lista[i] <= lista[j]:
#       salvar = lista[i]
#       lista[i] = lista[j]
#       lista[j] = salvar

# print(lista)

from pyexpat import model
import getmac
import platform
import psutil
from time import sleep
import bcrypt

# teste = getmac.get_mac_address()

# print(teste)

# so = platform.system()
# modelo = platform.node()

# print("Sistema Operacional: ", so)
# print("Modelo da Maqina: ", modelo)
# while True:


#     for processos in psutil.process_iter():
#         processos_info = processos.as_dict(['name', 'cpu_percent'])
#         nome = processos_info['name']
#         uso_cpu = processos_info['cpu_percent']
#         print("nome do Processo: ",nome)
#         print("Uso de cpu: ", uso_cpu)
#         print("")
#         sleep(1)

print(bcrypt.hashpw(b"senha123", bcrypt.gensalt(8))) #Criptografar senha do usuario

entrada_usu = "senha123"
senha = b"senha123" # só para conferir
senha = entrada_usu.encode('UTF-8')

hashed = bcrypt.hashpw(senha, bcrypt.gensalt(8))
login = bcrypt.checkpw(senha, hashed)

