import socket

server_socket = socket.socket()
hostname = socket.gethostname()
server_ip = socket.gethostbyname(hostname)
port = 8080 # doesn't have to be 8080, but it's standard

server_socket.bind((hostname, port))
print("Successfully bound server to port ", port)
print("Your IP is: ", server_ip)

name = input("Enter your name: ")
server_socket.listen(1)

connection, address = server_socket.accept()
print("Connected to: ", address[0])

client = (connection.recv(1024)).decode()
print(client + " has connected.")
connection.send(name.encode())

while True:
    message = input("Me: ")
    connection.send(message.encode())
    message = (connection.recv(1024)).decode()
    print(client + ": " + message)