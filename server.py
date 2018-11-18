import socket

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


def recieve_from_server(socket):
    while True:

        msg = socket.recv(1024)
        if len(msg) == 0:
            socket.close()
        elif msg.decode("utf-8") == "close":
            socket.close()
        else:
            if msg.decode("utf-8") == "download":
                msg = "Here is your downloaded file haha"
                socket.send(msg.encode("utf-8"))
            else:
                socket.send(msg)


def main():

    # establish a connection
    serversocket = create_socket()
    # clientsocket =  listen_server(serversocket)


main()
