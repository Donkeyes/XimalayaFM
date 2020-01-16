# -*- coding:utf-8 -*-
from __future__ import unicode_literals
__author__ = 'Vhsal.com'

from gevent import monkey;monkey.patch_all( thread=False)
import utils
import requests
import sys,os,time,platform
import hashlib
import random
import re
import json

from configparser import ConfigParser
from lxml import etree 
from abc import ABC, abstractmethod
from task_info import TaskInfo
from download_task import DownloadTask


class RadioDownload(ABC):

    def __init__(self, ext="m4a", header=None):
        if header is None:
            self.header = {
                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0'
            }
        self.s = requests.session()
        default_path = os.getcwd() + ("\\" if platform.system().lower() == "windows" else "/")
        self.save_path = utils.read_ini(key='download_path', default=default_path)
        self.ext = ext
        
    @abstractmethod
    def get_radio(self,id):
        pass


class XimalayaRadioDownload(RadioDownload):

    def __init__(self):
        self.fm_url = "https://www.ximalaya.com/lishi/{}/"

        self.api_url = 'https://www.ximalaya.com/revision/play/album?albumId={}&pageNum={}&sort=0&pageSize=30'
        self.time_api = 'https://www.ximalaya.com/revision/time'
        super().__init__()
    
    def get_time(self):
        """
        获取服务器时间戳
        :return:
        """
        r = self.s.get(self.time_api, headers=self.header)
        return r.text

    def get_sign(self):
        """
        获取sign： md5(ximalaya-服务器时间戳)(100以内随机数)服务器时间戳(100以内随机数)现在时间戳
        :return: xm_sign
        """
        nowtime = str(round(time.time() * 1000))
        servertime = self.get_time()
        sign = str(hashlib.md5("himalaya-{}".format(servertime).encode()).hexdigest()) + "({})".format(
            str(round(random.random() * 100))) + servertime + "({})".format(str(round(random.random() * 100))) + nowtime
        self.header["xm-sign"] = sign
        return sign

    def get_radio(self, id):
        url = self.fm_url.format(id)
        try:
            r = self.s.get(url, headers=self.header)
            if r.status_code == 200:
                fm_title, max_pages = self.__parse_page__(id,r.text)
                if fm_title is None:
                    print('无此专辑:%d,退出！' % id)
                    return 
                print('专辑名称：' + fm_title)
                fm_path = utils.make_dir(self.save_path, fm_title)
                downloadTask = DownloadTask(fm_path,self.header)

                for page in range(1, max_pages + 1):
                    tasks = self.get_radio_tasks(id,page)
                    if tasks != None and len(tasks)>0:
                        downloadTask.putTasks(tasks)
                downloadTask.run(fm_title)
            else:
                print("browse url error(%d):%s" %(r.status_code,url))
        except requests.exceptions.ConnectionError :
            print("requests.RequestException:requests.exceptions.ConnectionError" )
            return
        print("下载完成！")
        pass

    def get_radio_tasks(self,id,index):
        tasks = []
        url = self.api_url.format(id,index)
        try:
            self.get_sign()
            r = self.s.get(url, headers=self.header)
            
            if r.status_code == 200:
                r_json = json.loads(r.text)
                for audio in r_json['data']['tracksAudioPlay']:
                    audio_title = str(audio['trackName']).replace(' ', '')
                    audio_src = audio['src']
                    print(audio_title)
                    tasks.append(TaskInfo(audio_src,audio_title))
                 
            else:
                print("browse url error(%d):%s" %(r.status_code,url))
        except requests.exceptions.ConnectionError :
            print("requests.RequestException:requests.exceptions.ConnectionError" )
        return tasks

    def __parse_page__(self, id,html):
        
        fm_title = str(id)
        if re.findall('<h1 class="title _II0L">(.*?)</h1>', html, re.S) != None and \
            len(re.findall('<h1 class="title _II0L">(.*?)</h1>', html, re.S))>0:
            fm_title = re.findall('<h1 class="title _II0L">(.*?)</h1>',html, re.S)[0]
        elif re.findall('<h1 class="title lO_">(.*?)</h1>', html, re.S) != None and \
            len(re.findall('<h1 class="title lO_">(.*?)</h1>', html, re.S))>0:
            fm_title = re.findall('<h1 class="title lO_">(.*?)</h1>', html, re.S)[0]
        else:
            print("无此专辑！")
            return None, None
        
        # 取最大页数
        max_pages = re.findall(r'<input type="number" placeholder="请输入页码" step="1" min="1" '
                              r'max="(\d+)" class="control-input _bfuk" value=""/>', html, re.S)

        max_pages = 1 if max_pages ==None or len(max_pages)==0 else int(max_pages[0])
        return fm_title, max_pages 

