import socket  # Import socket module
import os
import argparse

# 传输文件的测试代码。。。
# 很久之前写的，虽然能运行但跟不符合现在的代码结构，这一部分最后做吧。。。
def recvall(sock):
    data = b''
    while True:
        more = sock.recv(1024)
        data += more
        if len(more) < 1024:
            break
    return data


def client(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket object

    sock.connect((host, port))

    path = r"C:\Users\zhoulinxuan\PycharmProjects\NetProg\transfer\test.txt"
    filename = os.path.basename(path)
    with open(filename, 'rb') as f:
        content = f.read()
        sock.sendall(content)
        print('Finish reading the file')

    f.close()
    print('Successfully send the file')
    sock.shutdown(socket.SHUT_WR)
    print('connection closed')


def server(interface, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((interface, port))
    sock.listen(1)
    print("listening at", sock.getsockname())

    path = r"./recv.txt"

    while True:
        conn, addr = sock.accept()  # Establish connection with client.
        print('Got connection from', addr)
        print('receiving data...')

        data = recvall(conn)

        with open(path, 'wb') as f:
            print('file opened')

            print('data=%s', data)
            f.write(data)
            print("Server: Done transfer")

        conn.close()


if __name__ == '__main__':
    choices = {'client': client, 'server': server}
    parser = argparse.ArgumentParser(description="transfer file")
    parser.add_argument('role', choices=choices)
    parser.add_argument('host')
    parser.add_argument('-p', metavar='PORT', type=int, default=1060)
    args = parser.parse_args()
    function = choices[args.role]
    function(args.host, args.p)