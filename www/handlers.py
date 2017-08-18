#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__='Seiei'

'''
编写Web App handler
'''

from web_app.webframe import get,post
import asyncio
from web_app.models import User,Blog,next_id,Comment
import time
from web_app.APIError import APIValueError,APIError,APIPermissionError,APIResourceNotfoundError
import re, hashlib
from web_app.configs.config import config
from aiohttp import web
import json
import logging
from web_app import markdown2


#---------------------------------- ----------------MVC---------------------------------------------------------

#首页
@get('/')
async def index(request):
    summary = 'Hello,World.'
    blogs = await Blog.findall(orderBy='create_at desc')
    return {
        '__template__': 'blogs.html',
        'blogs': blogs[0:4],
        '__user__': request.__user__
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

#显示创建日志页面
@get('/manage/blogs/create')
def manage_create_blog(request):
    return {
        '__template__': 'manage_blog_edit.html',
        'id': '',
        'action': '/api/blogs',
        '__user__': request.__user__
    }

#显示日志详情页面
@get('/blog/{id}')
async def get_blog(request,*,id):
    blog = await Blog.find(id)
    comments = await Comment.findall('blog_id=?', [id], orderBy='create_at desc')
    comments = comments[::-1]
    for c in comments:
        c.html_content = text2html(c.content)
    blog.html_content = markdown2.markdown(blog.content)
    return {
        '__template__': 'blog.html',
        'blog': blog,
        'comments': comments,
        '__user__': request.__user__
    }

#日志列表页面
@get('/manage/blogs')
def manage_blogs(request,*, page='1'):
    return {
        '__template__': 'manage_blogs.html',
        'page_index': get_page_index(page),
        '__user__': request.__user__
    }

#修改日志页面
@get('/manage/blogs/edit')
def manage_edit_blog(request,*, id):
    return {
        '__template__': 'manage_blog_edit.html',
        'id': id,
        'action': '/api/blogs/%s' % id,
        '__user__': request.__user__
    }

#评论列表页面
@get('/manage/comments')
def manage_comments(request,*, page='1'):
    return {
        '__template__': 'manage_comments.html',
        'page_index': get_page_index(page),
        '__user__': request.__user__
    }

#用户列表页面
@get('/manage/users')
def manage_users(request,*, page='1'):
    return {
        '__template__': 'manage_users.html',
        'page_index': get_page_index(page),
        '__user__': request.__user__
    }

#------------------------------------------------FUNCTION-------------------------------------------------------

COOKIE_NAME = 'awesession'#用来在set_cookie中命名
_COOKIE_KEY = config['session']['secret']#导入默认设置


#检测有否登录且是否为管理员
def check_admin(request):
    if request.__user__ is None or not request.__user__.admin:
        raise APIPermissionError()

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
        if user is None:
            return None
        #用数据库来生字符串(C)与cookie的比较
        s = '%s-%s-%s-%s'%(uid, user.passwd, expires, _COOKIE_KEY)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('invalid sha1')
            return None
        user.passwd = "******"
        return user
    except Exception as e:
        logging.exception(e)
        return None


#用于选择当前页面
def get_page_index(page_str):
    p = 1 #初始化页数取整
    try:
        p = int(page_str)
    except ValueError as e:
        pass
    if p < 1:
        p = 1
    return p

#定义选取数量，每一页都会选取相应选取数量的数据库中blog出来显示
class Page(object):

    def __init__(self, item_count, page_index=1, page_size=10):#参数依次是：数据库博客总数，初始页，一页显示博客数
        self.item_count = item_count
        self.page_size = page_size
        self.page_count = item_count // page_size + (1 if item_count % page_size > 0 else 0)#一共所需页的总数
        if (item_count == 0) or (page_index > self.page_count):#假如数据库没有博客或全部博客总页数不足一页
            self.offset = 0
            self.limit = 0
            self.page_index = 1
        else:
            self.page_index = page_index #初始页
            self.offset = self.page_size * (page_index - 1) #当前页数，应从数据库的那个序列博客开始显示
            self.limit = self.page_size #当前页数，应从数据库的那个序列博客结束像素
        self.has_next = self.page_index < self.page_count #有否下一页
        self.has_previous = self.page_index > 1 #有否上一页

    def __str__(self):
        return 'item_count: %s, page_count: %s, page_index: %s, page_size: %s, offset: %s, limit: %s' % (self.item_count, self.page_count, self.page_index, self.page_size, self.offset, self.limit)

    __repr__ = __str__

#显示日志评论页面html-->@get('/blog/{id}')显示页面
def text2html(text):
    lines = map(lambda s: '<p>%s</p>' % s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), filter(lambda s: s.strip() != '', text.split('\n')))
    return ''.join(lines)

