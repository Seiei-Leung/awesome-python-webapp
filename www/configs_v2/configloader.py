#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Seiei'

'''
创建配置文件
'''
import os

path = (os.path.join(os.path.dirname(os.path.abspath(__file__)),'default.cfg'))
print(path)

with open(path, "r") as fp:
    s = ''
    for line in fp.readlines():
        if line.strip().startwith('//'):
            continue
        s = s + line.strip()
    configs = json.loads(s)




