from __future__ import unicode_literals
__author__ = 'Vhsal.com'


import gevent
from gevent import monkey;monkey.patch_socket()
from gevent.queue import Queue, Empty
from task_info import TaskInfo
import utils
import requests
import sys,os
import random
from mp3convert import Mp3Convert,Mp3ConvertTask

class DownloadTask(object):
    
    def __init__(self, savePath, header,maxTasks=2,ext="m4a",convert=True):
        self.tasks = Queue()
        self.savePath = savePath
        self.s = requests.session()
        self.header = header
        self.maxTasks = maxTasks
        self.convert = True if utils.read_ini(key="convert",default="0")=="1" else False
        self.convertTask = None
        self.ext = ext
        pass

    def setExt(self, ext):
        self.ext = ext

    def putTask(self, taskInfo):
        self.tasks.put(taskInfo)
    
    def putTasks(self, tasks):
        for task in tasks:
            self.putTask(task)

    def run(self,title=''):
        p1 = []
        for i in range(self.maxTasks):
            p = gevent.spawn(self.download,i)
            p1.append(p)
            p.start()

        if self.convert:
            self.convertTask = Mp3ConvertTask(taskName='audio convert')
            self.convertTask.runAsync(Mp3Convert(child_path=title.replace(" ","")))

        gevent.joinall(p1)
        print("All download tasks are completed!")
        if self.convertTask != None:
            while not self.convertTask.tasks.empty():
                gevent.sleep(2)
            self.convertTask.terminate()
        

    def download(self, i):
        while not self.tasks.empty():
            r_audio_src = ''
            try:
                random_download_delay = random.uniform(1, 8)
                gevent.sleep(random_download_delay)
                d = self.tasks.get()
                print("开始下载(%d):%s" % (i+1,d.title))
                r_audio_src = self.s.get(d.url, headers=self.header)
                m4a_path = self.savePath + d.title + "." + self.ext
                if not os.path.exists(m4a_path):
                    with open(m4a_path, 'wb') as f:
                        f.write(r_audio_src.content)
                        print(d.title + '保存完毕...')
                        d.url = m4a_path
                        if self.convertTask!=None:
                            self.convertTask.putTask(d)
                else:
                    print(d.title + 'm4a已存在')
            except Empty:
                print("task(%d) is completed!" % i+1)
                break
            except requests.exceptions.ConnectTimeout:
                print("ConnectTimeout:"+r_audio_src)
                break
            except requests.exceptions.ReadTimeout:
                print("ReadTimeout:"+r_audio_src)
                break
            except requests.exceptions.ConnectionError:
                print("ConnectionError:"+r_audio_src)
                break
        print('Download task(%d) quit.' % (i))
            #except:
            #    print("DownloadTask:run occur other error!")
            #    break
            
        print("task(%d) is completed,quit!" % (i+1))
                