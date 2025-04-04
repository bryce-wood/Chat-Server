import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, Toplevel, Label, Button, Menu
import time

def add_reaction(server_socket, message, reaction):
    """
    Send a reaction to the server.

    Args:
        server_socket (socket): The server connection socket.
        message (str): The message being reacted to.
        reaction (str): The reaction emoji.
    """
    server_socket.send(f"REACTION:{message}:{reaction}".encode())

def receive_messages(server_socket, chat_display, typing_label):
    """
    Receive messages and reactions from the server and display them.

    Args:
        server_socket (socket): The server connection socket.
        chat_display (ScrolledText): The chat display widget.
        typing_label (Label): The typing indicator label.
    """
    def clear_typing_label():
        """Clear the typing label after a timeout."""
        time.sleep(3)  # Wait for 3 seconds
        typing_label.config(text="")

    while True:
        try:
            message = server_socket.recv(1024).decode()
            if message.startswith("TYPING:"):
                # Display typing notifications
                typing_label.config(text=message[7:])
                threading.Thread(target=clear_typing_label, daemon=True).start()
            elif message.startswith("REACTION:"):
                # Display reactions
                _, original_message, reaction = message.split(":", 2)
                chat_display.config(state=tk.NORMAL)
                chat_display.insert(tk.END, f"Reaction to '{original_message.strip()}': {reaction}\n")
                chat_display.config(state=tk.DISABLED)
                chat_display.see(tk.END)
            else:
                # Display regular messages
                typing_label.config(text="")  # Clear typing indicator
                chat_display.config(state=tk.NORMAL)
                chat_display.insert(tk.END, f"{message}\n")
                chat_display.config(state=tk.DISABLED)
                chat_display.see(tk.END)
        except ConnectionResetError:
            # Handle server disconnection
            chat_display.config(state=tk.NORMAL)
            chat_display.insert(tk.END, "Connection lost.\n")
            chat_display.config(state=tk.DISABLED)
            chat_display.see(tk.END)
            break

def send_message(server_socket, message_entry, chat_display):
    """
    Send a message to the server.

    Args:
        server_socket (socket): The server connection socket.
        message_entry (Entry): The message entry widget.
        chat_display (ScrolledText): The chat display widget.
    """
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

def notify_typing(server_socket, typing_flag, name):
    """
    Notify the server that the user is typing.

    Args:
        server_socket (socket): The server connection socket.
        typing_flag (list): A flag to track typing status.
        name (str): The user's name.
    """
    if not typing_flag[0]:  # Send typing notification only once per session
        try:
            server_socket.send(f"TYPING:{name} is typing...".encode())
            typing_flag[0] = True
        except:
            pass

def open_emoji_picker(message_entry):
    """
    Open a pop-up window with a grid of emojis.

    Args:
        message_entry (Entry): The message entry widget.
    """
    emoji_window = Toplevel()
    emoji_window.title("Pick an Emoji")
    emojis = ["😊", "😂", "❤️", "👍", "🎉", "😢", "😮", "🔥", "🎶", "🌟"]
    for i, emoji in enumerate(emojis):
        button = Button(emoji_window, text=emoji, font=("Arial", 16), width=3, command=lambda e=emoji: insert_emoji(e, message_entry))
        button.grid(row=i // 5, column=i % 5, padx=5, pady=5)

def insert_emoji(emoji, message_entry):
    """
    Insert an emoji into the message entry field.

    Args:
        emoji (str): The emoji to insert.
        message_entry (Entry): The message entry widget.
    """
    message_entry.insert(tk.END, emoji)

def chat_client(server_socket, name):
    """
    Create the chatroom GUI.

    Args:
        server_socket (socket): The server connection socket.
        name (str): The user's name.
    """
    root = tk.Tk()
    root.title("Chat Client")

    # Make the window resizable
    root.resizable(True, True)

    # Chat display area
    chat_display = scrolledtext.ScrolledText(root, state=tk.DISABLED, wrap=tk.WORD, height=20, width=50)
    chat_display.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

    # Typing indicator
    typing_label = Label(root, text="", fg="gray", font=("Arial", 10))
    typing_label.grid(row=1, column=0, columnspan=3, padx=10, pady=5)

    # Message entry field
    message_entry = tk.Entry(root, width=40)
    message_entry.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
    typing_flag = [False]
    message_entry.bind("<KeyPress>", lambda event: notify_typing(server_socket, typing_flag, name))
    message_entry.bind("<KeyRelease>", lambda event: typing_flag.__setitem__(0, False))
    message_entry.bind("<Return>", lambda event: send_message(server_socket, message_entry, chat_display))

    # Send button
    send_button = tk.Button(root, text="Send", command=lambda: send_message(server_socket, message_entry, chat_display))
    send_button.grid(row=2, column=1, padx=10, pady=10)

    # Emoji picker button
    emoji_button = tk.Button(root, text="😊", command=lambda: open_emoji_picker(message_entry))
    emoji_button.grid(row=2, column=2, padx=10, pady=10)

    # Configure grid weights
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # Right-click menu for reactions
    def on_right_click(event):
        try:
            cursor_index = chat_display.index(f"@{event.x},{event.y}")
            line_start = f"{cursor_index.split('.')[0]}.0"
            line_end = f"{cursor_index.split('.')[0]}.end"
            selected_text = chat_display.get(line_start, line_end).strip()
        except tk.TclError:
            return

        reaction_menu = Menu(root, tearoff=0)
        reactions = ["👍", "❤️", "😂", "😮", "😢"]
        for reaction in reactions:
            reaction_menu.add_command(
                label=reaction,
                command=lambda r=reaction: handle_reaction(server_socket, chat_display, selected_text, r)
            )
        reaction_menu.post(event.x_root, event.y_root)

    chat_display.bind("<Button-3>", on_right_click)

    # Start a thread to receive messages
    threading.Thread(target=receive_messages, args=(server_socket, chat_display, typing_label), daemon=True).start()

    root.mainloop()

def handle_reaction(server_socket, chat_display, message, reaction):
    """
    Handle adding a reaction and displaying it.

    Args:
        server_socket (socket): The server connection socket.
        chat_display (ScrolledText): The chat display widget.
        message (str): The message being reacted to.
        reaction (str): The reaction emoji.
    """
    add_reaction(server_socket, message, reaction)
    chat_display.config(state=tk.NORMAL)
    chat_display.insert(tk.END, f"Reaction to '{message}': {reaction} (You)\n")
    chat_display.config(state=tk.DISABLED)
    chat_display.see(tk.END)

def main():
    """
    Main function to start the chat client.
    """
    server_socket = socket.socket()
    hostname = socket.gethostname()
    server_ip = socket.gethostbyname(hostname)
    port = 8080

    print("This is your IP address: ", server_ip)
    server_host = input("Enter the chatroom's IP address: ")
    name = input("Enter your name: ")

    server_socket.connect((server_host, port))
    server_socket.send(name.encode())

    chat_client(server_socket, name)

if __name__ == "__main__":
    main()