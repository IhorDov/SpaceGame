import threading
import threading
import socket

'''Here I make server'''

host = "127.0.0.1"
port = 50_000
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()
clients = []
aliases = []


def broadcast(message):
    for client in clients:
        client.send(message)

# Function to handle clients connection


def handle_client(client):
    while True:
        try:
            message = client.recv(1024)
            broadcast(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            alias = aliases[index]
            broadcast(f"{alias} has left the chat room!".encode(
                "utf-8"))  # encode makes byte from string
            aliases.remove(alias)
            break

# Main function to receive the clients connection


def receive():
    while True:
        print("Server is running and listening for ...")
        # accept method run consently on the server and wait for any connections from the client
        client, address = server.accept()
        print(f"Connection is established with {str(address)}")
        client.send("alias?".encode("utf-8"))
        alias = client.recv(1024)
        aliases.append(alias)
        clients.append(client)
        print(f"The alias of this client is {alias}".encode("utf-8"))
        broadcast(f"{alias} has connected to the chat room".encode("utf-8"))
        client.send("You are now connected!".encode("utf-8"))

        thread = threading.Thread(target=handle_client, args=(client, ))
        thread.start()


# if __name__ == '__main__':

#     receive()
