#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Programa cliente que abre un socket a un servidor
"""

import socket
import sys
import time
import os

from xml.sax import make_parser
from xml.sax.handler import ContentHandler


def AñadirLog(evento):
    fichero = open(cHandler.log, 'a')
    mensaje = str(time.time()) + " " + evento + '\r\n'
    fichero.write(mensaje)
    fichero.close()


class ClientHandler(ContentHandler):


    def __init__(self):
        """
        Constructor. Inicializamos las variables
        """
        self.username = ""
        self.passwd = ""
        self.uaserver_ip = ""
        self.uaserver_puerto = 0
        self.rtp_puerto = 0
        self.regproxy_ip = ""
        self.regproxy_puerto = 0
        self.log = ""
        self.audio = ""

    def startElement(self, name, attrs):
        """
        Método que se llama cuando se abre una etiqueta
        """
        if name == 'account':
            self.username = attrs.get('username', "")
            self.passwd = attrs.get('passwd', "")
        elif name == 'uaserver':
            self.uaserver_ip = attrs.get('ip', "127.0.0.1")
            self.uaserver_puerto = attrs.get('puerto', "")
        elif name == 'rtpaudio':
            self.rtp_puerto = attrs.get('puerto', "")
        elif name == 'regproxy':
            self.regproxy_ip = attrs.get('ip', "")
            self.regproxy_puerto = attrs.get('puerto', "")
        elif name == 'log':
            self.log = attrs.get('path', "")
        elif name == 'audio':
            self.audio = attrs.get('path', "")

if __name__ == "__main__":
    """
    Programa principal
    """
    # Parser
    parser = make_parser()
    cHandler = ClientHandler()
    parser.setContentHandler(cHandler)
    parser.parse(open(str(sys.argv[1])))


    if len(sys.argv) != 4:
        sys.exit("Usage: python uaclient.py config method option")
    #meter error en log

    # Contenido que vamos a enviar si es un INVITE o un BYE
    #MENSAJE = METODO + " sip:" + login + " SIP/2.0\r\n"

    METODO = sys.argv[2]
    IP = cHandler.regproxy_ip
    PORT = cHandler.regproxy_port
    IP_PORT = str(IP) + ':' + str(PORT)
    # Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.connect((IP, int(PORT)))

    if (METODO == "REGISTER"):
		EXPIRES = sys.argv[3]
        #meter "staring" en log

    if (METODO == "INVITE"):
		LOGIN = str(sys.argv[3])
        #print "Enviando: " + MENSAJE
        #my_socket.send(MENSAJE + '\r\n')
    if (METODO == "BYE"):
        #print "Enviando: " + MENSAJE
        #my_socket.send(MENSAJE + '\r\n')

    #meter envio en log

    #Compruebo que el puerto está abierto
    try:
        data = my_socket.recv(1024)
    except socket.error:
        #meter error en log("Error: No server listening at ")

    #meter recepcion en log   
	
	if (data == ("SIP/2.0 200 OK\r\n\r\n")):
		print 'Recibida respuesta REGISTER-- \r\n\r\n', data
	
	data = data.split()
	server_ip = data[13]
    server_port = data[17]
    elif (data[2] == "Trying" + data[5] == "Ringing" + data[8] == "OK"):
        print 'Recibida respuesta INVITE-- \r\n\r\n', data
        #Se envía el ACK
        mensaje_ack = "ACK" + " sip:" + LOGIN + " SIP/2.0\r\n"
        my_socket.send(mensaje_ack + '\r\n')
        data = my_socket.recv(1024)
        print 'Recibida respuesta ACK -- \r\n\r\n', data

        #enviamos audio(RTP)  
		reproducir = ('mp32rtp -i ' + server_ip + ' -p ' + puerto_server +
					  ' < ' + cHandler.audio)
	    print "Listening... ", reproducir
        os.system(reproducir)
        print "Se ha terminado de reproducir"     

    if (METODO == "BYE"):
		LOGIN = str(sys.argv[3])
        print 'Recibida respuesta BYE-- \r\n\r\n', data

   		#meter envio en log

    # Cerramos todo
    my_socket.close()
