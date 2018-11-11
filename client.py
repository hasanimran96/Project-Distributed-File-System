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


def list_files(directory):
    temp_list = os.listdir(directory)
    for file in temp_list:
        print(file)


def create_directory(directory_name):
    if not os.path.exists(root + directory_name):
        os.mkdir(root + directory_name)
        print("Directory ", directory_name, " Created ")
    else:
        print("Directory ", directory_name, " already exists")


def make_socket():
    # create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # get local machine name
    host = socket.gethostname()

    port = 9999

    # connection to hostname on the port.
    s.connect((host, port))

    return s


def main():
    print("Project DFS!")
    print("Write a command to execute or type help")

    # Receive no more than 1024 bytes
    s = make_socket()

    msg = s.recv(1024)
    print(msg.decode("utf-8"))

    while True:

        print("Server says enter your command")
        prompt = input()

        if prompt == "close":
            s.send(prompt.encode("utf-8"))
            s.close()
        else:
            s.send(prompt.encode("utf-8"))

        msg = s.recv(1024)
        print(msg.decode("utf-8"))

    # while True:
    #     command = input()
    #     command_split = command.split()
    #     if len(command_split) < 1:
    #         print("Please write a command or type help")
    #     elif command_split[0] == "open":
    #         open_file(command_split[1])
    #     elif command_split[0] == "read":
    #         message = read_from_file(command_split[1])
    #         print(message)
    #     elif command_split[0] == "create":
    #         create_file(command_split[1])
    #     elif command_split[0] == "write":
    #         str_temp = " ".join(str(x) for x in command_split[2:])
    #         write_to_file(command_split[1], str_temp)
    #     elif command_split[0] == "append":
    #         str_temp = " ".join(str(x) for x in command_split[2:])
    #         append_to_file(command_split[1], str_temp)
    #     elif command_split[0] == "list":
    #         if len(command_split) > 2:
    #             list_files(command_split[1])
    #         else:
    #             list_files("Root")
    #     elif command_split[0] == "mkdir":
    #         create_directory(command_split[1])
    #     # elif(command_split[0]=="close"):
    #     elif command_split[0] == "exit":
    #         break
    #     else:
    #         print("Invalid intruction. Type help")


main()
