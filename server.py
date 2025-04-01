import socket
import threading

# List to store active client connections
clients = []

def broadcast(message, sender_connection=None): # must have sender_connection to not relay back to sender 
    """Send a message to all clients, including the sender."""
    for client in clients:
        if (client == sender_connection):
            continue
        try:
            client.send(message)
        except:
            # Remove the client if sending fails
            clients.remove(client)

def handle_client(connection, address):
    """Handle communication with a single client."""
    print(f"Connected to: {address[0]}")
    try:
        client_name = connection.recv(1024).decode()
        print(f"{client_name} has joined the chat.")
        broadcast(f"{client_name} has joined the chat.".encode(), connection)
        clients.append(connection)

        while True:
            try:
                message = connection.recv(1024)
                if not message:
                    break
                decoded_message = message.decode()
                print(f"{client_name}: {decoded_message}")
                broadcast(f"{client_name}: {decoded_message}".encode(), connection)
            except ConnectionResetError:
                break
    finally:
        # Remove the client from the list and notify others
        if connection in clients:
            clients.remove(connection)
        print(f"{client_name} has left the chat.")
        broadcast(f"{client_name} has left the chat.".encode()) # doesnt need connection since it wont relay back since it isnt in clients
        connection.close()

# Server setup
server_socket = socket.socket()
hostname = socket.gethostname()
server_ip = socket.gethostbyname(hostname)
port = 8080

server_socket.bind((hostname, port))
print("Successfully bound server to port ", port)
print("Your IP is: ", server_ip)

server_socket.listen(5)  # Allow up to 5 pending connections
print("Waiting for connections...")

# Accept clients dynamically
while True:
    connection, address = server_socket.accept()
    client_thread = threading.Thread(target=handle_client, args=(connection, address))
    client_thread.start()