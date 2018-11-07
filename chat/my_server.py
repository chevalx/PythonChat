import socket
import threading
from db.user import Repository, User
import json
from settings import header_struct


def recvall(sock, length):
    blocks = []
    while length:
        block = sock.recv(length)
        if not block:
            raise EOFError('socket closed with {} bytes left'
                           ' in this block'.format(length))
        length -= len(block)
        blocks.append(block)
    return b''.join(blocks)


def get_block(sock):
    data = recvall(sock, header_struct.size)
    block_length = header_struct.unpack(data)[0]
    return recvall(sock, block_length)


def put_block(sock, content, info):
    if len(info) <= 99:
        info += ' ' * (99 - len(info))
        content = info + content
    block_length = len(content)
    sock.send(header_struct.pack(block_length))
    sock.send(content.encode("utf-8"))


# 把whatToSay传给除了exceptNum的所有人
def tellOthers(except_name, content):
    for conn, user in user_dict:
        if user != except_name:
            try:
                resp_dict = {
                    "command": 5,
                    "from": "server",
                    "to": user
                }
                resp_info = json.dumps(resp_dict)
                put_block(conn, content, resp_info)
            except:
               pass


# 登录
def login(conn, info, repo):
    username, password = info.split(" ")
    user = User(username, password)

    # 构造响应
    resp_dict = {
        "command": 5,
        "from": "server",
        "to": username
    }
    resp_info = json.dumps(resp_dict)

    try:
        repo.login(user)
        conn_list.append(conn)
        if username in user_dict.values():
            raise ValueError("该用户已登陆")
        user_dict[conn] = username
        resp_content = "success"
        put_block(conn, resp_content, resp_info)
        return True
    except ValueError as e:
        (resp_content, ) = e.args
        put_block(conn, resp_content, resp_info)
        return False


# 输入要执行的操作
# 解包全部在此完成
def operation(conn):
    repo = Repository(db_file)
    while True:
        try:
            req = get_block(conn).decode("utf-8")
            info = json.loads(req[:99].rstrip(" "))
            cmd = info["command"]
            source = info["from"]
            to = info["to"]
            content = req[99:]
            if cmd == 0:
                login(conn, content, repo)
            elif cmd == 1:
                # TODO 查询用户是否已登录
                pass
            elif cmd == 2:
                # TODO 查询用户是否已登录
                pass
            elif cmd == 3:
                pass
            elif cmd == 4:
                pass
            elif cmd == 5:
                pass

        except (OSError, ConnectionResetError):
            try:
                conn_list.remove(conn)
            except:
                pass
            print(user_dict[conn], '已经离开,还剩下', len(conn_list), '人')
            tellOthers(user_dict[conn], '【系统提示：' + user_dict[conn] + ' 离开聊天室】')
            conn.close()
            return


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 5550))
    sock.listen(5)
    print('服务器', socket.gethostbyname('localhost'), '正在监听 ...')

    # 这里与原来不同，去掉了conn_no, 字典里是 conn: username
    user_dict = dict()  # conn: username
    # 列表里是conn，每个conn就是一个连接。。。
    conn_list = list()

    # 数据库文件
    db_file = "../db/network.db"

    while True:
        connection, addr = sock.accept()
        print('接受一个新的连接', connection.getsockname(), connection.fileno())
        try:
            dialogue_thd = threading.Thread(target=operation, args=(connection,))
            dialogue_thd.setDaemon(True)
            dialogue_thd.start()
        except:
            pass
