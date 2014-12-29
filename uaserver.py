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


class EchoHandler(SocketServer.DatagramRequestHandler):
    """
    server class
    """

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
    # Creamos servidor de eco y escuchamos
    serv = SocketServer.UDPServer((ip, int(puerto)), EchoHandler)
    print "Lanzando servidor UDP..."
    serv.serve_forever()
