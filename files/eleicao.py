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

UCAST_ADDR              = "127.0.0.1"
UCAST_PORT              = 3000
N_ATRIBUTOS             = 5
ATR_PAI                 = 1
ATR_FILHOS              = 2
ATR_MAIOR_PESO          = 3
ATR_MAIOR_REMETENTE     = 4
ATR_RETORNOS_RECEBIDOS  = 5

# Number of the current process
process_number      = int(sys.argv[1])

# Import the total number of process and the weight of the current process
text_import = "inputs/node" + str(process_number) + ".txt"
with open (text_import, "r") as file:
    aux             = file.read()
    process_count   = aux[0]
    config.peso     = aux[2]

process_count           = int(process_count)
config.peso             = int(config.peso)

# matriz_adj contains the adjacence list of all process
config.matriz_adj       = [[0] * (process_count + 1) for x in range(process_count + 1)]

# matriz_eleicao contains all the information of the election
#   - Father
#   - Number of adjacent process excluding father
#   - Greatest weight received
#   - Origin of the greatest weight received
#   - Number of received returns
config.matriz_eleicao   = [[0] * (process_count + 1) for x in range(int(N_ATRIBUTOS) + 1)]
config.matriz_eleicao[ATR_MAIOR_PESO][process_number] = config.peso
config.matriz_eleicao[ATR_MAIOR_REMETENTE][process_number] = process_number

with open("inputs/adj.txt", "r") as file:
    for line in file:
        config.matriz_adj[int(line[0])][int(line[2])] = 1
        config.matriz_adj[int(line[2])][int(line[0])] = 1

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((UCAST_ADDR, UCAST_PORT + process_number))

config.matriz_eleicao[ATR_FILHOS][process_number]               = 0

config.matriz_eleicao[ATR_PAI][process_number]                  = 0
config.matriz_eleicao[ATR_RETORNOS_RECEBIDOS][process_number]   = 0
for i in range(1, int(process_count) + 1):
    config.matriz_eleicao[ATR_MAIOR_PESO][i]           = config.peso
    config.matriz_eleicao[ATR_MAIOR_REMETENTE][i]      = process_number
    
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

        config.matriz_eleicao[ATR_FILHOS][process_number]               = 0
        
        config.matriz_eleicao[ATR_PAI][process_number]                  = 0
        config.matriz_eleicao[ATR_RETORNOS_RECEBIDOS][process_number]   = 0
        for i in range(1, int(process_count) + 1):
            config.matriz_eleicao[ATR_MAIOR_PESO][i]           = config.peso
            config.matriz_eleicao[ATR_MAIOR_REMETENTE][i]      = process_number
        

        if(opcao == 1):
            print("Starting election from process n. " + str(process_number) + " ...\n")
            msg_elect = "Eleicao" + "/" + str(process_number) + "/" + str(process_number)

            for i in range(1, int(process_count) + 1):
                if(config.matriz_adj[process_count][i] == 1):
                    print ("Sending ELECTION message to proces n. ", i)
                    sock.sendto(msg_elect.encode(), (UCAST_ADDR, UCAST_PORT + i))
                    config.matriz_eleicao[ATR_FILHOS][process_number] = config.matriz_eleicao[ATR_FILHOS][process_number] + 1
            while(True):
                if(config.matriz_eleicao[ATR_FILHOS][process_number] == config.matriz_eleicao[ATR_RETORNOS_RECEBIDOS][process_number]):
                    print("\nElection terminated, elected node: " + str(config.matriz_eleicao[ATR_MAIOR_REMETENTE][process_number]) 
                    + " Weight: " + str(config.matriz_eleicao[ATR_MAIOR_PESO][process_number]))


                    msg_elected = "Elected" + "/" + str(config.matriz_eleicao[ATR_MAIOR_REMETENTE][process_number]) + "/" + str(config.matriz_eleicao[ATR_MAIOR_PESO][process_number]) + "/" + str(process_number)

                    for i in range(1, process_count + 1):
                        if(i != process_number):
                            sock.sendto(msg_elected.encode(), (UCAST_ADDR, UCAST_PORT + i))

                    break

