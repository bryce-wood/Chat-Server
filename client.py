import socket

server_socket = socket.socket()
hostname = socket.gethostname()
server_ip = socket.gethostbyname(hostname)
port = 8080 # doesn't have to be 8080, but it's standard

print("This is your ip address: ", server_ip)
server_host = input("Enter your friend's ip address: ")
name = input("Enter your name: ")

server_socket.connect((server_host, port))

server_socket.send(name.encode())
server_name = (server_socket.recv(1024)).decode()
print(server_name + " has connected.")

while True:
    message = (server_socket.recv(1024)).decode()
    print(server_name + ": " + message)
    message = input("Me: ")
    server_socket.send(message.encode())