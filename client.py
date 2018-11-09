import os

#set directory for file server
root = "Root/"

def open_file(file_name):
    fd = open(root+file_name)
    return fd

def close_file(fd):
    fd.close()

def create_file(file_name):
    fd = open(root+file_name,'x')
    return fd

def read_from_file(file_name):
    fd = open(root+file_name,'r')
    message = fd.read
    return message

def write_to_file(file_name,message):
    fd = open(root+file_name,'w')
    fd.write(message)

def append_to_file(file_name,message):
    fd = open(root+file_name,'a')
    fd.write(message)

def list_files(directory):
    temp_list = os.listdir(directory)
    for file in temp_list:
        print(file)

def create_directory(directory_name):
    if not os.path.exists(root + directory_name):
        os.mkdir(root + directory_name)
        print("Directory " , directory_name ,  " Created ")
    else:    
        print("Directory " , directory_name ,  " already exists")

list_files("Root")

def main():
    print("Project DFS!")
    print("Write a command to execute or type help")
    command = input()
    command_split = command.split()
    if(command_split[0]=="open"):
        open_file(command_split[1])
    elif(command_split[0]=="read"):
        read_from_file(command_split[1])
    else:
        print("Invalid intruction. Type help")

main()
