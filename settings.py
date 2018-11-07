import struct
import json

# 字段设计
#
# command:
#     login 0
#     register 1
#     query 2
#     chat 3
#     file 4
#     info 5
# from:
#     server/username
# to:
#     all/server/username

block_info = {
    "command": 0,
    "from": "Chandler",
    "to": "Monica"
}

header_struct = struct.Struct('!I')

if __name__ == '__main__':
    json_info = json.dumps(block_info)
    print(json_info)
    print(type(json.loads(json_info)))