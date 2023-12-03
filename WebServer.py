import socket
import sys
import os
import argparse
import csv
import time


def create_server_socket(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', port))
    server_socket.listen(1)
    return server_socket


def generate_http_response(status_code, content, file_path):
    #print(content)
    #date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    #last_modified = date
    #file_stats = os.stat(file_path)
    if os.path.exists(file_path):
        file_stats = os.stat(file_path)
        last_modified_timestamp = file_stats.st_mtime
        last_modified = format_timestamp(last_modified_timestamp)
    else:
        last_modified = 'None'
    #last_modified_timestamp = file_stats.st_mtime
    #last_modified = format_timestamp(last_modified_timestamp)
    if isinstance(content, str):
        content = content.encode('utf-8')
    http_response = [
        f"HTTP/1.1 {status_code}",
        f"Content-Length: {len(content)}",
        f"Content-Type: {get_content_type(file_path)}",
        f"Date: {get_current_date()}",
        f"Last-Modified: {last_modified}",
        'Connection: close',
        '\n'
    ]
    header_bytes = '\r\n'.join(http_response).encode('utf-8')
    response = header_bytes + b'\r\n' + content
    #print("HEADER BYTES:", header_bytes)
    return response


def get_content_type(file_path):
    file_extension = os.path.splitext(file_path)[1].lstrip('.').lower()
    text_types = {'html': 'text/html', 'txt': 'text/plain', 'csv': 'text/csv'}
    image_types = {'png': 'image/png', 'jpg': 'image/jpeg', 'gif': 'image/gif'}
    archive_types = {'zip': 'application/zip'}
    document_types = {'doc': 'application/msword', 'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'}

    if file_extension in text_types:
        return text_types[file_extension]
    elif file_extension in image_types:
        return image_types[file_extension]
    elif file_extension in archive_types:
        return archive_types[file_extension]
    elif file_extension in document_types:
        return document_types[file_extension]
    return 'application/octet-stream'


def format_timestamp(timestamp):
    gm_time = time.gmtime(timestamp)
    return time.strftime('%a, %d %b %Y %H:%M:%S GMT', gm_time)


def get_current_date():
    return time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())


def serve_file(requested_file):
    if os.path.isfile(requested_file):
        #print("this is requested file: ", requested_file)
        with open(requested_file, 'rb') as file:
            content = file.read()
        return generate_http_response('200 OK', content, requested_file)
    else:
        #err = 'HTTP/1.1 404 File Not Found'
        #eturn err
        print('HTTP/1.1 404 File Not Found')
        return generate_http_response('404 File Not Found', b'', requested_file)


def write_to_csv(csv_filename, server_ip, server_port, client_ip, client_port, url, status, content_length):
    #status = status.decode('utf-8')
    if type(status) is bytes:
        status = status.decode('utf-8')
    if '501' in status:
        #print("501!!")
        with open(csv_filename, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['Client request served', '4-Tuple:', server_ip, server_port, client_ip, client_port])
            csv_writer.writerow(['Requested URL', url, '501 Not Implemented', 'Bytes sent:', content_length])
    else:
        with open(csv_filename, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['Client request served', '4-Tuple:', server_ip, server_port, client_ip, client_port])
            csv_writer.writerow(['Requested URL', url, status, 'Bytes sent:', content_length])


def write_to_text(text_filename, status, headers):
    #print("THIS IS STATUS IN write_to_text:", status.decode('utf-8'))
    #print("THIS IS HEADERS IN write_to_text:", headers)
    #status = status.decode('utf-8')
    if type(status) is bytes:
        status = status.decode('utf-8')
    if '501' in status:
        with open(text_filename, 'a') as textfile:
            textfile.write(status + '\n' + headers + '\n')
    else:
        with open(text_filename, 'a') as textfile:
            textfile.write(status + '\n' + headers + '\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, help='Port Number', required=True)
    parser.add_argument('-d', '--directory', type=str, required=True)
    # parser.add_argument('-f', '--filename', type=str, required=True)
    args = parser.parse_args()

    if 0 <= args.port < 1024 and args.port != 80:
        print(f"Well-known port number {args.port} entered - could cause a conflict.")
        print(args.port, args.directory)
    elif 1023 < args.port < 49152:
        print(f"Registered port number {args.port} entered - could cause a conflict.")
        print(args.port, args.directory)
    elif 49151 < args.port <= 65535:
        print(f"Terminating program, port number is not allowed.", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(args.directory):
        print("Error: Specified directory does not exist")

    csv_filename = f'SocketOutput.csv'
    text_filename = f'HTTPResponse.txt'

    welcome_socket = create_server_socket(args.port)
    print(f"Welcome socket created: {welcome_socket.getsockname()[0]}, {args.port}")

    while True:
        connection_socket, addr = welcome_socket.accept()
        print(f"Connection socket created: {addr[0]}, {addr[1]}\n")
        data = connection_socket.recv(1024).decode('utf-8')
        request_method, requested_file, _ = data.split(' ', 2)
        response_content = serve_file(os.path.join(args.directory, requested_file[1:]))
        #print(response_content.decode('utf-8'))
        server_ip, server_port = welcome_socket.getsockname()
        client_ip, client_port = addr

        status_line, *rest_headers = response_content.split(b'\r\n', 1)
        # print("This is status_line:", status_line)
        status = status_line.split(b' ')[1].decode('utf-8')
        #http_status = response_content.split(b'\r\n')[0].decode('utf-8').strip()
        content_length_header = rest_headers[0].split(b'Content-Length: ')[1].split(b'\r\n')[0].decode(
            'utf-8').strip()
        response_headers = rest_headers[0].split(b'\r\n', 5)
        heads = response_headers[:5]
        response_heads = ''
        try:
            if request_method == 'GET':
                if response_content:
                    for h in heads:
                        response_heads += h.decode('utf-8') + '\n'
                    http_response = status_line.decode('utf-8') + "\n" + response_heads
                    if status.startswith('2'):
                        try:
                            #response_str = response_content.decode('utf-8')
                            #print(response_content.decode('utf-8'))
                            #print("RESPONSE HEADS:", response_heads)
                            #print("REST HEADERS:", rest_headers)
                            print(http_response)
                            connection_socket.sendall(response_content)
                        except UnicodeDecodeError:
                            response_str = response_content.decode('utf-8', errors='ignore')
                            #print(response_heads)
                            #response_str = response_heads
                            #response_str = "Binary content, unable to decode as UTF-8"
                            connection_socket.sendall(response_heads.encode('utf-8'))
                    write_to_csv(csv_filename, server_ip, server_port, client_ip, client_port, requested_file,
                                 status_line, content_length_header)
                    write_to_text(text_filename, status_line, response_heads)
                    connection_socket.sendall(response_heads.encode('utf-8'))
            else:
                print("HTTP/1.1 501 Not Implemented")
                for h in heads:
                    response_heads += h.decode('utf-8') + '\n'
                #print(response_heads)
                write_to_csv(csv_filename, server_ip, server_port, client_ip, client_port, requested_file,
                             '501 Not Implemented', content_length_header)
                write_to_text(text_filename, '501 Not Implemented', response_heads)
                connection_socket.sendall(response_heads.encode('utf-8'))
        except IOError:
            print("Error in file creation")
        finally:
            connection_socket.close()
            print(f"Connection to {addr[0]}, {addr[1]} is now closed.")


if __name__ == "__main__":
    main()