def receiver():
    while True:
        data = sock.recv(1024)
        data = data.decode()

        msgsplit        = data.split("/")
        msg             = msgsplit[0]
        origem          = int(msgsplit[1])
        raiz_eleicao    = int(msgsplit[2])

        if(msg == "Eleicao"):
        
            print("Received an ELECTION" + str(raiz_eleicao) + " message from process n." + str(origem))
            retornar = 1
            
            if(config.matriz_eleicao[ATR_PAI][raiz_eleicao] == 0):
                print("Defined father as process n." + str(origem))
                config.matriz_eleicao[ATR_PAI][raiz_eleicao] = origem
                for i in range(1, process_count + 1):
                    if(config.matriz_adj[process_number][i] == 1):
                        if(not config.matriz_eleicao[ATR_PAI][raiz_eleicao] == i):
                            print("Sending ELECTION message to process n." + str(i))
                            msg_elect = "Eleicao" + "/" + str(process_number) + "/" + str(raiz_eleicao)
                            sock.sendto(msg_elect.encode(), (UCAST_ADDR, UCAST_PORT + i))
                            retornar = 0
                            config.matriz_eleicao[ATR_FILHOS][raiz_eleicao] = config.matriz_eleicao[ATR_FILHOS][raiz_eleicao] + 1
                
                if(retornar):
                    print("Returning to node n." + str(config.matriz_eleicao[ATR_PAI][raiz_eleicao]))

                    msg_return = "Return" + "/" + str(process_number) + "/" + str(raiz_eleicao) + "/" + str(config.matriz_eleicao[ATR_MAIOR_REMETENTE][raiz_eleicao]) + "/" + str(config.matriz_eleicao[ATR_MAIOR_PESO][raiz_eleicao])
                    print("????"+msg_return)
                    sock.sendto(msg_return.encode(), (UCAST_ADDR, UCAST_PORT + config.matriz_eleicao[ATR_PAI][raiz_eleicao]))
                
            else:
                msg_ok = "OK" + "/" + str(raiz_eleicao) + "/" + str(process_number)
                print("origem:"+str(origem))
                sock.sendto(msg_ok.encode(), (UCAST_ADDR, UCAST_PORT + origem))



        elif(msg == "Return"):
        
            print("Received Return message from process n." + str(origem))
            peso_recebido       = int(msgsplit[4])
            process_recebido    = int(msgsplit[3])
            print(peso_recebido)
            config.matriz_eleicao[ATR_RETORNOS_RECEBIDOS][raiz_eleicao] = config.matriz_eleicao[ATR_RETORNOS_RECEBIDOS][raiz_eleicao] + 1
            if(peso_recebido > int(config.matriz_eleicao[ATR_MAIOR_PESO][raiz_eleicao])):
                config.matriz_eleicao[ATR_MAIOR_PESO][raiz_eleicao] = peso_recebido
                config.matriz_eleicao[ATR_MAIOR_REMETENTE][raiz_eleicao] = process_recebido

            if(config.matriz_eleicao[ATR_FILHOS][raiz_eleicao] == config.matriz_eleicao[ATR_RETORNOS_RECEBIDOS][raiz_eleicao]):         
                print("Returning to node n." + str(config.matriz_eleicao[ATR_PAI][raiz_eleicao]))
                msg_return = "Return" + "/" + str(process_number) + "/" + str(raiz_eleicao) + "/" + str(config.matriz_eleicao[ATR_MAIOR_REMETENTE][raiz_eleicao]) + "/"               + str(config.matriz_eleicao[ATR_MAIOR_PESO][raiz_eleicao])

                sock.sendto(msg_return.encode(), (UCAST_ADDR, UCAST_PORT + config.matriz_eleicao[ATR_PAI][raiz_eleicao]))
        
        
        elif(msg == "OK"):
            raiz_eleicao = int(msgsplit[1])
            origem = int(msgsplit[2])
            print("Received OK message from process n." + str(msgsplit[2]))
        
            config.matriz_eleicao[ATR_FILHOS][raiz_eleicao] -= 1
            if(config.matriz_eleicao[ATR_FILHOS][raiz_eleicao] < 0):
                config.matriz_eleicao[ATR_FILHOS][raiz_eleicao] = 0
            if(config.matriz_eleicao[ATR_FILHOS][raiz_eleicao] == config.matriz_eleicao[ATR_RETORNOS_RECEBIDOS][raiz_eleicao]):
                print("Returning to node n." + str(config.matriz_eleicao[ATR_PAI][raiz_eleicao]))
                A = np.array(config.matriz_eleicao)
                print(A)
                msg_return = "Return" + "/" + str(process_number) + "/" + str(raiz_eleicao) + "/" + str(config.matriz_eleicao[ATR_MAIOR_REMETENTE][raiz_eleicao]) + "/" + str(config.matriz_eleicao[ATR_MAIOR_PESO][raiz_eleicao])
                print(msg_return)
                sock.sendto(msg_return.encode(), (UCAST_ADDR, UCAST_PORT + config.matriz_eleicao[ATR_PAI][raiz_eleicao]))

        elif(msg == "Elected"):
            origem = int(msgsplit[3])
            print("Election" + str(msgsplit[3] + " terminated, Elected node: " + str(msgsplit[1]) + ", Weight: " + str(msgsplit[2])))

            config.matriz_eleicao[ATR_PAI][origem] = 0
            config.matriz_eleicao[ATR_FILHOS][origem]               = 0
            config.matriz_eleicao[ATR_RETORNOS_RECEBIDOS][origem]   = 0
            for i in range(1, process_count + 1):
                config.matriz_eleicao[ATR_MAIOR_PESO][i]           = config.peso
                config.matriz_eleicao[ATR_MAIOR_REMETENTE][i]      = process_number



if __name__ == '__main__':
    r = threading.Thread(target = receiver)
    s = threading.Thread(target = sender)

    r.daemon = True
    s.daemon = True

    r.start()
    s.start()

    while True:
        time.sleep(1)