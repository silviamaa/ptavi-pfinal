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


def MeterLog(evento):
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
        error = 'Error:  Usage: python uaclient.py config method option'
        MeterLog(error)

    METODO = sys.argv[2]
    OPCION = sys.argv[3]
    IP = cHandler.regproxy_ip
    PORT = cHandler.regproxy_port
    IP_PORT = str(IP) + ':' + str(PORT)
    # Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.connect((IP, int(PORT)))

    if (METODO == "REGISTER"):
        MENSAJE = (METODO + ' sip:' + cHandler.username + ':' +
                   cHandler.uaserver_port + ' ' + 'SIP/2.0\r\n' + 
                   'Expires: ' + OPCION)
        print "Enviando: " + MENSAJE
        my_socket.send(MENSAJE + '\r\n')
		#meter "starting" en log
		inicio = 'Starting...'
		MeterLog(inicio)
    elif (METODO == "INVITE"):      
        SDP = 'Content-Type: application/sdp\r\n\r\n' + 'v=0' + '\n'
        SDP += 'o=' + str(cHandler.username) + ' '
        SDP += str(cHandler.uaserver_ip)
        SDP += '\n' + 's=misesion\n' + 't=0\n' + 'm=audio '
        SDP += str(cHandler.rtp_puerto) + ' RTP'
        MENSAJE = METODO + ' sip:' + OPCION + ' SIP/2.0\r\n' + SDP
        print "Enviando: " + MENSAJE
        my_socket.send(MENSAJE + '\r\n')
    elif (METODO == "BYE"):
        MENSAJE = METODO + ' sip:' + OPCION + ' SIP/2.0\r\n'
        print "Enviando: " + MENSAJE
        my_socket.send(MENSAJE + '\r\n')    
    else:       
        MENSAJE = METODO + 'sip:' + OPCION + ' SIP/2.0\r\n'
        print "Enviando: " + MENSAJE
        my_socket.send(MENSAJE + '\r\n')

    #meter envío en log
    envio = 'Send to: ' + IP_PORT + ':' + MENSAJE + '\r\n'
    MeterLog(envio)

    #Compruebo que el puerto está abierto
    try:
        data = my_socket.recv(1024)
    except socket.error:
        #meter error en log("Error: No server listening at ")
        error = ('Error: no server listening at ' + IP_PORT)
        MeterLog(error)
        sys.exit()
    #meter recepcion en log  
    recepcion = 'Received from ' + IP_PORT + ':' + data + '\r\n'
    EscribirEnLog(recepcion) 
    
    if (data == ("SIP/2.0 200 OK\r\n\r\n")):
        print 'Recibida respuesta REGISTER-- \r\n\r\n', data
    
    data = data.split()
    server_ip = data[13]
    server_port = data[17]
    elif (data[2] == "Trying" + data[5] == "Ringing" + data[8] == "OK"):
        print 'Recibida respuesta INVITE-- \r\n\r\n', data
        #Se envía el ACK
        mensaje_ack = "ACK" + " sip:" + OPCION + " SIP/2.0\r\n"
        my_socket.send(mensaje_ack + '\r\n')
        #meter envío en log
        envio = 'Send to: ' + IP_PORT + ':' + mensaje_ack + '\r\n'
        MeterLog(envio)
        #enviamos audio(RTP)  
        reproducir = ('mp32rtp -i ' + server_ip + ' -p ' + server_port +
                      ' < ' + cHandler.audio)
        print "Listening... ", reproducir
        os.system(reproducir)
        print "Se ha terminado de reproducir"  
		#meter audio en log
		audio = ('Listening...\r\n' + 'Se ha terminado de reproducir')
		MeterLog(audio)   

    if (METODO == "BYE"):
        print 'Recibida respuesta BYE-- \r\n\r\n', data
           #meter "finishing" en log
        despedida = 'finishing.'
        MeterLog(despedida)

    # Cerramos todo
    my_socket.close()
