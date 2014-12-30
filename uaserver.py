#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

import SocketServer
import sys
import os

ip = sys.argv[1]
puerto = sys.argv[2]
fichero_audio = sys.argv[3]

if len(sys.argv) != 4:
    sys.exit("Usage: python server.py " + ip + " " + puerto + " " +
             fichero_audio)


#Maneja ua.xml
class ServerHandler(SocketServer.DatagramRequestHandler):
    """
    server class
    """

    def __init__(self):
        #variables ua.xml
        self.account_username = ''
        self.account_passwd = ''
        self.uaserver_ip = ''
        self.uaserver_puerto = 0
        self.rtp_puerto = 0
        self.regproxy_ip = ''
        self.regproxy_puerto = 0
        self.log = ''
        self.audio = ''

    def startElement(self, name, attrs):

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
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            line = self.rfile.read()
            print line
            line1 = line.split()

            # Si no hay más líneas salimos del bucle infinito
            if not line1:
                break
            if (line1[0] == "INVITE"):
                self.wfile.write("SIP/2.0 100 Trying\r\n\r\n" +
                                 "SIP/2.0 180 Ringing\r\n\r\n" +
                                 "SIP/2.0 200 OK\r\n\r\n")
            elif (line1[0] == "ACK"):
                #enviamos audio
                reproducir = ('./mp32rtp -i ' + client_ip + ' -p 23032 < ' +
                              fichero_audio)
                print "Listening... ", reproducir
                os.system(reproducir)
                print "Se ha terminado de reproducir"
            elif (line1[0] == "BYE"):
                self.wfile.write("SIP/2.0 200 OK\r\n\r\n")
            elif len(line1) != 3:
                print "SIP/2.0 400 Bad Request"
            else:
                print "SIP/2.0 405 Method Not Allowed"

if __name__ == "__main__":
    # Creamos servidor y escuchamos

    # Parser
    parser = make_parser()
    cHandler = ClientHandler()
    parser.setContentHandler(cHandler)
    parser.parse(open(str(sys.argv[1])))

    serv = SocketServer.UDPServer((ip, int(puerto)), EchoHandler)
    print "Lanzando servidor..."
    serv.serve_forever()
