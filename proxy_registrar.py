#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Clase (y programa principal) para un servidor
"""

import socket
import SocketServer
import sys
import time
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

dicc_usuario = {}


def MeterLog(evento):
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
            line2 = line1[1]
            line3 = line2.split(":")
            if line1[0] == "REGISTER":
                user = str(line3[1])
                dicc_usuario[user] = ip
                port = int(line3[2])
                IP_PORT = str(ip) + ':' + str(port)
                if line1[4] == '0':
                    if user in dicc_usuario:
                        del dicc_usuario[user]
                        mensaje = "SIP/2.0 200 OK"
                        mensaje2 = "El usuario se ha borrado"
                        self.wfile.write(mensaje + '\r\n\r\n')
                        self.wfile.write(mensaje2 + '\r\n')
                        envio = ('Send to: ' + IP_PORT + ':' + mensaje +
                                 ' ' + mensaje2 + '\r\n')
                        MeterLog(envio)

                else:
                    hora_actualizada = hora + int(line1[4])
                    #añado valor y tiempo a la clave del dicc_usuario
                    dicc_usuario[user] = (ip + ',' + str(port) + ',' +
                                          str(hora_actualizada))
                    self.register2file()
                    mensaje = "SIP/2.0 200 OK\r\n\r\n"
                    self.wfile.write(mensaje)
                    envio = 'Send to: ' + IP_PORT + ':' + mensaje + '\r\n'
                    MeterLog(envio)

            else:
                #busco si el usuario existe y envío el mensaje, si no, "envío"
                #"404 user not found"
                user = str(line3[1])
                if user in dicc_usuario:
                    if (line1[0] == "INVITE" or "ACK" or "BYE"):
                        my_socket = socket.socket(socket.AF_INET,
                                                  socket.SOCK_DGRAM)
                        my_socket.setsockopt(socket.SOL_SOCKET,
                                             socket.SO_REUSEADDR, 1)
                        my_socket.connect((ip, int(dicc_usuario[user][1])))
                        my_socket.send(line)
                        print "Enviando: " + line
                        #meter envío en log
                        envio = ('Send to: ' + str(ip) + ':' +
                                 str(dicc_usuario[user][1]) + ':' + line +
                                 '\r\n')
                        MeterLog(envio)
                        if (line1[0] == "INVITE" or "BYE"):
                            #Compruebo que el puerto está abierto
                            try:
                                data = my_socket.recv(1024)
                                print 'Recibida respuesta-- \r\n\r\n', data
                            except socket.error:
                                #meter error en log
                                error = ('Error: no server listening at ' +
                                         str(ip) + ':' +
                                         str(dicc_usuario[user][1]))
                                MeterLog(error)
                                sys.exit()
                                my_socket.close()
                            #meter recepcion en log
                            recepcion = ('Received from ' + str(ip) + ':' +
                                         str(dicc_usuario[user][1]) + ':' +
                                         data + '\r\n')
                            MeterLog(recepcion)
                            #Envio al user agent el mensaje que recibo
                            print ("Enviando: " + data)
                            self.wfile.write(data)
                            #meter envio en log
                            envio = ('Send to: ' + str(ip) + ':' +
                                     str(dicc_usuario[user][1]) + ':' +
                                     data + '\r\n')
                            MeterLog(envio)
                    else:
                        print "SIP/2.0 405 Method Not Allowed"
                        #meter error en log
                        error = ("Send to " + str(ip) + ':' +
                                 str(dicc_usuario[user][1]) + ':' +
                                 "SIP/2.0 405 Method Not Allowed")
                        MeterLog(error)
                else:
                    print "SIP/2.0 404 user not found"
                    #meter error en log
                    error = ("Send to " + str(ip) + ':' +
                             str(dicc_usuario[user][1]) + ':' +
                             "SIP/2.0 404 user not found")
                    MeterLog(error)
            if not line or "[""]":
                break

    """
    Registrar al usuario con + IP + PORT + fecha de registro + Expires
    """
    def register2file(self):
        registered = open(cHandler.registro_usuarios, "w")
        registered.write('User' + "\t" + 'IP' + "\t" + 'PORT' + "\t" +
                         'Expires' + '\n')
        for user, valor in dicc_usuario.items():
            ip = valor.split(',')[0]
            port = valor.split(',')[1]
            hora_actual = time.strftime('%Y-%m-%d %H:%M:%S',
                                        time.gmtime(time.time()))
            registered.write(user + "\t" + ip + "\t" + port + "\t" +
                             hora_actual + "\n")


if __name__ == "__main__":

    """
    Programa principal
    """

    # Parser
    parser = make_parser()
    cHandler = ProxyRegisHandler()
    parser.setContentHandler(cHandler)
    parser.parse(open(str(sys.argv[1])))

    if len(sys.argv) != 2:
        sys.exit("Usage: python proxy_registrar.py config")
        #meter error en log
        error = ("Error: Usage: python proxy_registrar.py config")
        MeterLog(error)

    # Creamos servidor y escuchamos
    serv = SocketServer.UDPServer((str(cHandler.s_ip),
                                   int(cHandler.s_port)), Handler)

    print "Server MiServidorProxy listening at port " + cHandler.s_port + "..."
    frase = ("Server MiServidorProxy listening at port " + cHandler.s_port +
             "...")
    MeterLog(frase)
    serv.serve_forever()
