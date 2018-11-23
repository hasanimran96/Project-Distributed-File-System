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

    # get local machine name
    host = socket.gethostname()

    port = 9999

    # bind to the port
    serversocket.bind((host, port))

    return serversocket


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


def recieve_from_server(socket):
    while True:
        msg = socket.recv(1024)



def recieve_from_client(socket):
    while True:
        command = socket.recv(1024)
        command_split = command.split()
        if len(command_split) < 1:
            print("Please write a command or type help")
        elif command_split[0] == "list":
            temp_list = list_local("Root")
            socket.send(str(temp_list))
        elif command == "get":
            send_file(socket, command_split[1])
        else:
            socket.send("error")


def list_local(directory):
    temp_list = os.listdir(directory)
    return temp_list


def list_global():
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
    serversocket = create_socket()

    thread_listen = threading.Thread(
        target=listen_server, kwargs={"serversocket": serversocket}
    )
    thread_listen.daemon = True
    thread_listen.start()

    # serversocket.connect((server1[0],server1[1]))
    # serversocket.connect((server2[0],server2[1]))
    # serversocket.connect((server3[0],server3[1]))


main()
