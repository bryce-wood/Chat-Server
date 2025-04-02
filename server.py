import socket
import threading

# List to store active client connections
clients = []

def broadcast(message, sender_connection=None):
    """
    Send a message to all connected clients except the sender.

    Args:
        message (bytes): The message to broadcast.
        sender_connection (socket): The connection of the sender (optional).
    """
    for client in clients:
        if client != sender_connection:
            try:
                client.send(message)
            except:
                # Remove the client if sending fails
                clients.remove(client)

def handle_client(connection, address):
    """
    Handle communication with a single client.

    Args:
        connection (socket): The client's connection socket.
        address (tuple): The client's address (IP and port).
    """
    print(f"Connected to: {address[0]}")
    try:
        # Receive the client's name
        client_name = connection.recv(1024).decode()
        print(f"{client_name} has joined the chat.")
        broadcast(f"{client_name} has joined the chat.".encode(), connection)
        clients.append(connection)

        while True:
            try:
                # Receive a message from the client
                message = connection.recv(1024).decode()
                if message.startswith("TYPING:"):
                    # Broadcast typing notifications
                    broadcast(message.encode(), connection)
                elif message.startswith("REACTION:"):
                    # Parse and log reaction messages
                    try:
                        reaction = message.rsplit(":",1)[-1]
                        original_message = message.rsplit(":",1)[0].split(":",1)[-1]
                        log_message = f"Reaction received: '{reaction.strip()}' to message: '{original_message.strip()}'"
                        print(log_message)  # Log the reaction in the server console
                        broadcast(message.encode(), connection)
                    except ValueError:
                        print("Error: Malformed REACTION message received.")
                else:
                    # Log and broadcast regular messages
                    print(f"{client_name}: {message}")
                    broadcast(f"{client_name}: {message}".encode(), connection)
            except ConnectionResetError:
                # Handle client disconnection
                break
    finally:
        # Remove the client and notify others
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

# Bind the server to the hostname and port
server_socket.bind((hostname, port))
print("Successfully bound server to port ", port)
print("Your IP is: ", server_ip)

# Start listening for incoming connections
server_socket.listen(5)  # Allow up to 5 pending connections
print("Waiting for connections...")

# Accept clients dynamically
while True:
    connection, address = server_socket.accept()
    client_thread = threading.Thread(target=handle_client, args=(connection, address))
    client_thread.start()