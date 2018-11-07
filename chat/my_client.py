import socket
import json
from settings import header_struct

# header_struct 定义在 settings.py 里
# struct 模块是一个 python 标准库
# 可以将一部分变量（包括int, 字符串等）打包成类似于 C 语言里结构体一样的东西
# 且长度固定，因此使得头部包长度固定。。。

def recvall(sock, length):
    # 接收客户端发送的包，无论是只有长度的包（头部包）还是正式消息的包（正文）
    # 由于头部包本身长度固定，所以接收的时候传入固定长度的length即可
    # 而在收到头部包之后，根据头部包里的内容（指示了正文有多长）传入length以接收接下来的正文
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
    # block 就是包的意思。。。
    # 可以是头部包，也可以是正文。。。
    data = recvall(sock, header_struct.size)
    block_length = header_struct.unpack(data)[0]  # unpack返回tuple，所以要加索引
    return recvall(sock, block_length)


def put_block(sock, content, info):
    # 发送包，先发头部包，再发正文包
    # 正文里有信息，固定为 100 位
    # 如果不够用空格补齐
    if len(info) <= 99:
        info += ' ' * (99 - len(info))
    content = info + content
    block_length = len(content)
    sock.send(header_struct.pack(block_length))
    sock.send(content.encode("utf-8"))


class Menu:
    def __init__(self):
        self.logged = False
        self.choices = {
            "1": self.login,
            "2": self.register,
            "3": self.query,
            "4": self.chat_with_all,
            "5": self.chat_with_one
        }  # 每个选项都对应了一个函数

    def display_menu(self):
        # 1,2,3三个操作均在输入数字后显示结果，并再次出现这个菜单
        # 4,5两个操作在输入某一字符才退出，不然就一直和别人聊天。。
        print('''
        ----菜单
        
        --------1. 登录
        --------2. 注册
        --------3. 查询在线用户
        --------4. 群聊
        --------5. 与单一用户聊天
        ''')

    def login(self):
        # 如果已经登录过就不能再次登录，由logged标识。。
        if self.logged:
            return

        username = input("请输入用户名")
        password = input("请输入密码")
        # 正文
        login_info = username + " " + password
        # 正文包里的信息，指示服务器接下来要干啥。。当然服务器返回的包里也会有服务器定义的信息。。
        req_dict = {
            "command": 0,
            "from": username,
            "to": "server"
        }
        req_info = json.dumps(req_dict)

        # 发送包
        put_block(sock, login_info, req_info)

        # 接收包
        resp = get_block(sock).decode("utf-8")
        # 取出正文的信息
        info = json.loads(resp[:99].rstrip(" "))
        cmd = info["command"]
        source = info["from"]
        to = info["to"]
        content = resp[99:]
        if content == "success":
            print("登录成功")
            self.logged = True
            return True
        print("登录失败")
        return False

    def query(self):
        pass

    def register(self):
        pass

    def chat_with_all(self):
        pass

    def chat_with_one(self):
        pass

    def run(self):
        while True:
            self.display_menu()
            choice = input("输入选项: ")
            action = self.choices.get(choice)
            if action:
                action()
            else:
                print("无效选项，请重新输入: ")


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.connect(('localhost', 5550))

    Menu().run()
