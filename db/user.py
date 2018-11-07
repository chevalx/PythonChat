import sqlite3


class User:
    # TODO 给名字加上长度限制
    def __init__(self, name=None, password=None):
        self.name = name
        if len(password) < 6:
            raise ValueError("密码过短")
        self.password = password


class Repository:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)

    def select_others(self, names):
        cursor = self.conn.cursor()
        sql = "SELECT name from main.user where id in (%s)" % ','.join('?'*len(names))
        cursor.execute(sql, names)

    def insert_user(self, user):
        cursor = self.conn.cursor()
        try:
            sql = "INSERT INTO main.user(name, password) VALUES (?, ?)"
            cursor.execute(sql, (user.name, user.password))
            row_id = cursor.lastrowid
        except sqlite3.IntegrityError:
            self.conn.rollback()
            raise ValueError("用户名已存在")
        self.conn.commit()
        cursor.close()
        return row_id

    def select_user_by_name(self, name):
        # TODO 添加异常，没有该用户的情况
        cursor = self.conn.cursor()
        sql = "SELECT name, password from main.user where name=(?)"
        cursor.execute(sql, (name,))
        row = cursor.fetchone()
        cursor.close()
        return row

    def login(self, user: User):
        row = self.select_user_by_name(user.name)
        if user.password != row[1]:
            raise ValueError("Password is not correct.")
        print(row)
        return

    def register(self, user: User):
        latest_id = self.insert_user(user)
        print(latest_id)
        return latest_id

    def close(self):
        self.conn.close()


# 以下部分测试用
if __name__ == '__main__':
    repo = Repository()
    testUser = User("test4", "12345678")
    repo.register(testUser)
