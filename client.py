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
    with open(file_name, "rb") as file_to_send:
        for data in file_to_send:
            server_sock.sendall(data)
    print("file sent to server")


def recieve_file(server_sock, file_name):
    with open(file_name, "wb") as file_to_write:
        while True:
            data = server_sock.recv(1024)
            # print data
            if not data:
                break
            # print data
            file_to_write.write(data)
    print("recieved file from server")


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
    print("Enter server IP")
    msg = input()
    host = msg

    # get server port
    print("Enter server port")
    msg = input()
    port = int(msg)

    # connection to hostname on the port.
    s.connect((host, port))

    # Receive no more than 1024 bytes
    msg = s.recv(1024)
    print(msg.decode())

    while True:
        print("Write a command to execute or type help")
        command = input()
        command_split = command.split()
        if len(command_split) < 1:
            print("Please write a command or type help")
        elif command_split[0] == "hello":
            print("hello from client")
        elif command_split[0] == "open":
            open_file(command_split[1])
        elif command_split[0] == "read":
            s.send(command)
            recieve_file(s, command_split[1])
            message = read_from_file(command_split[1])
            print(message)
        elif command_split[0] == "create":
            create_file(command_split[1])
        elif command_split[0] == "write":
            s.send(command)
            recieve_file(s, command_split[1])
            str_temp = " ".join(str(x) for x in command_split[2:])
            write_to_file(command_split[1], str_temp)
            # add a method to let server know that you are know sending a file
            send_file(s, command_split[1])
        elif command_split[0] == "append":
            str_temp = " ".join(str(x) for x in command_split[2:])
            append_to_file(command_split[1], str_temp)
        elif command_split[0] == "list":
            s.sendall("list".encode())
            while True:
                data = s.recv(1024).decode()
                print(data)
                if not data:
                    break
                print(data)
        elif command_split[0] == "mkdir":
            create_directory(command_split[1])
        # elif(command_split[0]=="close"):
        elif command_split[0] == "exit":
            break
        else:
            print("Invalid intruction. Type help")


main()
