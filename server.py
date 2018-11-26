import socket
import threading
import os
import config
import time

# set directory for file server
root = "Root/"

servers = []
clients = []


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
        elif command_split[0] == "read" or command_split[0] == "write":
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

    # create a socket object
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # get local machine name
    host = socket.gethostname()

    server_port = config.SERVER_A_CONFIG['port']
    client_port = config.SERVER_A_CONFIG['client_port']

    # bind to the port
    serversocket.bind((host, server_port))
    clientsocket.bind((host, client_port))

    thread_listen_server = threading.Thread(
        target=listen_server, kwargs={"serversocket": serversocket}
    )
    thread_listen_server.daemon = True
    thread_listen_server.start()

    # SERVER A
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(
            (config.SERVER_B_CONFIG['host'], config.SERVER_B_CONFIG['port']))
        servers.append(sock)
    except:
        print("could not connect to server B")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(
            (config.SERVER_C_CONFIG['host'], config.SERVER_C_CONFIG['port']))
    except:
        print("could not connect to server C")

    # SERVER B
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(
            (config.SERVER_B_CONFIG['host'], config.SERVER_B_CONFIG['port']))
    except:
        print("could not connect to server B")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(
            (config.SERVER_C_CONFIG['host'], config.SERVER_C_CONFIG['port']))
    except:
        print("could not connect to server C")

    # SERVER C
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(
            (config.SERVER_B_CONFIG['host'], config.SERVER_B_CONFIG['port']))
    except:
        print("could not connect to server B")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(
            (config.SERVER_C_CONFIG['host'], config.SERVER_C_CONFIG['port']))
    except:
        print("could not connect to server C")

    thread_listen_client = threading.Thread(
        target=listen_client, kwargs={"clientsocket": clientsocket}
    )
    thread_listen_client.daemon = True
    thread_listen_client.start()

    while True:
        time.sleep(5)
        print("server is awake")


main()
