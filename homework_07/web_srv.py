import socket
import threading
import os

HOST = '127.0.0.1'
PORT = 8090

DOCUMENT_ROOT = './www'  # root folder for static files


def handle_request(client_socket):
    try:
        request = client_socket.recv(1024).decode()
        headers = request.split('\n')
        method, path, _ = headers[0].split(' ')

        if method in ['GET', 'HEAD']:
            if path == '/':
                path = '/index.html'

            file_path = os.path.join(DOCUMENT_ROOT, path[1:])

            if os.path.exists(file_path):
                with open(file_path, 'rb') as file:
                    content = file.read()

                response = f'HTTP/1.1 200 OK\nContent-Length: {len(content)}\n\n'

                if method == 'GET':
                    response = response.encode() + content
                else:  # HEAD
                    response = response.encode()
            else:
                response = 'HTTP/1.1 404 Not Found\n\nFile Not Found'.encode()

            client_socket.sendall(response)
    finally:
        client_socket.close()


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    print(f'Server is listening on {HOST}:{PORT}')

    while True:
        client_socket, addr = server_socket.accept()
        # print(f'Connection from {addr[0]}:{addr[1]}')
        threading.Thread(target=handle_request, args=(client_socket,)).start()


if __name__ == "__main__":
    start_server()
