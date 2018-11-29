import socket
import threading
import os
import time
import sys
import ast

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


def list_local(directory):
    temp_list = os.listdir(directory)
    return temp_list


def list_to_string(list_to_convert):
    list_str = ""
    for item in list_to_convert:
        list_str += item + ","
    list_str = list_str[:-1]
    return list_str


def list_local_file_list(directory):
    del local_file_list[:]
    temp_list = os.listdir(directory)
    for item in temp_list:
        local_file_list.append(item)


def check_if_file_exists(file_name):
    fname = "./" + file_name
    return os.path.isfile(fname)


def create_file(file_name):
    try:
        with open(root + file_name, "x") as fd:
            fd.close()
            return True
    except FileExistsError:
        return False


def send_file(server_sock, file_name):
    with open(root + file_name, 'rb') as fd:
        data = fd.read(1024)
        while data:
            print(data)
            server_sock.sendall(data)
            data = fd.read(1024)
        fd.close()
        server_sock.sendall('###'.encode())


def recieve_file(client_sock, file_name):
    data = client_sock.recv(1024)
    with open(root + file_name, 'wb') as fd:
        while True:
            if data.decode().endswith('###'):
                data = data[:-3]
                fd.write(data)
                break
            fd.write(data)
            data = client_sock.recv(1024)
        fd.close()


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
            temp_list = []
            data = data[:-3]
            split_data = data.split(',')
            for item in split_data:
                lock.acquire(True)
                global_file_list.append([item, server_sock_accept])
                lock.release()
            temp_list = list_local("Root")
            temp_list_str = list_to_string(temp_list)
            msg = temp_list_str + "###"
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
        print(msg)
        if len(msg) < 1:
            socket.close()
        elif msg == "list":
            temp_list = local_file_list
            msg = "list | " + temp_list
            socket.sendall().encode()
        elif msg[:4] == "send":
            socket.sendall(("recieve " + msg[5:]).encode())
            send_file(socket, msg[5:])
        elif msg[:7] == 'recieve':
            recieve_file(socket, msg[8:])
        else:
            print(msg)


def recieve_from_client(socket):
    global global_file_list
    while True:
        command = socket.recv(1024).decode()
        if len(command) < 1:
            socket.close()
        elif command[:4] == "list":
            lock.acquire(True)
            temp_list = global_file_list
            lock.release()
            list_str = ""
            final_list = []
            for item in temp_list:
                if item[0] not in final_list:
                    final_list.append(item[0])
            for item in final_list:
                list_str += item + "\n"
            list_str = list_str[:-1]
            socket.sendall((list_str+"###").encode())
        elif command[:4] == 'read':
            temp_list == global_file_list
            file_here = False
            for item in temp_list:
                if item[0] == command[5:]:
                    file_here = True
                    if item[1] == 'self':
                        socket.sendall(('sending file').encode())
                        send_file(socket, command[5:])
                        break
                    else:
                        item[1].sendall(('send '+command[5:]).encode())
                        time.sleep(5)
                        socket.sendall(('sending file').encode())
                        send_file(socket, command[5:])
                        break
            if(not file_here):
                socket.sendall(('No Such File Exists').encode())
        elif command[:5] == "write":
            recieve_file(socket, command[6:])
        else:
            socket.sendall(("error from server").encode())


def is_in_servers_to_connect(port, list):
    size = len([item for item in list if port[1] == item[1]])
    if size > 0:
        return True
    else:
        return False


def main():
    global local_file_list, servers_connected, servers_to_connect, clients_connected, global_file_list

    list_local_file_list("Root")
    for item in local_file_list:
        global_file_list.append([item, 'self'])

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
                    temp_list = list_local("Root")
                    temp_list_str = list_to_string(temp_list)
                    msg = temp_list_str + "###"
                    lock.acquire(True)
                    server_conn.sendall(msg.encode())
                    lock.release()
                    print('recieve list from connected socket')
                    data = server_conn.recv(1024).decode()
                    while(data[-3:] != "###"):
                        data += server_conn.recv(1024).decode()
                    temp_list = []
                    data = data[:-3]
                    split_data = data.split(',')
                    for item in split_data:
                        lock.acquire(True)
                        global_file_list.append([item, server_conn])
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
            print(local_file_list)


main()
