import socket
import threading
import os
import time
import sys
import ast
import random
import struct

# set directory for file server
root = "Root/"
# set port for server
port = 5557
# set port for server client socket
c_port = 9997
servers_to_connect = [['127.0.0.1', 5556], ['127.0.0.1', 5555]]

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
    global local_file_list
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


def delete_file(file_name):
    if os.path.exists(root + file_name):
        os.remove(root + file_name)
        return True
    else:
        return False


def send_file(server_sock, file_name):
    with open(root + file_name, 'rb') as fd:
        data = fd.read(1024)
        while data:
            # print(data)
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


def check_extension(file_name):
    return(file_name.lower().endswith(('.txt', '.c', '.py')))


# --------------------------------------------------
# functions for recieving and sending files on servers
# --------------------------------------------------


def send_one_message(sock, data):
    length = len(data)
    sock.sendall(struct.pack('!I', length))
    sock.sendall(data)


def recv_one_message(sock):
    lengthbuf = recvall(sock, 4)
    length, = struct.unpack('!I', lengthbuf)
    return recvall(sock, length)


def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf:
            return None
        buf += newbuf
        count -= len(newbuf)
    return buf


def recieve_file_server(client_sock, file_name):
    print("recieve_file_server function")
    with open(root + file_name, 'wb') as fd:
        while True:
            data = recv_one_message(client_sock)
            if data.decode().endswith('EOF'):
                data = data[:-3]
                fd.write(data)
                break
            fd.write(data)
        fd.close()


def send_file_server(server_sock, file_name):
    with open(root + file_name, 'rb') as fd:
        data = fd.read(1024)
        while data:
            send_one_message(server_sock, data)
            data = fd.read(1024)
        send_one_message(server_sock, ('EOF').encode())
        fd.close()

# -----------------------------------------------
# -----------------------------------------------


def listen_server(serversocket):
    global global_file_list, servers_connected
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
                global_file_list.append(
                    [item, server_sock_accept, server_sock_accept.getpeername()])
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
    global clients_connected
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
        msg = "you are connected to server"
        client_sock_accept.sendall(msg.encode())

        thread_recieve = threading.Thread(
            target=recieve_from_client, kwargs={"socket": client_sock_accept}
        )
        thread_recieve.daemon = True
        thread_recieve.start()


def recieve_from_server(socket):
    global global_file_list
    while True:
        msg = socket.recv(1024).decode()
        if not msg:
            socket.close()
        # ----------------------------------------------
        elif len(msg) < 1:
            socket.close()
        # --------------------------------------------
        elif msg[:4] == "send":
            socket.sendall(("recieve " + msg[5:]).encode())
            send_file(socket, msg[5:])
        # -------------------------------------------
        elif msg[:7] == 'recieve':
            recieve_file(socket, msg[8:])
        # ----------------------------------------------
        elif msg[:7] == 'gfl add':
            global_file_list.append([msg[8:], socket, socket.getpeername()])
            print("list updated")
        # --------------------------------------------
        elif msg[:7] == 'gfl del':
            global_file_list.remove([msg[8:], socket, socket.getpeername()])
            print("list updated")
        # --------------------------------------------
        elif msg[:16] == 'replicate_create':
            print(msg)
            if(create_file(msg[17:])):
                print("replicated file created " + msg[17:])
                global_file_list.append([msg[17:], 'self'])
                for servers in servers_connected:
                    servers[2].sendall(('gfl add '+msg[17:]).encode())
            else:
                print("replicated file created error")
        # --------------------------------------------
        elif msg[:16] == 'replicate_update':
            print(msg)
            recieve_file_server(socket, msg[17:])
            print("replicated file recieved " + msg[17:])
        # --------------------------------------------
        elif msg[:16] == 'replicate_delete':
            print(msg)
            if(delete_file(msg[17:])):
                print("replicated file deleted " + msg[17:])
                global_file_list.remove([msg[17:], 'self'])
                for servers in servers_connected:
                    servers[2].sendall(('gfl del '+msg[17:]).encode())
            else:
                print("replicated file delete error")
        # --------------------------------------------
        else:
            print("Invalid instruction --> "+msg)


def replicate_create(file_name):
    server_to_replicate = servers_connected[random.randint(0, 1)][2]
    # server_to_replicate = servers_connected[1][2]
    server_to_replicate.sendall(("replicate_create " + file_name).encode())


def replicate_update(file_name):
    temp_list = global_file_list
    file_here = False
    for item in temp_list:
        if item[0] == file_name:
            file_here = True
            if item[1] != 'self':
                item[1].sendall(("replicate_update "+file_name).encode())
                send_file_server(item[1], file_name)
                print("file sent " + file_name)
    if(not file_here):
        print("file not found on other servers")


def replicate_delete(file_name):
    temp_list = global_file_list
    file_here = False
    for item in temp_list:
        if item[0] == file_name:
            file_here = True
            if item[1] != 'self':
                # index_delete = temp_list.index(item)
                # global_file_list.remove(index_delete)
                item[1].sendall(("replicate_delete "+file_name).encode())
    if(not file_here):
        print("file not found on other servers")


