import socket
from threading import Thread
import pickle
import random, string
import os
class PeerToPeer:
    def __init__(self, LOCALPORT,HOST ):
        self.HOST=HOST
        self.LOCALPORT=LOCALPORT
        self.connections = []
    def conectar(self,PORT,HOST):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST,PORT ))
        dicionario={0:"Hello World",1:"Hello World"}
        msg=pickle.dumps(dicionario)
        s.send(msg)
        dicionario={0:PORT,1:HOST}
        self.connections.append(dicionario)
        msg = s.recv(1024)
        print(msg.decode("utf-8"))
    def listen(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.HOST,self.LOCALPORT ))
        s.listen(5)
        print(f"Servidor escutando na porta:",self.LOCALPORT)

        while True:
            clientsocket, address = s.accept()
            recebido=clientsocket.recv(1024)
            recebido=pickle.loads(recebido)#converte de bytes para dictionary
            if(recebido[0]=="Ping"):
                if(recebido[2]>=0):#verifica se O TTL não zerou
                    tamanho=len(self.connections)
                    if(tamanho>=0):#verifica se existe portas cadastradas em connections
                        for peer in self.connections:#percorre todas as conexões do host
                            s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            s2.connect((peer[1],peer[0] ))
                            dicionario={0:"Ping",1:peer[0],2:recebido[2]-1,3:recebido[3],4:recebido[4]+1,5:peer[1]}
                            msg=pickle.dumps(dicionario)
                            s2.send(msg)#para cada porta de connetions, envia um Ping com TTL decrementado
                            msg=s2.recv(100)#recebe porta do outro salto 
                            while(msg):
                                clientsocket.send(msg)#retorna a porta 
                                msg=s2.recv(100)#recebe portas dos outros saltos 
 
                    clientsocket.send(bytes(f'A Porta do host:{recebido[1]}\n',"utf-8"))
                    clientsocket.send(bytes(f'O IP do host:{self.HOST}\n',"utf-8"))
                    clientsocket.send(bytes(f'Saltos até o momento:{recebido[4]}\n',"utf-8")) 
                    clientsocket.send(bytes(f'ID da mensagem:{recebido[3]}\n',"utf-8"))
            print(f"Connection from {address} has been established.")
            if(recebido[0]=="Querry"):
                if(recebido[4]>=0):#verifica se O TTL não zerou
                    path = os.path.dirname(os.path.abspath(__file__))#o caminho até o arquivo atual
                    files = os.listdir(path)#retorna todos os nomes dos arquivos no diretório
                    flag=False
                    for f in files:#percorre todos os arquivos dodiretório
                        if(os.path.splitext(f)[0]==recebido[1]):#compara os nomes sem a extensão
                            flag=True
                            arquivo=f
                            break
                    if(flag):#caso o arquivo exista no host
                        clientsocket.send(bytes("O arquivo existe\n","utf-8"))
                        clientsocket.send(bytes(f'Porta de localização do arquivo {self.LOCALPORT}\n',"utf-8"))
                        clientsocket.send(bytes(f'Tamanho do arquivo em Bytes é {os.path.getsize(arquivo)}\n',"utf-8"))
                        clientsocket.send(bytes(f'Extensão do arquivo é {os.path.splitext(arquivo)[1]}\n',"utf-8"))
                
                    tamanho=len(self.connections)
                    if(tamanho>=0):#verifica se existe portas cadastradas em connections
                        for peer in self.connections:#percorre todas as conexões do host
                            s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            s2.connect((peer[1],peer[0] ))
                            dicionario={0:"Querry",1:recebido[1],2:recebido[2],3:recebido[3]+1,4:recebido[4]-1}
                            msg=pickle.dumps(dicionario)
                            s2.send(msg)#para cada porta de connetions,chama a fnção querry
                            msg=s2.recv(4)#recebe porta do outro salto 
                            while(msg):
                                clientsocket.send(msg)#retorna a porta 
                                msg=s2.recv(4)#recebe portas dos outros saltos     

                
            if(recebido[0]=="Download"): 
                f = open(recebido[1], "r")#cria o arquivo como o nome em recebido[1]
                for x in f:#percorre todo o arquivo
                    clientsocket.send(bytes(x,"utf-8"))#envia uma linha do arquivo
                f.close()

            if(recebido[0]=="Hello World"):
                clientsocket.send(bytes("Welcome to the server!","utf-8"))
            clientsocket.close()
    def ping(self,PORT,TTL,IP):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.HOST,PORT ))
        Message_ID=self.randomword(10)
        Hop=0
        dicionario={0:"Ping",1:PORT,2:TTL-1,3:Message_ID,4:Hop+1,5:IP}# dicionario[0]="Ping" dicionario[1]=PORT dicionario[2]=TTL-1
        msg=pickle.dumps(dicionario)#transforma dicionário em byte
        s.send(msg)
        msg=s.recv(100)
        while(msg):#enquanto tiver mensagem para receber
            print(msg.decode("utf-8"))
            msg=s.recv(100)

    def query(self,PORT,filename,IP):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        s.connect((self.HOST,PORT ))
        Message_ID=self.randomword(10)
        Hop=0
        TTL=10
        dicionario={0:"Querry",1:filename,2:Message_ID,3:Hop,4:TTL,5:IP}

        msg=pickle.dumps(dicionario)
        s.send(msg)
        msg=s.recv(1024)
        if(msg.decode("utf-8")!="O arquivo existe\n"):#caso a primeira mensagem seja vazia,s.recv(1024) não retorna nada
            return False

        while(msg):#enquanto tiver mensagem para receber
            print(msg.decode("utf-8"))
            msg=s.recv(1024)
        return True

    def download(self,PORT,filename,IP):
        nome_do_arquivo=self.randomword(10)#gera um nome alatório para o arquivo
        nome_do_arquivo=nome_do_arquivo+os.path.splitext(filename)[1]#adiciona a extensão do filename
        print("Nome do arquivo baixado:",nome_do_arquivo)
        f = open(nome_do_arquivo, "x")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        s.connect((self.HOST,PORT ))
        dicionario={0:"Download",1:filename,2:IP}
        msg=pickle.dumps(dicionario)
        s.send(msg) 
        msg=s.recv(8)
        while(msg):#enquanto tiver mensagem para receber
            f.write(msg.decode("utf-8"))#escreve no novo arquivo
            msg=s.recv(100)
        
    def randomword(self,length):#gera um nome aleatório
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))