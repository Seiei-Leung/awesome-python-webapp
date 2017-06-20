#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__='Seiei'

'''
编写Web App handler
'''

from web_app.webframe import get,post
import asyncio
from web_app.models import User,Blog,next_id
import time
from web_app.APIError import APIValueError,APIError
import re, hashlib
from web_app.configs.config import config
from aiohttp import web
import json
import logging


#首页
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

#显示注册页面
@get('/register')
def register():
    return {
        '__template__': 'register.html'
    }

#显示登录页面
@get('/signin')
def signin():
    return {
        '__template__': 'signin.html'
    }

COOKIE_NAME = 'awesession'#用来在set_cookie中命名
_COOKIE_KEY = config['session']['secret']#导入默认设置

#制作set_cookie的value
def user2cookie(user, max_age):
    # build cookie string by: id-expires-sha1（id-到期时间-摘要算法）
    expires = str(time.time()+max_age)
    s = '%s-%s-%s-%s'%(user.id, user.passwd, expires, _COOKIE_KEY)#s的组成：id, passwd, expires, _COOKIE_KEY
    L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]#再把s进行摘要算法
    return '-'.join(L)

#正则表达式我是参考这里的(http://www.cnblogs.com/vs-bug/archive/2010/03/26/1696752.html)
_RE_EMAIL = re.compile(r'^(\w)+(\.\w)*\@(\w)+((\.\w{2,3}){1,3})$')
_RE_PASSWD = re.compile(r'^[\w\.]{40}')#对老师这里的密码正则表达式也做了点修改

#用户注册api
@post('/api/users')#注意这里路径是'/api/users'，而不是`/register`
async def api_register_usesr(*,name,email,passwd):
    if not name or not name.strip():#如果名字是空格或没有返错，这里感觉not name可以省去，因为在web框架中的RequsetHandler已经验证过一遍了
        raise APIValueError('name')
    if not email or not _RE_EMAIL.match(email):
        raise APIValueError('email')
    if not passwd and not _RE_SHA1.match(passwd):
        raise APIValueError('password')
    users = await User.findall(where='email=?', args=[email])#查询邮箱是否已注册，查看ORM框架源码
    if len(users) > 0:
        raise APIError('register:failed','email','Email is already in use.')
    #接下来就是注册到数据库上,具体看会ORM框架中的models源码
    #这里用来注册数据库表id不是使用Use类中的默认id生成，而是调到外部来，原因是后面的密码存储摘要算法时，会把id使用上。
    uid = next_id()
    sha1_passwd = '%s:%s' % (uid, passwd)
    user = User(id=uid, name=name.strip(), email=email, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(), image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest())#
    await user.save()
    #制作cookie返回浏览器客户端
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user,86400), max_age=86400, httponly=True)
    user.passwd = '******'#掩盖passwd返回浏览器
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')#https://docs.python.org/2/library/json.html#basic-usage
    return r

#验证登录信息
@post('/api/authenticate')
async def authenticate(*,email,passwd):
    if not email:
        raise APIValueError('email')
    if not passwd:
        raise APIValueError('passwd')
    users = await User.findall(where='email=?',args=[email])
    if len(users) == 0:
        raise APIValueError('email','Email not exist.')
    user = users[0]#此时finall得出来的数值是一个仅含一个dict的list,就是sql语句返回什么类型的数据自己忘了
    #把登录密码转化格式并进行摘要算法
    sha1 = hashlib.sha1()
    sha1.update(user.id.encode('utf-8'))
    sha1.update(b':')
    sha1.update(passwd.encode('utf-8'))
    if sha1.hexdigest() != user.passwd:#与数据库密码比较
        raise APIValueError('password','Invaild password')
    #制作cookie发送给浏览器，这步骤与注册用户一样
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user,86400), max_age=86400, httponly=True)
    user.passwd = "******"
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii = False).encode('utf-8')
    return r

#解释cookie
async def cookie2user(cookie_str):
    if not cookie_str:
        return None
    try:
        L = cookie_str.split('-') #拆分字符串(D)
        if len(L) !=3:
            return None
        uid, expires, sha1 = L
        if float(expires) < time.time():#查看是否过期,这里廖大用的是int，但是字符串用int的时候，只能全是数字，不能含小数点
            return None
        user = await User.find(uid)
        if not user:
            return None
        #用数据库来生字符串(C)与cookie的比较
        s = '%s-%s-%s-%s'%(uid, user.passwd, expires, _COOKIE_KEY)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest:
            logging.info('invalid sha1')
            return None
        user.passwd = "******"
        return user
    except Exception as e:
        logging.exception(e)
        return None








