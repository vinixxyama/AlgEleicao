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
import time
import threading
from time import sleep
import numpy as np

UCAST_ADDR = "127.0.0.1"
UCAST_PORT = 3000

process_number      = int(sys.argv[1])

text_import = "inputs/node" + str(process_number) + ".txt"

with open (text_import, "r") as file:
    aux             = file.read()
    process_count   = aux[0]
    config.peso     = aux[2]

# process_count       = int(input("Insert the number of the process: "))
# config.peso         = int(input("Insert the weight of your process: "))
config.matriz_adj   = [[0] * (int(process_count) + 1) for x in range(int(process_count) + 1)]
config.pai          = 0
config.visitado     = [0 for x in range(int(process_count) + 1)]
config.filhos       = 0
config.maior_peso   = config.peso
config.maior_remetente = process_number
config.retornos_recebidos = 0

with open("inputs/adj.txt", "r") as file:
    for line in file:
        config.matriz_adj[int(line[0])][int(line[2])] = 1
        config.matriz_adj[int(line[2])][int(line[0])] = 1

A = np.array(config.matriz_adj)
print("Matriz de adjacencia:")
print(A)
process_count = int(process_count)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((UCAST_ADDR, UCAST_PORT + process_number))

def sender():
    while True:
        time.sleep(0.25)
        print("""
        ------------------------
        1. Elect a process
        ------------------------
        """)
        time.sleep(0.25)
        opcao = int(input("Select an option: "))

        config.pai          = 0
        config.visitado     = [0 for x in range(int(process_count) + 1)]
        config.filhos       = 0
        config.maior_peso   = config.peso
        config.maior_remetente = process_number
        config.retornos_recebidos = 0

        if(opcao == 1):
            print("Starting election from process n. " + str(process_number) + " ...")
            msg_elect = "Eleicao" + "/" + str(process_number)
            for i in range(1, int(process_count ) + 1):
                msg_visitado = "visitado" + "/" + str(process_number)
                sock.sendto(msg_visitado.encode(), (UCAST_ADDR, UCAST_PORT + i))

            for i in range(1, int(process_count) + 1):
                if(config.matriz_adj[process_count][i] == 1):
                    if(i != config.pai):
                        print ("envicnaod para: ", i)
                        sock.sendto(msg_elect.encode(), (UCAST_ADDR, UCAST_PORT + i))
                        config.filhos = config.filhos + 1
            config.visitado[process_number] = 1
            while(True):
                if(config.filhos == config.retornos_recebidos):
                    print("Elected node: " + str(config.maior_remetente) + " weight: " + str(config.maior_peso))
                    break

def receiver():
    while True:
        data = sock.recv(1024)
        data = data.decode()

        msgsplit    = data.split("/")
        msg         = msgsplit[0]
        origem      = int(msgsplit[1])

        if(msg == "Eleicao"):
            print("Received an ELECTION message from process n." + str(origem))
            retornar = 1
            
            if(config.pai == 0):
                print("Defined father as process n." + str(origem))
                config.pai = origem

            for i in range(1, int(process_count ) + 1):
                msg_visitado = "visitado" + "/" + str(process_number)
                sock.sendto(msg_visitado.encode(), (UCAST_ADDR, UCAST_PORT + i))

            for i in range(1, process_count + 1):
                if(config.matriz_adj[process_number][i] == 1):
                    if(config.visitado[i] == 0):
                        print("Sending ELECTION message to process n." + str(i))
                        msg_visitado = "visitado" + "/" + str(process_number)
                        sock.sendto(msg_visitado.encode(), (UCAST_ADDR, UCAST_PORT + i))
                        msg_elect = "Eleicao" + "/" + str(process_number)
                        sock.sendto(msg_elect.encode(), (UCAST_ADDR, UCAST_PORT + i))
                        retornar = 0
                        config.filhos = config.filhos + 1

            if(retornar):
                print("No unvisited adjacent process, returning to process n." + str(config.pai)+ "peso: " + str(config.maior_peso))
                msg_return = "Retornar" + "/" + str(process_number) + "/" + str(config.maior_remetente) + "/" + str(config.maior_peso)
                sock.sendto(msg_return.encode(), (UCAST_ADDR, UCAST_PORT + config.pai))

        elif(msg == "visitado"):
            config.visitado[origem] = 1

        elif(msg == "Retornar"):
            print("Received Return message from process n." + str(origem))
            print("Filhos: " + str(config.filhos))
            peso_recebido       = int(msgsplit[3])
            process_recebido    = int(msgsplit[2])
            config.retornos_recebidos = config.retornos_recebidos + 1
            if(peso_recebido > int(config.maior_peso)):
                config.maior_peso = peso_recebido
                config.maior_remetente = process_recebido

            if(config.filhos == config.retornos_recebidos):         
                print("Returning to node n." + str(config.pai) + " peso: " + str(peso_recebido))
                msg_return = "Retornar" + "/" + str(process_number) + "/" + str(config.maior_remetente) + "/" + str(config.maior_peso)
                sock.sendto(msg_return.encode(), (UCAST_ADDR, UCAST_PORT + config.pai))


if __name__ == '__main__':
    r = threading.Thread(target = receiver)
    s = threading.Thread(target = sender)

    r.daemon = True
    s.daemon = True

    r.start()
    s.start()

    while True:
        time.sleep(1)