#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Seiei'

'''
编写最新配置文件
'''

from web_app.configs import config_default

#创建一个以覆盖配置文件为准，从而更新默认配置并返回的函数
def merge(defaults,override):#收集参数
    r = {}
    for name,value in defaults.items():
        if name in override: #覆盖文件有此参数
            if isinstance(value,dict): #判断是否其value为dict
                r[name] = merge(value,override[name]) #是的话，则创建新的字典后，调用原函数（递归）
            else:
                r[name] = override[name] #否则把覆盖配置文件的值导入
        else:
            r[name] = defaults[name] #如果覆盖文件没有，就继续使用默认值
    return r

config = config_default.configs

try:
    from web_app.configs import config_override
    config = merge(config,config_override.configs)
except ImportError:
    pass





