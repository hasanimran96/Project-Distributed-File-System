import socket
import threading
import os

# set directory for file server
root = "Root/"

server1 = ["localhost", 5555]
server2 = ["localhost", 5555]
server3 = ["localhost", 5555]

servers = []
clients = []


def create_socket():
    # create a socket object
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # get local machine name
    host = socket.gethostname()

    server_port = 9999
    client_port = 9998

    # bind to the port
    serversocket.bind((host, server_port))
    clientsocket.bind((host, client_port))

    return serversocket, clientsocket


def listen_server(serversocket):
    # queue up to 5 requests
    serversocket.listen(5)

    while True:

        server_sock_accept, addr = serversocket.accept()

        print("Got a connection from %s" % str(addr))

        msg = "Thank you for connecting"
        server_sock_accept.send(msg.encode("utf-8"))
        servers.append(server_sock_accept)

        thread_recieve = threading.Thread(
            target=recieve_from_server, kwargs={"socket": server_sock_accept}
        )
        thread_recieve.daemon = True
        thread_recieve.start()


def listen_client(clientsocket):
    # queue up to 5 requests
    clientsocket.listen(5)

    while True:

        client_sock_accept, addr = clientsocket.accept()

        print("Got a connection from %s" % str(addr))

        msg = "Thank you for connecting"
        client_sock_accept.send(msg.encode("utf-8"))
        clients.append(client_sock_accept)

        thread_recieve = threading.Thread(
            target=recieve_from_client, kwargs={"socket": client_sock_accept}
        )
        thread_recieve.daemon = True
        thread_recieve.start()


def recieve_from_server(socket):
    while True:
        msg = socket.recv(1024)
        if len(msg) < 1:
            socket.close()
        elif msg == "list":
            temp_list = list_local("Root")
            msg = "list | " + temp_list
            socket.send()


def recieve_from_client(socket):
    while True:
        command = socket.recv(1024)
        command_split = command.split()
        if len(command_split) < 1:
            socket.close()
        elif command_split[0] == "list":
            list_global(socket)
        elif command == "get":
            send_file(socket, command_split[1])
        else:
            socket.send("error")


def list_local(directory):
    temp_list = os.listdir(directory)
    return temp_list


def list_global(socket):
    for server in servers:
        server.send("list local")


def send_file(client_sock, file_name):
    with open(file_name, "rb") as file_to_send:
        for data in file_to_send:
            client_sock.sendall(data)


def recieve_file(client_sock, file_name):
    with open(file_name, "wb") as file_to_write:
        while True:
            data = client_sock.recv(1024)
            if not data:
                break
            file_to_write.write(data)
            file_to_write.close()


def main():

    # establish a connection
    server_socket, client_socket = create_socket()

    thread_listen_server = threading.Thread(
        target=listen_server, kwargs={"serversocket": server_socket}
    )
    thread_listen_server.daemon = True
    thread_listen_server.start()

    server_socket.connect((server1[0], server1[1]))
    server_socket.connect((server2[0], server2[1]))
    server_socket.connect((server3[0], server3[1]))

    thread_listen_client = threading.Thread(
        target=listen_client, kwargs={"clientsocket": client_socket}
    )
    thread_listen_client.daemon = True
    thread_listen_client.start()


main()
