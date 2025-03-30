import socket
import threading

def receive_messages(server_socket):
    while True:
        try:
            message = (server_socket.recv(1024)).decode()
            if not message:
                print("Connection closed by the server.")
                break
            print(message)
        except ConnectionResetError:
            print("Connection lost.")
            break

def send_messages(server_socket):
    while True:
        try:
            message = input("Me: ")
            server_socket.send(message.encode())
        except ConnectionResetError:
            print("Connection lost.")
            break

server_socket = socket.socket()
hostname = socket.gethostname()
server_ip = socket.gethostbyname(hostname)
port = 8080

print("This is your IP address: ", server_ip)
server_host = input("Enter your friend's IP address: ")
name = input("Enter your name: ")

server_socket.connect((server_host, port))
server_socket.send(name.encode())
server_name = (server_socket.recv(1024)).decode()
print(server_name + " has connected.")

receive_thread = threading.Thread(target=receive_messages, args=(server_socket,))
send_thread = threading.Thread(target=send_messages, args=(server_socket,))
receive_thread.start()
send_thread.start()
receive_thread.join()
send_thread.join()
server_socket.close()