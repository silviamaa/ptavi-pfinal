#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Clase (y programa principal) para un servidor
"""

import SocketServer
import sys
import time

puerto = sys.argv[1]

dicc_usuario = {}


class SIPRegisterHandler(SocketServer.DatagramRequestHandler):

    """
    Registro SIP
    """

    def handle(self):
        self.wfile.write("SIP/1.0 200 OK\r\n\r\n")
        ip = str(self.client_address[0])
        puerto = str(self.client_address[1])
        hora = time.time()
        while 1:
            line = self.rfile.read()
            line1 = line.split()
            line2 = line1[1]
            line3 = line2.split(":")
            user = line3[1]
            dicc_usuario[user] = ip
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
            if not line or "[""]":
                break
    """
    Registrar cliente con ip y hora
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
    # Creamos servidor de eco y escuchamos
    serv = SocketServer.UDPServer(("", int(puerto)), SIPRegisterHandler)
    print "Lanzando servidor..."
    serv.serve_forever()
