import socket
import threading

# List to store active client connections
clients = []

def broadcast(message, sender_connection=None):
    """Send a message to all clients."""
    for client in clients:
        if client != sender_connection:
            try:
                client.send(message)
            except:
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
                message = connection.recv(1024).decode()
                if message.startswith("TYPING:"):
                    broadcast(message.encode(), connection)
                elif message.startswith("REACTION:"):
                    # Parse the reaction message
                    try:
                        log_message = f"Reaction received: '{message.strip().split(':')[-1]}' to message: '{message.strip()[message.find(':')+1:message.rfind(':')]}'"
                        print(log_message)  # Log the reaction in the server console
                        broadcast(message.encode(), connection)
                    except ValueError:
                        print("Error: Malformed REACTION message received.")
                else:
                    print(f"{client_name}: {message}")
                    broadcast(f"{client_name}: {message}".encode(), connection)
            except ConnectionResetError:
                break
    finally:
        if connection in clients:
            clients.remove(connection)
        print(f"{client_name} has left the chat.")
        broadcast(f"{client_name} has left the chat.".encode())
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