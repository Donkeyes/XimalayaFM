from __future__ import unicode_literals
__author__ = 'Vhsal.com'

import gevent
from gevent import monkey;monkey.patch_socket()
from gevent.queue import Queue, Empty
import requests
import sys,os
import random



class DownloadInfo():
    def __init__(self,url,title):
        self.url = url
        self.title = title
        

class DownloadTask(object):
    
    def __init__(self, savePath, header,maxTasks=2):
        self.tasks = Queue()
        self.savePath = savePath
        self.s = requests.session()
        self.header = header
        self.maxTasks = maxTasks
        pass

    def putTask(self, downloadInfo):
        self.tasks.put(downloadInfo)

    def run(self):
        gevent.joinall([gevent.spawn(self.download,i) for i in range(self.maxTasks)])
        print("all task is completed!")

    def download(self, i):
        while not self.tasks.empty():
            try:
                random_download_delay = random.uniform(1, 8)
                gevent.sleep(random_download_delay)
                d = self.tasks.get()
                print("开始下载(%d):%s" % (i+1,d.title))
                r_audio_src = self.s.get(d.url, headers=self.header)
                
                m4a_path = self.savePath + d.title + '.m4a'
                if not os.path.exists(m4a_path):
                    with open(m4a_path, 'wb') as f:
                        f.write(r_audio_src.content)
                        print(d.title + '保存完毕...')
                else:
                    print(d.title + 'm4a已存在')
            except Empty:
                print("task(%d) is completed!" % i+1)
                break
            except:
                print("DownloadTask:run occur other error!")
                break
            
        print("task(%d) is completed,quit!" % i+1)
                


