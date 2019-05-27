"""
 Implements a simple HTTP/1.0 Server

"""
import socket
from pathlib import Path  # Get extention suffix
from threading import Thread, Timer
from cache import *
from sqlite import *

file_types = [".jpg", ".jpeg", ".png", ".pdf", ".gif", ".mp3", ".mp4"]

# Define socket host and port
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8000

# Create socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen(1)
print('Listening on port %s ...' % SERVER_PORT)


def check_is_close_connection_header(request):
    """ Check if connection is closed
    :param request: Header request form client
    """
    if "Connection: close" in request:
        return True
    else:
        return False


def close_client_connection(client_connection):
    """Method to close client connection"""
    client_connection.close()


def accept_incoming_connections():
    """
    Set up incoming clients.
    """
    while True:
        try:
            connected = True
            while connected:
                # Wait for client connections
                client_connection, client_address = server_socket.accept()
                # print("O client {} fez um pedido\n\n".format(client_address))

                # add_ip_client(client_address)
                timer = Timer(10, close_client_connection, args=(client_connection,))
                timer.start()
                # Handle client request
                request = client_connection.recv(1024).decode()
                timer.cancel()
                is_closed_connection = check_is_close_connection_header(request)
                # Check and start count to close connection if don't have requests in 10 seconds
                if request != "":
                    # Receives content from client
                    content = handle_request(request, client_address)

                    # Prepare byte-encoded HTTP response
                    response = handle_response(content)

                    # Return HTTP response
                    client_connection.sendall(response)

                    if is_closed_connection == True:
                        break
            client_connection.close()
            connected = False
        except:
            connected = False


def write_logs(ip_address, url_resquest):
    method = url_resquest[0]
    folder = url_resquest[1]
    http_version = url_resquest[2]

    formated_request = method + " " + folder + " " + http_version

    with open("logs.txt", "a") as myfile:
        myfile.write("{} - {} {}\n".format(strftime("%Y-%m-%d %H:%M:%S", gmtime()), ip_address, formated_request))


def handle_request(request, client_address):
    # Parse headers
    # print(request)
    headers = request.split('\n')
    get_content = headers[0].split()

    host = request.split("\n")[1].split(" ")[1]
    url = get_content[1]

    method = get_content[0]

    if method == "GET":

        filename = get_content[1]
        if filename == "/favicon.ico":
            return ''

        if filename == "/":
            filename = "/index.html"

        files_suffix = Path(filename).suffix
        write_logs(reorganize_ip(client_address), get_content)  # Write to log file

        content_in_cache = check(url)
        # print("Content in cache\n", content_in_cache)

        if content_in_cache is None:  # Check if content of cache is None, and update the new content
            time.sleep(1)
            update(url, read_file_from_disk(filename, files_suffix, request))
            return read_file_from_disk(filename, files_suffix, request)
        else:
            return content_in_cache

    if method == "POST":

        name = request.split("\n\r")[1].split("&")[0].split("=")[1]
        password = request.split("&")[1].split("=")[1]

        from_form = get_content[1]
        what_form = from_form.split("public")[1].split("/")[1]

        if "form.html" in what_form:
            json = {"fullname": name,
                    "password": password}

            return str(json)
        else:
            ip_client = reorganize_ip(client_address)
            login_user(name, password, ip_client)
            return read_file_from_disk("/index.html", ".html", request)


def reorganize_ip(client_address):
    get_client_ip = str(client_address)
    ip_client = get_client_ip.split(",")[0].split("'")[1]
    return ip_client


def read_file_from_disk(filename, files_suffix, request):
    is_private_folder = request.split("/")[1]
    try:
        if is_private_folder == "private":
            # if is_user_logged == True:
            #     with open('htdocs' + filename) as fin:
            #         return fin.read()
            # else:
            is_private_folder = ""
            response = 'Acesso Negado'
            return response
        elif files_suffix in file_types:
            with open('htdocs' + filename, "rb") as fin:
                return fin.read()
        else:
            # Return file contents
            with open('htdocs' + filename) as fin:
                return fin.read()
    except FileNotFoundError:
        return None


def handle_response(content):
    """Returns byte-encoded HTTP response."""

    # Get current time
    time_now = strftime("%Y-%m-%d %H:%M:%S", gmtime())

    # Build HTTP response
    if isinstance(content, bytes):  # Case media
        response = 'HTTP/1.1 200 OK\n' \
                   'Content-length: ' + str(len(content)) + '\n' \
                                                            'Date: {now} '.format(now=time_now) + '\n\n'
        response = response.encode()
        response += content
    elif content:  # Case submit from form
        if content == "Acesso Negado":
            response = 'HTTP/1.1 403 Forbidden\n\n'
        elif content.endswith("}"):
            response = 'HTTP/1.1 200 OK\n' \
                       'Content-length: ' + str(len(content)) + '\n' \
                                                                'Date: {now} '.format(now=time_now) + '\n' \
                                                                                                      'Content-type: text/json\n\n'
            response += content
            return response.encode()
        else:  # Last case to normal html pages
            response = 'HTTP/1.1 200 OK\n' \
                       'Content-length: ' + str(len(content)) + '\n' \
                                                                'Date: {now} '.format(now=time_now) + '\n' \
                                                                                                      'Content-type: text/html\n\n'

        response += content
        response = response.encode()
    else:
        response = 'HTTP/1.1 404 NOT FOUND\n\nFile Not Found'.encode()

    # Return encoded response
    return response


if __name__ == "__main__":
    server_socket.listen(30)  # Listens for 30 connections at max.
    print("Waiting for connection...")
    thread_accept_incoming_connections = Thread(name="Accept Incomming connection", target=accept_incoming_connections)
    thread_accept_incoming_connections.start()  # Starts the infinite loop.
    thread_accept_incoming_connections.join()
    server_socket.close()
