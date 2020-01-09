#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/24 17:22
# @Author  : Py.qi
# @File    : gevent_sock.py
# @Software: PyCharm
import socket,gevent
from gevent import monkey
monkey.patch_all()

class TestGevent(object):

    def server_sock(port):
        s = socket.socket()
        s.bind(('',port))
        s.listen(10)
        while True:
            conn,addr = s.accept()
            gevent.spawn(handle_request,conn)

    def run(i):
        gevent.sleep(2)
        print(i)

    def handle_request(conn):
        try:
            while True:
                data = conn.recv(1024)
                if not data: conn.shutdown(socket.SHUT_WR)
                print('recv:',data.decode())
                conn.send(data)
        except Exception as ex:
            print(ex)
        finally:
            conn.close()

if __name__ == '__main__':
    server_sock(8888)




#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/24 17:35
# @Author  : Py.qi
# @File    : gevent_sockclient.py
# @Software: PyCharm

import socket

HOST = 'localhost'  # The remote host
PORT = 8888  # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
while True:
    #msg = bytes(input(">>:"), encoding="utf8")
    for i in range(50):
        s.send('dddd'.encode())
        data = s.recv(1024)
    # print(data)

        print('Received', repr(data))
    s.close()