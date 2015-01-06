#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

import SocketServer
import sys
import os
import time

from xml.sax import make_parser
from xml.sax.handler import ContentHandler

def AñadirLog(evento):
    fichero = open(cHandler.log, 'a')
    mensaje = str(time.time()) + " " + evento + '\r\n'
    fichero.write(mensaje)
    fichero.close()


class ServerHandler(ContentHandler):
    """
    server class
    """

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
            self.account_username = attrs.get('username', "")
            self.account_passwd = attrs.get('passwd', "")
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


    def handle(self):
        client_ip = str(self.client_address[0])
        client_port = str(self.client_address[0])
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente(desde el proxy)
            line = self.rfile.read()
            print line
            line1 = line.split()
            ip = line1[7]
            port = line[11]
            # Si no hay más líneas salimos del bucle infinito
            if not line1:
                break
            if (line1[0] == "INVITE"):
                MENSAJE = ("SIP/2.0 100 Trying\r\n\r\n" +
                           "SIP/2.0 180 Ringing\r\n\r\n" +
                           "SIP/2.0 200 OK\r\n\r\n")
                #contenido SDP
				SDP = 'Content-Type: application/sdp\r\n' + 'v=0' + '\n'
                SDP += 'o=' + str(cHandler.account_un) + ' '
                SDP += str(cHandler.uaserver_ip)
                SDP += '\n' + 's=misesion\n' + 't=0\n' + 'm=audio '
                SDP += str(cHandler.rtp_port) + ' RTP'
                self.wfile.write(MENSAJE + SDP)
                #meter envio en log 
                envio = ("Send to " + client_ip + client_port + MENSAJE + SDP)
                MeterLog(envio)           
            elif (line1[0] == "ACK"):
                #enviamos audio
                reproducir = ('./mp32rtp -i ' + ip + ' -p ' +
                              port + ' < ' + cHandler.audio)
                print "Listening... ", reproducir
                os.system(reproducir)
                print "Se ha terminado de reproducir"
            elif (line1[0] == "BYE"):
                self.wfile.write("SIP/2.0 200 OK\r\n\r\n")
                #meter envio en log
				envio = ("Send to " + client_ip + client_port +
						 "SIP/2.0 200 OK\r\n\r\n")
                MeterLog(envio)   
            elif len(line1) != ("INVITE" or "ACK" or "BYE"):
				print "SIP/2.0 405 Method Not Allowed"
                #meter error en log
				error = ("Send to " + client_ip + client_port +
						 "SIP/2.0 405 Method Not Allowed")
                MeterLog(error) 
            else:
                print "SIP/2.0 400 Bad Request"
                #meter error en log
				error = ("Send to " + client_ip + client_port +
						 "SIP/2.0 400 Bad Request")
                MeterLog(error) 

if __name__ == "__main__":
    # Creamos servidor y escuchamos
    # Parser
    parser = make_parser()
    cHandler = ClientHandler()
    parser.setContentHandler(cHandler)
    parser.parse(open(str(sys.argv[1])))

    if len(sys.argv) != 2:
		sys.exit("Usage: python uaserver.py config")
		#meter error en log
		error = ("Error: Usage: python uaserver.py config")
        MeterLog(error)

    serv = SocketServer.UDPServer((cHandler.uaserver_ip,
                                   int(cHandler.uaserver_port)), EchoHandler)
    print "Listening..."
    serv.serve_forever()
