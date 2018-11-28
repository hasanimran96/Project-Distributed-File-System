import os
import socket

# set directory for file server
root = "Root/"


def open_file(file_name):
    fd = open(root + file_name)
    return fd


def close_file(fd):
    fd.close()


def create_file(file_name):
    fd = open(root + file_name, "x")
    return fd


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


def create_directory(directory_name):
    if not os.path.exists(root + directory_name):
        os.mkdir(root + directory_name)
        print("Directory ", directory_name, " Created ")
    else:
        print("Directory ", directory_name, " already exists")


def main():
    print("Project DFS!")

    # create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # get server ip
    # print("Enter server IP")
    # msg = input()
    # host = msg
    host = "127.0.0.1"

    # get server port
    # print("Enter server port")
    # msg = input()
    # port = int(msg)
    port = 9999

    # connection to hostname on the port.
    s.connect((host, port))

    # Receive no more than 1024 bytes
    msg = s.recv(1024)
    print(msg.decode())

    while True:
        print("Write a command to execute or type help")
        command = input()
        if len(command) < 1:
            print("Please write a command or type help")
        elif command[:5] == "hello":
            print("hello from client")
        elif command[:4] == "open":
            open_file(command[5:])
        elif command[:4] == "read":
            s.sendall(command.encode())
            data = s.recv(1024).decode()
            if(data == "sending file"):
                recieve_file(s, command[5:])
                message = read_from_file(command[5:])
                print(message)
            else:
                print(data)
        # elif command_split[0] == "create":
        #     create_file(command_split[1])
        elif command[:5] == "write":
            print("enter message to write")
            msg = input()
            write_to_file(command[6:], msg)
            s.sendall(command.encode())
            send_file(s, command[6:])
        #     s.send(command)
        #     recieve_file(s, command_split[1])
        #     str_temp = " ".join(str(x) for x in command_split[2:])
        #     write_to_file(command_split[1], str_temp)
        #     # add a method to let server know that you are know sending a file
        #     send_file(s, command_split[1])
        # elif command_split[0] == "append":
        #     str_temp = " ".join(str(x) for x in command_split[2:])
        #     append_to_file(command_split[1], str_temp)
        elif command[:4] == "list":
            s.sendall((command).encode())
            data = s.recv(1024).decode()
            while(data[-3:] != "###"):
                data += s.recv(1024).decode()
            print(data[:-3])
        # elif command_split[0] == "mkdir":
        #     create_directory(command_split[1])
        # # elif(command_split[0]=="close"):
        # elif command_split[0] == "exit":
        #     break
        else:
            print("Invalid intruction. Type help")


main()
