# -*- coding:utf-8 -*-
from __future__ import unicode_literals
__author__ = 'Vhsal.com'

import gevent
from gevent import monkey;monkey.patch_all( thread=False)
import os,sys,platform
import utils
import time
from configparser import ConfigParser
from task_info import TaskInfo
import multiprocessing
from multiprocessing import Process,Queue
from multiprocessing.pool import ThreadPool

class Mp3Convert(object):
    def __init__(self, ffmpeg=None, output_path=None, output_format=None, output_kbs=None,child_path=''):

        if ffmpeg is None:
            default = os.getcwd() + ("\\ffmpeg\\bin\\ffmpeg" if platform.system().lower() == "windows" else "/ffmpeg/bin/ffmpeg")  
            self.ffmpeg = utils.read_ini(key='ffmpeg', default=default)
        else:
            self.ffmpeg = ffmpeg

        if output_path is None:
            default = os.getcwd() + ("\\output\\" if platform.system().lower() == "windows" else "/output/") 
            self.output_path = utils.read_ini(key='output_path', default='mp3')
        else:
            self.output_path = output_path
        
        if child_path !='':
            self.set_childpath(child_path)

        if output_kbs is None:
            self.output_kbs = utils.read_ini(key='output_kbs', default='22k')
        else:
            self.output_kbs = output_format
        
        if output_format is None:
            self.output_format = utils.read_ini(key='output_format', default='mp3')
        else:
            self.output_format = output_format
        pass

    def set_childpath(self,child_path):
        self.output_path = utils.fill_path_end(self.output_path + child_path)

    @staticmethod
    def convert(ffmpeg,presets,src,dst,ignore=True):
        
        if os.path.exists(dst):
            if not ignore:
                os.rename(dst, dst+".bk")
            else:
                return 0
        n = os.system(ffmpeg+" -i "+src+" "+presets+" "+dst)
        print("%s is converted." % dst)
        return n

    def convertMp3(self,src,title):
        presets = "-ab {} -f {}".format(self.output_kbs,self.output_format)
        dst = self.output_path + title.replace(" ","") + "."+self.output_format
        utils.make_dir(self.output_path)
        return Mp3Convert.convert(self.ffmpeg,presets,src,dst)
    
    def convertTask(self,task):
        src = task.url
        presets = "-ab {} -f {}".format(self.output_kbs,self.output_format)
        dst = self.output_path + task.title.replace(" ","") + "."+self.output_format
        utils.make_dir(self.output_path)
        return Mp3Convert.convert(self.ffmpeg,presets,src,dst)
    
class Mp3ConvertTask(object):

    def __init__(self, taskName,maxTasks=3):
        self.tasks = Queue()
        self.maxTasks = maxTasks
        self.taskName = taskName
        self.workers = [] 

        self.process = None
        self.runSignal = multiprocessing.Event()
        self.runSignal.set()

        self.threadPool = None
        pass

    def putTask(self, taskInfo):
        self.tasks.put(taskInfo)
        pass
    
    def putTasks(self,tasks):
        for task in tasks:
            self.putTask(task)
    
    def run(self, convert, join=True):

        for i in range(self.maxTasks):
            p = Process(target=self.work,args=(convert.convertTask,i))
            self.workers.append(p)
            p.start()
            
        print("All works(%s) start!" % self.taskName)
        

    def runAsync(self, convert):
    
        self.threadPool = ThreadPool(self.maxTasks)
        #self.threadPool.map(self.work,(convert.convertTask,1,))
        for i in range(self.maxTasks):
            self.threadPool.apply_async(self.work, (convert.convertTask, i,))
        
        print("works(%s) run, qty is %d." % (self.taskName,self.maxTasks))
    
    def terminate(self):

        self.runSignal.clear()
        print("Task(%s) is quiting!" % self.taskName)
        #self.process.join()
        self.threadPool.close()
        self.threadPool.join()
        print("Task(%s) quit!" % self.taskName)
        
        self.workers = []
        self.threadPool = None
    
    def work(self ,callback ,i):
        while self.runSignal.is_set():
            if not self.tasks.empty():
                task = self.tasks.get()
                callback(task)
            else:
                gevent.sleep(1)

        print("work(%s):%d get the quit signal and quit!" % (self.taskName,i))


if __name__ == '__main__':

    c = Mp3Convert()
    t = Mp3ConvertTask('audio convert',maxTasks=3)
    t.putTask(TaskInfo(r'E:\fm\百家讲坛蒙曼讲大隋风云【全集】大隋风云上部（1）流星王朝.m4a','百家讲坛蒙曼讲大隋风云【全集】大隋风云上部（1）流星王朝'))
    t.putTask(TaskInfo(r'E:\fm\百家讲坛蒙曼讲大隋风云【全集】大隋风云上部（2）杨坚出世.m4a','百家讲坛蒙曼讲大隋风云【全集】大隋风云上部（2）杨坚出世'))
    t.putTask(TaskInfo(r'E:\fm\百家讲坛蒙曼讲大隋风云【全集】大隋风云上部（3）坎坷仕途.m4a','百家讲坛蒙曼讲大隋风云【全集】大隋风云上部（3）坎坷仕途'))
    t.putTask(TaskInfo(r'E:\fm\百家讲坛蒙曼讲大隋风云【全集】大隋风云上部（4）权威震主.m4a','百家讲坛蒙曼讲大隋风云【全集】大隋风云上部（4）权威震主'))
    
    t.run(c)
    #t.runAsync(c.convertMp3Task)
    input(u'输入任意键退出：')
    #t.terminate()