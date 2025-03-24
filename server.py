import socket
import sys
import time

server_socket = socket.socket()
hostname = socket.gethostname()
server_ip = socket.gethostbyname(hostname)
port = 8080 # doesn't have to be 8080, but it's standard