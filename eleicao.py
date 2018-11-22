# - Alunos:
#       Henrique afundado Kodama    RA:
#       Vinicius Yamamoto RA:490105
#
# - Disciplina:
#       Sistemas Distribuidos
#
# - Professo:
#       Fabio Verdi
#
# - UFSCar Sorocaba
# ------ Libraries ------ #

import config
import mod
import socket
import operator
import sys
import random
import queue
import time
import threading
from time import sleep
from _thread import *
from random import *

UCAST_ADDR = "127.0.0.1"
UCAST_PORT = 3000
config.fila = queue.Queue()
process_count = input()
config.matriz_adj = [[0] * (int(process_count) + 1) for x in range(int(process_count) + 1)]
config.peso = [0 for i in range(process_count+1)]
config.reconhecimento = [[0] * (int(process_count) + 1) for x in range(int(process_count) + 1)]
config.pai = [0 for i in range(process_count+1)]
config.visitado = [0 for i in range(process_count+1)]

int(process_one) = input()
int(process_two) = input()

while(process_one != 0 && process_two != 0):
    config.matriz_adj[process_one][process_two] = 1
    config.matriz_adj[process_two][process_one] = 1
    int(process_one) = input()
    int(process_two) = input()

for(i in range(1,process_count+1)):
    int(config.peso[i]) = input()
    config.reconhecimento[i] = config.peso[i]

int(raiz) = input()
config.fila.put(raiz)
config.visitado[raiz] = 1

#sender
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((UCAST_ADDR, UCAST_PORT))

#receiver
for(i in range(1,process_count+1)):
    config.socket[i] = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    config.socket[i].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    config.socket[i].bind((UCAST_ADDR, UCAST_PORT + i))
# sock0 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

# sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# sock.bind((UCAST_ADDR, UCAST_PORT + process_number))

# sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
# sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# sock.bind((UCAST_ADDR, UCAST_PORT + process_number))

# sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
# sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# sock.bind((UCAST_ADDR, UCAST_PORT + process_number))

# sock3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
# sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# sock.bind((UCAST_ADDR, UCAST_PORT + process_number))

# sock4 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
# sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# sock.bind((UCAST_ADDR, UCAST_PORT + process_number))

# sock5 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
# sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# sock.bind((UCAST_ADDR, UCAST_PORT + process_number))

# sock6 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
# sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# sock.bind((UCAST_ADDR, UCAST_PORT + process_number))

# sock7 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
# sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# sock.bind((UCAST_ADDR, UCAST_PORT + process_number))

# sock8 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
# sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# sock.bind((UCAST_ADDR, UCAST_PORT + process_number))

# sock9 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
# sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# sock.bind((UCAST_ADDR, UCAST_PORT + process_number))

def eleger():
    while(!config.fila.empty()):
        origem = config.fila.get()
        for(i in range(1,process_count+1)):
            if(config.matriz_adj[origem][i] == 1):
                if(config.pai[i] == 0):
                    initial_msg = "eleicao" + "/" + str(origem) + "/" + str(i)
                    sock.sendto(initial_msg.encode(), (UCAST_ADDR, UCAST_PORT+i))
                
def sender(remetente, mensagem):
    sock.sendto(mensagem.encode(), (UCAST_ADDR, UCAST_PORT))
    
def receiver1():
    # Receive loop
    while True:
        data = socket[1].recv(1024)
        data = data.decode()
        msgsplit = data.split("/")
        msgsplit[1] = int(msgsplit[1])
        msgsplit[2] = int(msgsplit[2])
        if(msgsplit[0] == "eleicao"):
            config.pai[msgsplit[2]] = msgsplit[1]
            config.fila.put(msgsplit[2])
            config.visitado[msgsplit[2]] = 1
            retornar = 1
            for(i in range(1,process_count+1)):
                if(config.matriz_adj[msgsplit[2]][i] == 1):
                    if(config.visitado[i] == 0):
                        retornar = 0
                        break
            if(retornar == 1):
                maior = max(config.reconhecimento[msgsplit[2]])
                mensagem_retorno = "retorno" + "/" + str(msgsplit[2]) + "/" + str(config.pai[msgsplit[2]]) + "/" + str(maior)
                sock.sendto(mensagem_retorno.encode(), (UCAST_ADDR, UCAST_PORT+config.pai[msgsplit[2]]))
        else:
            msgsplit[3] = int(msgsplit[3])
            config.reconhecimento[msgsplit[2]][msgsplit[1]] = msgsplit[3]
            maior = max(config.reconhecimento[msgsplit[2]])
            mensagem_retorno = "retorno" + "/" + str(msgsplit[2]) + "/" + str(config.pai[msgsplit[2]]) + "/" + str(maior)
            sock.sendto(mensagem_retorno.encode(), (UCAST_ADDR, UCAST_PORT+config.pai[msgsplit[2]]))

if __name__ == '__main__':
    pid = int(sys.argv[1])
    if(sys.argv[1] == str(0)):
        rtinit0()
    if(sys.argv[1] == str(1)):
        rtinit1()
    if(sys.argv[1] == str(2)):
        rtinit2()
    if(sys.argv[1] == str(3)):
        rtinit3()

    for a in tabeladist:
        print(str(a.dist) + " " + str(a.nexthope))

    r = threading.Thread(target = receiver)

    r.daemon = True

    r.start()
    time.sleep(7)
    sender()
    while(True):
        time.sleep(1)