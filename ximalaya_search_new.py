
#!/usr/bin/python
# -*- coding:utf-8 -*-
# author:joel 19-9-22

import hashlib
import json
import os
import re
import time
import random
import requests
from download_task import DownloadTask,DownloadInfo

"""
注意运行前请修改 make_dir() 中的下载路径！不要过度爬取，仅供测试学习！
"""


class XiMa(object):

    def __init__(self):
        self.base_url = 'https://www.ximalaya.com'
        self.base_api = 'https://www.ximalaya.com/revision/play/album?albumId={}&pageNum={}&sort=0&pageSize=30'
        self.time_api = 'https://www.ximalaya.com/revision/time'
        self.header = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0'
        }
        self.s = requests.session()

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
        #print(sign)
        return sign

    def index_choose(self):
        c_num = input(u'请输入对应操作的选项：\n'
                      u'1、下载整部有声书\n'
                      u'2、下载单个音源\n'
                      u'3、返回\n')
        if c_num == '1':
            xm_id = input(u'请输入要获取喜马拉雅节目的ID：')
            xima.get_fm(xm_id)
            self.index_choose()
        elif c_num == '2':
            xm_id = input(u'请输入要获取的音源：')
            print(xm_id)
            self.index_choose()
        elif c_num == '3':
            print('结束')
        else:
            pass

    @staticmethod
    def make_dir(xm_fm_id):
        # 保存路径，请自行修改，这里是以有声书ID作为文件夹的路径
        fm_path = 'e:\\{}\\'.format(xm_fm_id)
        f = os.path.exists(fm_path)
        if not f:
            os.makedirs(fm_path)
            print('make file success...')
        else:
            print('file already exists...')
        return fm_path

    def get_fm(self, xm_fm_id):
        # 根据有声书ID构造url
        fm_url = self.base_url + '/lishi/{}'.format(xm_fm_id)
        print(fm_url)
        r_fm_url = self.s.get(fm_url, headers=self.header)

        fm_title = ""
        if re.findall('<h1 class="title _II0L">(.*?)</h1>', r_fm_url.text, re.S) != None and \
            len(re.findall('<h1 class="title _II0L">(.*?)</h1>', r_fm_url.text, re.S))>0:
            fm_title = re.findall('<h1 class="title _II0L">(.*?)</h1>', r_fm_url.text, re.S)[0]
        elif re.findall('<h1 class="title lO_">(.*?)</h1>', r_fm_url.text, re.S) != None and \
            len(re.findall('<h1 class="title lO_">(.*?)</h1>', r_fm_url.text, re.S))>0:
            fm_title = re.findall('<h1 class="title lO_">(.*?)</h1>', r_fm_url.text, re.S)[0]

        print('书名：' + fm_title)
        # 新建有声书ID的文件夹
        fm_path = self.make_dir(xm_fm_id)
        # 取最大页数
        max_page = re.findall(r'<input type="number" placeholder="请输入页码" step="1" min="1" '
                              r'max="(\d+)" class="control-input _bfuk" value=""/>', r_fm_url.text, re.S)

        maxPage = 1 if max_page ==None or len(max_page)==0 else int(max_page[0])
        downloadTask = DownloadTask(fm_path,self.header)
        #if max_page and max_page[0]:
        if True:
            #for page in range(1, int(max_page[0]) + 1):
            for page in range(1, maxPage + 1):
                print('第' + str(page) + '页')
                self.get_sign()
                r = self.s.get(self.base_api.format(xm_fm_id, page), headers=self.header)
                # print(json.loads(r.text))
                r_json = json.loads(r.text)
                for audio in r_json['data']['tracksAudioPlay']:
                    audio_title = str(audio['trackName']).replace(' ', '')
                    audio_src = audio['src']
                    downloadTask.putTask(DownloadInfo(audio_src,audio_title))
                    #self.get_detail(audio_title, audio_src, fm_path)
                # 每爬取1页，30个音频，休眠3秒
                time.sleep(3)
            
            downloadTask.run()
        else:
            print(os.error)

    def get_detail(self, title, src, path):
        r_audio_src = self.s.get(src, headers=self.header)
        m4a_path = path + title + '.m4a'
        if not os.path.exists(m4a_path):
            with open(m4a_path, 'wb') as f:
                f.write(r_audio_src.content)
                print(title + '保存完毕...')
        else:
            print(title + 'm4a已存在')


if __name__ == '__main__':
    xima = XiMa()
    xima.index_choose()
