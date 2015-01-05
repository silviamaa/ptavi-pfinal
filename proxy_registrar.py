#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Clase (y programa principal) para un servidor
"""

import SocketServer
import sys
import time
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

dicc_usuario = {}

def AñadirLog(evento):
    fichero = open(cHandler.log, 'a')
    mensaje = str(time.time()) + " " + evento + '\r\n'
    fichero.write(mensaje)
    fichero.close()


class ProxyRegisHandler(ContentHandler):

    def __init__(self):
        """
        Constructor. Inicializamos las variables
        """
        self.s_name = ''
        self.s_ip = ''
        self.s_port = ''
        self.registro_usuarios = ''
        self.passwd_path = ''
        self.log = ''

    def startElement(self, name, attrs):
        """
        Método que se llama cuando se abre una etiqueta
        """
        if name == 'server':
            self.s_name = attrs.get('name', "")
            self.s_ip = attrs.get('ip', "127.0.0.1")
            self.s_port = attrs.get('puerto', "")
        elif name == 'database':
            self.registro_usuarios = attrs.get('path', "")
            self.passwd_path = attrs.get('passwdpath', "")
        elif name == 'log':
            self.log = attrs.get('path', "")


class Handler(SocketServer.DatagramRequestHandler):

    """
    Handler
    """

    def handle(self):
        ip = str(self.client_address[0])
        hora = time.time()
        while 1:
            line = self.rfile.read()
            line1 = line.split()
            
            if line1[0] == "REGISTER":
                line2 = line1[1]
                line3 = line2.split(":")
                user = line3[1]
                dicc_usuario[user] = ip
                port = int(line3[2])
                if line1[4] == '0':
                    if user in dicc_usuario:
                        del dicc_usuario[user]
                        self.register2file()
                        self.wfile.write("El usuario se ha borrado\r\n")
                        self.wfile.write("SIP/2.0 200 OK\r\n\r\n")
                else:
                    hora_actualizada = hora + int(line1[4])
                    #añado valor y tiempo a la clave del dicc_usuario
                    dicc_usuario[user] = ip + ',' + str(hora_actualizada)
                    self.register2file()
                    self.wfile.write("SIP/2.0 200 OK\r\n\r\n")

            if line1[0] == "INVITE":
            #busco si el usuario existe y envío el INVITE, si no, envío 
            #"404 user not found"

            #meter en log envío y recepcion

            if line1[0] == "ACK":
            #se retransmite al destino

            #meter en log envio
            
            if line1[0] == "BYE":
            #se retransmite al destino y se envia la respuesta al uaclient
            
            #meter en log envio, recepcion y envio

            if not line or "[""]":
                break
    """
    Registrar al usuario con dirección + IP + PORT + fecha de registro + Expires
    """

    def register2file(self):
        registered = open("registered.txt", "w")
        registered.write('User' + "\t" + 'IP' + "\t" + 'Expires' + '\n')
        for user, valor in dicc_usuario.items():
            ip = valor.split(',')[0]
            hora_actual = time.strftime('%Y-%m-%d %H:%M:%S',
                                        time.gmtime(time.time()))
            registered.write(user + "\t" + ip + "\t" + hora_actual + "\n")


if __name__ == "__main__":
    
    """
    Programa principal
    """
    # Parser
    parser = make_parser()
    cHandler = ProxyHandler()
    parser.setContentHandler(cHandler)
    parser.parse(open(str(sys.argv[1]))

    if len(sys.argv) != 2:
        print("Usage: python proxy_registrar.py config")
        
        #meter error en log
         
    # Creamos servidor y escuchamos
    serv = SocketServer.UDPServer((str(cHandler.s_ip),
                                   int(cHandler.s_port)), Handler)
    print "Server MiServidorProxy listening at port " + cHandler.s_port + "..."
    serv.serve_forever()
