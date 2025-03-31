import socket
import threading
import curses

def receive_messages(server_socket, chat_window, lock):
    """Receive messages from the server and display them in the chat window."""
    while True:
        try:
            message = server_socket.recv(1024).decode()
            if not message:
                break
            with lock:
                chat_window.addstr(f"{message}\n")
                chat_window.refresh()
        except ConnectionResetError:
            with lock:
                chat_window.addstr("Connection lost.\n")
                chat_window.refresh()
            break

def send_messages(server_socket, input_window, chat_window, lock):
    """Send messages to the server."""
    while True:
        with lock:
            input_window.clear()
            input_window.addstr("Me: ")
            input_window.refresh()
        message = input_window.getstr().decode()
        with lock:
            chat_window.addstr(f"Me: {message}\n")  # Display the user's message in the chat window
            chat_window.refresh()
        try:
            server_socket.send(message.encode())
        except ConnectionResetError:
            with lock:
                chat_window.addstr("Connection lost.\n")
                chat_window.refresh()
            break

def chat_client(stdscr, server_socket):
    """Main function to handle the chatroom interface."""
    curses.curs_set(1)  # Enable the cursor
    stdscr.clear()

    # Create windows for chat and input
    height, width = stdscr.getmaxyx()
    chat_window = curses.newwin(height - 3, width, 0, 0)
    input_window = curses.newwin(3, width, height - 3, 0)

    # Lock for thread-safe updates to the chat window
    lock = threading.Lock()

    # Start threads for receiving and sending messages
    receive_thread = threading.Thread(target=receive_messages, args=(server_socket, chat_window, lock))
    send_thread = threading.Thread(target=send_messages, args=(server_socket, input_window, chat_window, lock))
    receive_thread.daemon = True
    send_thread.daemon = True
    receive_thread.start()
    send_thread.start()

    # Wait for threads to finish
    receive_thread.join()
    send_thread.join()

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

    # Start the curses interface
    curses.wrapper(chat_client, server_socket)

if __name__ == "__main__":
    main()