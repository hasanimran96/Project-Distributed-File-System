import socket
import threading
import os
import time
import sys

# set directory for file server
root = "Root/"
# set port for server
port = 5555
# set port for server client socket
c_port = 9999
servers_to_connect = [['127.0.0.1', 5556], ['127.0.0.1', 5557]]

# locking mechanism
lock = threading.Lock()

# list of servers connected
servers_connected = []

# list of clients connected
clients_connected = []

# list local
local_file_list = []
# list global
global_file_list = []


def listen_server(serversocket):
    global servers_connected, global_file_list
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
            lock.release()
            data = server_sock_accept.recv(1024).decode()
            while(data[-3:] != "###"):
                data += server_sock_accept.recv(1024).decode()
            lock.acquire(True)
            global_file_list.append(data[:-3])
            lock.release()
            list_str = " ".join(list_local("Root"))
            msg = str(addr[1]) + " " + list_str + " " + "###"
            lock.acquire(True)
            server_sock_accept.sendall(msg.encode())
            lock.release()

        thread_recieve = threading.Thread(
            target=recieve_from_server, kwargs={"socket": server_sock_accept}
        )
        thread_recieve.daemon = True
        thread_recieve.start()


def listen_client(clientsocket):
    global clients_connected, global_file_list
    print('client listening thread')
    # queue up to 5 requests
    clientsocket.listen(5)
    while True:
        client_sock_accept, addr = clientsocket.accept()
        print("Got a connection from %s" % str(addr))
        print('Listening Connection Successful', addr)
        sock_temp = [addr[0], addr[1], client_sock_accept]
        lock.acquire(True)
        clients_connected.append(sock_temp)
        lock.release()
        msg = "you are connected to server" + str(port)
        client_sock_accept.sendall(msg.encode())

        thread_recieve = threading.Thread(
            target=recieve_from_client, kwargs={"socket": client_sock_accept}
        )
        thread_recieve.daemon = True
        thread_recieve.start()


def recieve_from_server(socket):
    global local_file_list
    while True:
        msg = socket.recv(1024).decode()
        if len(msg) < 1:
            socket.close()
        elif msg == "list":
            temp_list = local_file_list
            msg = "list | " + temp_list
            socket.sendall().encode()
        else:
            print(msg)


def recieve_from_client(socket):
    global global_file_list
    while True:
        command = socket.recv(1024).decode()
        if len(command) < 1:
            socket.close()
        elif command == "list":
            socket.sendall((str(global_file_list)).encode())
        elif command == "read" or command == "write":
            send_file(socket, command[5:])
        else:
            socket.sendall("error").encode()


def list_local(directory):
    temp_list = os.listdir(directory)
    return temp_list


def send_file(client_sock, file_name):
    with open(file_name, "rb") as file_to_send:
        for data in file_to_send:
            client_sock.sendall(data).encode()


def recieve_file(client_sock, file_name):
    with open(file_name, "wb") as file_to_write:
        while True:
            data = client_sock.recv(1024).decode()
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
    global local_file_list, servers_connected, servers_to_connect, clients_connected, global_file_list
    # create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # get local machine name
    host = '127.0.0.1'
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

    # Connection Requests to servers
    for sock in servers_to_connect:
        lock.acquire(True)
        bool = is_in_servers_to_connect(sock, servers_connected)
        lock.release()
        if bool:
            continue
        else:
            print('connecting to:', sock)
            server_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_conn.settimeout(3)
            try:
                print(sock)
                ret = server_conn.connect_ex((sock[0], sock[1]))
                server_conn.settimeout(None)
                if ret == 0:
                    sock_temp = [sock[0], sock[1], server_conn]
                    lock.acquire(True)
                    servers_connected.append(sock_temp)
                    print('Connect successful')
                    lock.release()
                    print('sending list')
                    list_str = " ".join(list_local("Root"))
                    msg = str(sock[1]) + " " + list_str + " " + "###"
                    lock.acquire(True)
                    server_conn.sendall(msg.encode())
                    lock.release()
                    print('recieve list from connected socket')
                    data = server_conn.recv(1024).decode()
                    while(data[-3:] != "###"):
                        data += server_conn.recv(1024).decode()
                    lock.acquire(True)
                    global_file_list.append(data[:-3])
                    lock.release()
            except socket.error:
                print("connect failed on " + sock[0], sock[1])

    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    clientsocket.bind((host, c_port))

    thread_listen_client = threading.Thread(
        target=listen_client, kwargs={"clientsocket": clientsocket}
    )
    thread_listen_client.daemon = True
    thread_listen_client.start()

    while True:
        command = input()
        if(command == 'close' or command == 'exit'):
            sys.exit()
        if(command == 'listg'):
            print(global_file_list)
        if(command == 'listl'):
            temp_list = list_local('Root')
            print(temp_list)


main()
