# -*- coding:utf-8 -*-
from __future__ import unicode_literals
__author__ = 'Vhsal.com'
import requests
import sys,os,time,platform
from configparser import ConfigParser


def make_dir(base_path, title=''):
    if title !='':
        fm_path = fill_path_end(base_path + title.replace(' ','')) 
    else:
        fm_path = base_path

    f = os.path.exists(fm_path)
    if not f:
        os.makedirs(fm_path)
    print("create dir：" + fm_path)
    return fm_path

def read_ini(key, field="sys",default=""):
    print (os.getcwd())
    try:
        cf = ConfigParser()
        cf.read(os.getcwd() + "\\sys.ini")
        return cf.get(field, key)
    except:
        print (sys.exc_info())
        return default

def fill_path_end(path):
    return path + ("\\" if platform.system().lower() == "windows" else "/")
