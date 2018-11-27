import socket
import threading
import os
import time
import sys

# set directory for file server
root = "Root/"
# set port for server
port = 5556
# set port for server client socket
c_port = 9999
servers_to_connect = [['127.0.0.1', 5555], ['127.0.0.1', 5557]]

# locking mechanism
lock = threading.Lock()

# list of servers connected
servers_connected = []

# list of clients connected
clients_connected = []


def listen_server(serversocket):
    print('listening server thread')
    # queue up to 5 requests
    serversocket.listen(5)
    while True:
        server_sock_accept, addr = serversocket.accept()
        print("Got a connection from %s" % str(addr))
        lock.acquire()
        bool = is_in_servers_to_connect(addr, servers_connected)
        lock.release()
        if bool:
            server_sock_accept.close()
        else:
            print('Listening Connection Successful', addr)
            sock_temp = [addr[0], addr[1], server_sock_accept]
            lock.acquire(True)
            servers_connected.append(sock_temp)
            print(servers_connected)
            lock.release()

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
        clients_connected.append(client_sock_accept)

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
        else:
            print(msg)


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
    for server in servers_connected:
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


def is_in_servers_to_connect(port, list):
    size = len([item for item in list if port[1] == item[1]])
    if size > 0:
        return True
    else:
        return False


def main():

    # create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # get local machine name
    host = socket.gethostname()
    # bind to the port
    server_socket.bind((host, port))
    print("bind socket port: %s" % (port))

    try:
        thread_listen_server = threading.Thread(
            target=listen_server, kwargs={"serversocket": server_socket}
        )
        thread_listen_server.daemon = True
        thread_listen_server.start()
    except:
        print("Error in thread: listen_server")

    # Connection Requests
    for sock in servers_to_connect:
        lock.acquire(True)
        bool = is_in_servers_to_connect(sock, servers_connected)
        lock.release()
        if bool:
            continue
        else:
            print('connecting to:', sock)
            server_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print('server_conn created')
            server_conn.settimeout(3)
            print('set timeout')
            try:
                print('start connect')
                ret = server_conn.connect_ex((sock[0], sock[1]))
                print('connect executed')
                server_conn.settimeout(None)
                if ret == 0:
                    print('connect successful')
                    sock_temp = [sock[0], sock[1], server_conn]
                    lock.acquire(True)
                    servers_connected.append(sock_temp)
                    print('Connect successful')
                    print(servers_connected)
                    lock.release()
            except socket.error:
                print("connect failed on " + sock[0], sock[1])

    # clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # clientsocket.bind((host, c_port))

    # thread_listen_client = threading.Thread(
    #     target=listen_client, kwargs={"clientsocket": clientsocket}
    # )
    # thread_listen_client.daemon = True
    # thread_listen_client.start()

    print(servers_connected)

    while True:
        command = input()
        if(command == 'close' or command == 'exit'):
            sys.exit()


main()
