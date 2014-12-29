#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Programa cliente que abre un socket a un servidor
"""

import socket
import sys

# Cliente UDP simple.

# Dirección IP del servidor.
METODO = sys.argv[1]

if len(sys.argv) != 3:
    sys.exit("Usage: python client.py method receiver@IP:SIPport")

#Partimos los argumentos
z = sys.argv[2].split(":")
login = z[-2]
a = sys.argv[2].split("@")
b = a[1].split(":")
IPreceptor = b[-2]
puertoSIP = b[-1]

# Contenido que vamos a enviar si es un INVITE o un BYE
MENSAJE = METODO + " sip:" + login + " SIP/2.0\r\n"

# Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
my_socket.connect((IPreceptor, int(puertoSIP)))

if (METODO == "INVITE"):
    print "Enviando: " + MENSAJE
    my_socket.send(MENSAJE + '\r\n')
if (METODO == "BYE"):
    print "Enviando: " + MENSAJE
    my_socket.send(MENSAJE + '\r\n')
#Compruebo que el puerto está abierto
try:
    data = my_socket.recv(1024)
except socket.error:
    sys.exit("Error: No server listening at " + IPreceptor + " port " +
             puertoSIP)
if (data == ("SIP/2.0 100 Trying\r\n\r\n" + "SIP/2.0 180 Ringing\r\n\r\n" +
             "SIP/2.0 200 OK\r\n\r\n")):
    print 'Recibida respuesta INVITE-- \r\n\r\n', data
    #Se envía el ACK
    mensaje_ack = "ACK" + " sip:" + login + " SIP/2.0\r\n"
    my_socket.send(mensaje_ack + '\r\n')
    data = my_socket.recv(1024)
    print 'Recibida respuesta ACK -- \r\n\r\n', data
if (METODO == "BYE"):
    print 'Recibida respuesta BYE-- \r\n\r\n', data

# Cerramos todo
my_socket.close()