def recieve_from_client(socket):
    global global_file_list
    while True:
        command = socket.recv(1024).decode()
        if len(command) < 1:
            socket.close()
        # ---------------------------------------------------
        elif command == "exit":
            socket.close()
        # ---------------------------------------------------
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
         # ---------------------------------------------------
        elif command[:4] == 'read':
            if(check_extension(command[5:])):
                temp_list = global_file_list
                file_here = False
                for item in temp_list:
                    if item[0] == command[5:]:
                        file_here = True
                        if item[1] == 'self':
                            socket.sendall(('sending file').encode())
                            send_file(socket, command[5:])
                            print("file sent " + command[5:])
                            break
                        else:
                            socket.sendall(
                                ("connect to " + item[2][0]).encode())
                            break
                if(not file_here):
                    socket.sendall(('No Such File Exists').encode())
            else:
                socket.sendall(('File not readable').encode())
        # -------------------------------------------------------
        elif command[:5] == "write":
            temp_list = global_file_list
            file_here = False
            for item in temp_list:
                if item[0] == command[6:]:
                    file_here = True
                    if item[1] == 'self':
                        socket.sendall(('sending file').encode())
                        send_file(socket, command[6:])
                        print("file sent " + command[6:])
                        recieve_file(socket, command[6:])
                        print("file recieved " + command[6:])
                        replicate_update(command[6:])
                        print("file sent to update replicated file")
                        break
                    else:
                        socket.sendall(("connect to " + item[2][0]).encode())
                        break
            if(not file_here):
                socket.sendall(("file doesnot exist").encode())
        # -------------------------------------------------------
        elif command[:6] == "create":
            temp_list = global_file_list
            file_here = False
            for item in temp_list:
                if item[0] == command[7:]:
                    file_here = True
                    socket.sendall(("File already exists").encode())
                    break
            if(not file_here):
                socket.sendall(("create possible").encode())
                if((create_file(command[7:]))):
                    print("file created " + command[7:])
                    global_file_list.append([command[7:], 'self'])
                    for servers in servers_connected:
                        servers[2].sendall(('gfl add '+command[7:]).encode())
                    time.sleep(1)
                    replicate_create(command[7:])
                    print("file sent for replication")
                else:
                    print("create file error")
        # ------------------------------------------------------
        elif command[:6] == 'delete':
            temp_list = global_file_list
            file_here = False
            for item in temp_list:
                if item[0] == command[7:]:
                    file_here = True
                    if item[1] == 'self':
                        if((delete_file(command[7:]))):
                            socket.sendall(('file deleted').encode())
                            global_file_list.remove([command[7:], 'self'])
                            print("deleting replicates of the file")
                            replicate_delete(command[7:])
                            break
                        else:
                            socket.sendall(("file delete error").encode())
                    else:
                        socket.sendall(("connect to " + item[2][0]).encode())
                        break
            if(not file_here):
                socket.sendall(('No Such File Exists').encode())
        # -------------------------------------------------------
        elif command[:6] == "append":
            temp_list = global_file_list
            file_here = False
            for item in temp_list:
                if item[0] == command[7:]:
                    file_here = True
                    if item[1] == 'self':
                        socket.sendall(('sending file').encode())
                        send_file(socket, command[7:])
                        print("file sent " + command[7:])
                        recieve_file(socket, command[7:])
                        print("file recieved " + command[7:])
                        replicate_update(command[7:])
                        print("file sent to update replicated file")
                        break
                    else:
                        socket.sendall(("connect to " + item[2][0]).encode())
                        break
            if(not file_here):
                socket.sendall(("file doesnot exist").encode())
        # ---------------------------------------------------------
        else:
            socket.sendall(("error from server").encode())


def is_in_servers_to_connect(port, list):
    size = len([item for item in list if port[1] == item[1]])
    if size > 0:
        return True
    else:
        return False


def calculate_cost_of_creation():
    temp_list = global_file_list
    count1 = 0
    count2 = 0
    for item in temp_list:
        if item[2] == "self":
            count1 = count1 + 1
        else:
            count2 = count2 + 1
    if(count1 <= count2):
        return True
    else:
        return False


def main():
    global global_file_list, servers_connected

    list_local_file_list("Root")
    for item in local_file_list:
        global_file_list.append([item, 'self'])

    # create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # get local machine name
    host = "127.0.0.1"
    # bind to the port
    server_socket.bind((host, port))
    print("server ip " + str(host))
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
                        global_file_list.append(
                            [item, server_conn, server_conn.getpeername()])
                        lock.release()
                    thread_recieve_main = threading.Thread(
                        target=recieve_from_server, kwargs={
                            "socket": server_conn}
                    )
                    thread_recieve_main.daemon = True
                    thread_recieve_main.start()
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
        # --------------------------------------------
        if(command == 'close' or command == 'exit'):
            sys.exit()
        # -----------------------------------------
        elif(command == 'listg'):
            print(global_file_list)
        # ------------------------------------------
        elif(command == 'listl'):
            print(local_file_list)
        # -----------------------------------------
        else:
            print("invalid command")


main()
