#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Seiei'

'''
串联ORM框架以及Web框架编写MVC，用于测试运行
'''

from web_app.webframe import get,post
import asyncio
from web_app.models import User #引入orm框架的User模型

@get('/')
async def index(request):
    users = await User.findall()
    return {
    '__template__':'text.html',
    'users':users
    } #不懂就查看Web框架的middleware里的Response_factory源码以及Jinja2初始化的源码，__template__是用来辨认出返回数据是Jinja2模板，而不是Json，同时可以从初始化Jinja2那里获取Environment，从而导进名叫text.html的模板；而dict中的users是传递给模板的数据
