import socket
from threading import Thread
import pickle
import random, string
import os
import sys
from PeerToPeer import PeerToPeer

if len(sys.argv) != 3:#valida a entrada do teclado
    print("use:", sys.argv[0], "<host> <porta>")
    sys.exit(1)

host, port = sys.argv[1], int(sys.argv[2]) 

p2p=PeerToPeer(port,host)#cria o host p2p

class Th(Thread):#essa thread serve para deixar o host escutando para receber reqisições
    def __init__ (self):
        Thread.__init__(self)

    def run(self):      
        p2p.listen()



a = Th()#instancia a thread
a.start() #executa
menu = 0
while not menu == 5:
    menu = int(input('''
        [1] Conectar a uma rede
        [2] Lista de Host cadastradas
        [3] Ping
        [4] Query
        [5] Sair do programa\n
        '''))
    if menu == 1:
        EXTERNALPORT=int(input('Digite o número da porta do servidor que deseja conectar '))
        EXTERNALHOST=str(input('Digite o IP do servidor que deseja conectar '))

        p2p.conectar(EXTERNALPORT,EXTERNALHOST)
    if menu == 2:
        print(p2p.connections)
    if menu == 3:
        print((f'O IP do host:{p2p.HOST}'))
        print((f'A porta do host:{p2p.LOCALPORT}\n'))
        for peer in p2p.connections:
            p2p.ping(peer[0],3,peer[1])#recebe de entrada cada porta de connetions mais o TTL
    if menu == 4:
        nome_do_arquivo=str(input('Qual o nome do arquivo?[somente o nome, sem extensão]'))
        flag=False
        for peer in p2p.connections:
            flag=p2p.query(peer[0],nome_do_arquivo,peer[0])
        if(flag):
            resposta=int(input('Deseja fazer download?[1 para Sim][2 para Não]'))
            if(resposta==1):
                numero_da_porta=int(input('Qual a porta que deseja baixar?'))
                numero_da_IP=str(input('Qual o IP que deseja baixar?'))
                nome_do_arquivo=str(input('Qual o nome do arquivo que deseja baixar?[Nome.extensão]'))
                p2p.download(numero_da_porta,nome_do_arquivo,numero_da_IP)
        else:
            print("O arquivo não existe")
print ('\033[0:31mPrograma finalizado.\033[m')