class QingtingRadioDownload(RadioDownload):

    def __init__(self):
        self.fm_url = "https://www.qingting.fm/channels/{}/"
        self.aduio_url = r'https://od.qingting.fm/'
        self.api_url='https://i.qingting.fm/wapi/channels/{}/programs/page/{}/pagesize/30'
        super().__init__()

    def get_radio(self, id):
        url = self.fm_url.format(id)
        try:
            r = self.s.get(url, headers=self.header)
            if r.status_code == 200:
                fm_title, max_pages = self.__parse_page__(id,r.text)
                if fm_title is None:
                    print('无此专辑:%d,退出！' % id)
                    return 
                print('专辑名称：' + fm_title)
                fm_path = utils.make_dir(self.save_path, fm_title)
                downloadTask = DownloadTask(fm_path,self.header)

                for page in range(1, max_pages + 1):
                    tasks = self.get_radio_tasks(id,page)
                    if tasks != None and len(tasks)>0:
                        downloadTask.putTasks(tasks)
                downloadTask.run(fm_title)
            else:
                print("browse url error(%d):%s" %(r.status_code,url))
        except requests.exceptions.ConnectionError :
            print("requests.RequestException:requests.exceptions.ConnectionError" )
            return
        print("下载完成！")
        pass

    def __parse_page__(self, id,html):
        tree = etree.HTML(html)
        nodes = tree.xpath('//h1[@class="title"]')
        title = str(id)
        if len(nodes) > 0:
            title = nodes[0].text
        else:
            None, None
        nodes = tree.xpath("//ul[@class='pagination']")
        if len(nodes)>0:
            nodes = nodes[0].xpath('//li/a/text()')
            if len(nodes) >0:
                max_pages= int(nodes[-2])
        else:
            max_pages = 1
        return title, max_pages
    
    def get_radio_tasks(self,id,index):
        tasks = []
        url = self.api_url.format(id,index)
        try:
            r = self.s.get(url)
            if r.status_code == 200:
                r_json = json.loads(r.text)
                n = 0
                for audio in r_json['data']:
                    audio_title = str(audio['name']).replace(' ', '')
                    audio_src = self.aduio_url + audio['file_path']
                    print(audio_title)
                    tasks.append(TaskInfo(audio_src,audio_title))
                    n += 1
                    if n>5:
                        break
            else:
                print("browse url error(%d):%s" %(r.status_code,url))
        except requests.exceptions.ConnectionError :
            print("requests.RequestException:requests.exceptions.ConnectionError" )
        return tasks

def index_radio():
    radioId = input(u'请输入对应操作的选项：\n'
                u'1、喜马拉雅音频\n'
                u'2、蜻蜓FM音频\n'
                u'其他退出\n'
                )
    if radioId in ('1','2'):
        input_fm_id(int(radioId))
        return True
    else:
        return False

def input_fm_id(radioId):
    fmId = input(u'请输入要获取的音源Id：')
    print("输入的专辑Id:%s" % fmId)  

    radioDownload = XimalayaRadioDownload() if radioId == 1 else QingtingRadioDownload()
    radioDownload.get_radio(fmId)  
    pass

if __name__ == '__main__':

    while index_radio():
        pass

