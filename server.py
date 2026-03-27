import socket
import threading

HOST = "127.0.0.1"
PORT = 4040

clients = []


def broadcast(message, sender):
    for client in clients:
        if client != sender:

            try:
                client.send(message)
            except:
                clients.remove(client)


                def handle_client(client):
                    while True:
                        try:
                            msg = client.recv(1024)

                            if not msg:
                                break
                            broadcast(msg, client)

                        except:
                            break
                        clients.remove(client)
                        client.close()


                        def start_server():
                            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            server.bind((HOST, PORT))
                            server.listen()

                            while True:

                                client, addr = server.accept()

                                clients.append(client)

                                thread = threading.Thread(target=handle_client, args=(client,))
                                thread.start()


                                start_server()