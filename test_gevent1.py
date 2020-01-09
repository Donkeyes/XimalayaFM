import socket,gevent
from gevent import monkey
monkey.patch_all( thread=False)

class TestGevent1(object):

    def run(self,i):
        gevent.sleep(2)
        print(i)

if __name__ == "__main__":
    t = TestGevent1()

    gevent.joinall([gevent.spawn(t.run, i) for i in range(2)])
    print("------------")