#--------------------------------------------------API----------------------------------------------------------

#接口都是用来返回信息给页面或从页面上读取命令操作服务器

#后端API创建新用户
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

#后端API获取用户
@get('/api/users')
async def api_get_users(*, page='1'):
    page_index = get_page_index(page)
    num = await User.findnumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, users=())
    users = await User.findall(orderBy='create_at desc', limit=(p.offset, p.limit))
    for u in users:
        u.passwd = '******'
    return dict(page=p, users=users)

#后端API用户登录
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

#后端API用户登出
@get('/signout')
def signout(request):
    referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/') #重回首页
    r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True) #送回一个名字一样的cookie重置
    logging.info('user signed out.')
    return r

#后端API创建日志
@post('/api/blogs')
async def api_create_blogs(request, *, name, summary, content):
    check_admin(request)
    if not name or not name.strip():
        raise APIValueError('name','name can not empty.')
    if not summary or not summary.strip():
        raise APIValueError('summary','summary can not empty.')
    if not content or not content.strip():
        raise APIValueError('content','content can not empty.')
    blog = Blog(user_id=request.__user__.id, user_name=request.__user__.name, user_image=request.__user__.image, summary=summary.strip(), name=name.strip(), content=content.strip())
    await blog.save()
    return blog

#后端API获取日志列表,见manage_blogs.html
@get('/api/blogs')
async def api_blogs(*, page='1'):
    page_index = get_page_index(page)
    num = await Blog.findnumber('count(id)')#查询日志总数
    p = Page(num, page_index)
    if num == 0: #数据库没日志
        return dict(page=p, blogs=())
    blogs = await Blog.findall(orderBy='create_at desc', limit=(p.offset, p.limit))
    return dict(page=p, blogs=blogs)#返回管理页面信息，及显示日志数


#后端API获取日志详情，详情见manage_blog_edit.html
@get('/api/blogs/{id}')
async def api_get_blog(*, id):
    blog = await Blog.find(id)
    return blog

#后端API修改日志，详情见manage_blog_edit.html
@post('/api/blogs/{id}')
async def api_update_blog(id, request, *, name, summary, content):
    check_admin(request)
    blog = await Blog.find(id)
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty.')
    if not summary or not summary.strip():
        raise APIValueError('summary', 'summary cannot be empty.')
    if not content or not content.strip():
        raise APIValueError('content', 'content cannot be empty.')
    blog.name = name.strip()
    blog.summary = summary.strip()
    blog.content = content.strip()
    await blog.update()
    return blog

#后端API删除日志
@post('/api/blogs/{id}/delete')
async def api_delete_blog(request,*,id):
    check_admin(request)
    blog = await Blog.find(id)
    await blog.remove()
    return dict(id=id)

#后端API删除评论
@post('/api/comments/{id}/delete')
async def api_delete_comment(request,*,id):
    check_admin(request)
    comment = await Comment.find(id)
    await comment.remove()
    return dict(id=id)

#后端API获取评论列表，见manage_comments.html
@get('/api/comments')
async def api_comments(*, page='1'):
    page_index = get_page_index(page)
    num = await Comment.findnumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, comments=())
    comments = await Comment.findall(orderBy='create_at desc', limit=(p.offset, p.limit))
    return dict(page=p, comments=comments)

#后端API创建评论
@post('/api/blogs/{id}/comments')
async def api_create_comments(id, request, *, content):
    user = request.__user__ #登录再说
    if not user:
        raise APIPermissionError('Please signin first.')
    if not content or not content.strip():
        raise APIValueError('content', 'content cannot be empty.')
    blog = await Blog.find(id)
    if blog is None:
        raise APIResourceNotFoundError('Blog')
    comment = Comment(blog_id=blog.id, user_id=user.id, user_name=user.name, user_image=user.image, content=content.strip())
    await comment.save()
    return comment



