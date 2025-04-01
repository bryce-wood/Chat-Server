import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

def receive_messages(server_socket, chat_display):
    """Receive messages from the server and display them in the chat window."""
    while True:
        try:
            message = server_socket.recv(1024).decode()
            if not message:
                break
            chat_display.config(state=tk.NORMAL)
            chat_display.insert(tk.END, f"{message}\n")
            chat_display.config(state=tk.DISABLED)
            chat_display.see(tk.END)
        except ConnectionResetError:
            chat_display.config(state=tk.NORMAL)
            chat_display.insert(tk.END, "Connection lost.\n")
            chat_display.config(state=tk.DISABLED)
            chat_display.see(tk.END)
            break

def send_message(server_socket, message_entry, chat_display):
    """Send a message to the server."""
    message = message_entry.get()
    if message.strip():
        chat_display.config(state=tk.NORMAL)
        chat_display.insert(tk.END, f"Me: {message}\n")
        chat_display.config(state=tk.DISABLED)
        chat_display.see(tk.END)
        try:
            server_socket.send(message.encode())
        except ConnectionResetError:
            chat_display.config(state=tk.NORMAL)
            chat_display.insert(tk.END, "Connection lost.\n")
            chat_display.config(state=tk.DISABLED)
            chat_display.see(tk.END)
        message_entry.delete(0, tk.END)

def chat_client(server_socket):
    """Create the chatroom GUI."""
    root = tk.Tk()
    root.title("Chat Client")

    # Chat display area
    chat_display = scrolledtext.ScrolledText(root, state=tk.DISABLED, wrap=tk.WORD, height=20, width=50)
    chat_display.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

    # Message entry field
    message_entry = tk.Entry(root, width=40)
    message_entry.grid(row=1, column=0, padx=10, pady=10)
    message_entry.bind("<Return>", lambda event: send_message(server_socket, message_entry, chat_display))

    # Send button
    send_button = tk.Button(root, text="Send", command=lambda: send_message(server_socket, message_entry, chat_display))
    send_button.grid(row=1, column=1, padx=10, pady=10)

    # Start a thread to receive messages
    threading.Thread(target=receive_messages, args=(server_socket, chat_display), daemon=True).start()

    root.mainloop()

def main():
    server_socket = socket.socket()
    hostname = socket.gethostname()
    server_ip = socket.gethostbyname(hostname)
    port = 8080

    print("This is your IP address: ", server_ip)
    server_host = input("Enter the chatroom's IP address: ")
    name = input("Enter your name: ")

    server_socket.connect((server_host, port))
    server_socket.send(name.encode())

    # Start the GUI chat client
    chat_client(server_socket)

if __name__ == "__main__":
    main()