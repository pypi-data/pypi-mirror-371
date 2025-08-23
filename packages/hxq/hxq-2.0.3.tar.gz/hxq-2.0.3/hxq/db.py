# -*- coding: utf-8 -*-
# @Time    : 2023/4/6 23:38
# @Author  : hxq
# @Software: PyCharm
# @File    : db.py
import time
from hxq.libs.db import DBHelper

__all__ = [
    "DBHelper",
]

if __name__ == '__main__':
    CONFIG = {
        'SQL_CREATOR': r'sqlite3',
        'SQL_DATABASE': r'C:\Users\hxq\Desktop\KucunManager-master\kucun.db'
    }
    db = DBHelper(config=CONFIG)

    # input(db.get_placeholder(2))
    # create_table = '''
    # CREATE TABLE IF NOT EXISTS hxq(
    #    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    #    NAME           TEXT    NOT NULL,
    #    AGE            INT     NOT NULL,
    #    ADDRESS        CHAR(50),
    #    SALARY         REAL
    # );
    # '''
    # db.execute(create_table)

    data_list = []
    for i in range(1000):
        data_list.append((f'test{i}', '#172389', "", "后道", "567", "0"))
    # print(db.get_placeholder())
    sql = f"INSERT INTO goods('name','size','factory','place','price','number') VALUES ({db.get_placeholder(6)})"
    print(sql)
    db.executemany(sql, data_list)
    #
    # r = db.all("select * from hxq")
    # print(r)
    # if isinstance(r, list):
    #     for i in r:
    #         print(i)
    # else:
    #     print(r)
    #
    # print(len(r))
