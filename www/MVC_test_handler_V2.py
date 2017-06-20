#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Seiei'

'''
串联ORM框架以及Web框架编写MVC，用于测试运行
'''

from web_app.webframe import get,post
import asyncio
from web_app.models import User,Blog
import time

@get('/')
def index(request):
    summary = 'Hello,World.'
    blogs = [
        Blog(id='1', name='Test Blog', summary=summary, created_at=time.time()-120),
        Blog(id='2', name='Something New', summary=summary, created_at=time.time()-3600),
        Blog(id='3', name='Learn Swift', summary=summary, created_at=time.time()-7200)
    ]
    return {
        '__template__': 'blogs.html',
        'blogs': blogs
    }

#编写api
@get('/api/users')
async def api_get_users():
    users = await User.findall(orderBy='create_at desc')
    for u in users:
        u.passwd = '******'
    return dict(users=users)