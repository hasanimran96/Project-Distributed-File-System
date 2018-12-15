import os
import socket
import ast
import subprocess
import sys

# set directory for file server
root = "Root/"


def open_file(file_name):
    fd = open(root + file_name)
    return fd


def close_file(fd):
    fd.close()


def delete_file(file_name):
    if os.path.exists(root + file_name):
        os.remove(root + file_name)
        return True
    else:
        return False


def create_file(file_name):
    try:
        with open(root + file_name, "x") as fd:
            fd.close()
            return True
    except FileExistsError:
        return False


def read_from_file(file_name):
    fd = open(root + file_name, "r")
    message = fd.read()
    return message


def write_to_file(file_name, message):
    fd = open(root + file_name, "w")
    fd.write(message)


def append_to_file(file_name, message):
    fd = open(root + file_name, "a")
    fd.write(message)


def list_files(server_sock, directory):
    while True:
        data = server_sock.recv(1024)
        if not data:
            break
        temp_list = data
    for item in temp_list:
        print(item)


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


def create_directory(directory_name):
    if not os.path.exists(root + directory_name):
        os.mkdir(root + directory_name)
        print("Directory ", directory_name, " Created ")
    else:
        print("Directory ", directory_name, " already exists")


def check_extension(file_name):
    return(file_name.lower().endswith(('.txt', '.c', '.py')))


def main():
    print("Project DFS!")

    # get server ip
    print("Enter server IP")
    msg = input()
    host = msg
    #host = "127.0.0.1"

    # get server port
    print("Enter server port")
    msg = input()
    port = int(msg)
    #port = 9999

    while True:

        # create a socket object
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # connection to hostname on the port.
        s.connect((host, port))

        # Receive no more than 1024 bytes
        msg = s.recv(1024)
        print(msg.decode())

        while True:
            print("Write a command to execute or type help")
            print(">>> ", end='', flush=True)
            command = input()
            if len(command) < 1:
                print("Please write a command or type help")
            # ------------------------------------------------
            elif command[:5] == "hello":
                print("hello from client")
            # ------------------------------------------------
            elif command == "exit":
                s.sendall(command.encode())
                s.close()
                sys.exit()
            # -------------------------------------------------
            elif command[:4] == "open":
                open_file(command[5:])
            # ------------------------------------------------
            elif command[:5] == "close":
                open_file(command[6:])
            # ------------------------------------------------
            elif command[:4] == "read":
                s.sendall(command.encode())
                data = s.recv(1024).decode()
                if(data == 'File not readable'):
                    print(data)
                elif(data == "sending file"):
                    recieve_file(s, command[5:])

                    print("Press 1 to read in terminal")
                    print("Press 2 to read in editor")

                    msg = input()
                    if(int(msg) == 1):
                        message = read_from_file(command[5:])
                        print(message)
                    else:
                        proc = subprocess.Popen(
                            ['leafpad', root + command[6:]])
                        proc.wait()

                elif(data[:10] == "connect to"):
                    print("connecting to a different server")
                    print("please enter the command again")
                    host = data[11:]
                    s.close()
                    break
                else:
                    print(data)
            # ----------------------------------------------
            elif command[:6] == "create":
                if(check_extension(command[5:])):
                    s.sendall(command.encode())
                    data = s.recv(1024).decode()
                    if(data == "File already exists"):
                        print(data)
                    elif(data == "create possible"):
                        print("file created on server")
                    else:
                        print("error in create")
                else:
                    print('No support for this file extension')
            # ----------------------------------------------
            elif command[:6] == "delete":
                s.sendall(command.encode())
                data = s.recv(1024).decode()
                if(data == "file deleted"):
                    print(data)
                elif(data == "file delete error"):
                    print(data)
                elif(data[:10] == "connect to"):
                    host = data[11:]
                    port = 9998
                    s.close()
                    break
                else:
                    print("error in create")
            # -------------------------------------------
            elif command[:5] == "write":
                s.sendall(command.encode())
                data = s.recv(1024).decode()
                if(data == "sending file"):
                    recieve_file(s, command[6:])

                    proc = subprocess.Popen(['leafpad', root + command[6:]])
                    proc.wait()

                    # print("enter message to write")
                    # msg = input()
                    # write_to_file(command[6:], msg)

                    send_file(s, command[6:])
                elif(data[:10] == "connect to"):
                    print("connecting to a different server")
                    print("please enter the command again")
                    host = data[11:]
                    s.close()
                    break
                else:
                    print("error in write")
            # --------------------------------------------
            elif command[:6] == "append":
                s.sendall(command.encode())
                data = s.recv(1024).decode()
                if(data == "sending file"):
                    recieve_file(s, command[7:])

                    proc = subprocess.Popen(['leafpad', root + command[7:]])
                    proc.wait()

                    # print("enter message to write")
                    # msg = input()
                    # append_to_file(command[7:], msg)

                    send_file(s, command[7:])
                elif(data[:10] == "connect to"):
                    print("connecting to a different server")
                    print("please enter the command again")
                    host = data[11:]
                    s.close()
                    break
                else:
                    print("error in append")
            # ------------------------------------------
            elif command == "list":
                s.sendall((command).encode())
                data = s.recv(1024).decode()
                while(data[-3:] != "###"):
                    data += s.recv(1024).decode()
                data = data[:-3]
                print(data)
            # -----------------------------------------
            # elif command_split[0] == "mkdir":
            #     create_directory(command_split[1])
            # # elif(command_split[0]=="close"):
            # elif command_split[0] == "exit":
            #     break
            else:
                print("Invalid intruction. Type help")


main()
