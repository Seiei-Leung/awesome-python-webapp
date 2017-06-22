#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Seiei'

'''
编写web框架测试
'''

from aiohttp import web
import asyncio
from web_app.webframe import add_routes,add_static
from web_app.middleware_factories import init_jinja2,datetime_filter,logger_factory,response_factory,auth_factory
import logging; logging.basicConfig(level=logging.INFO)
from web_app import orm
from web_app.configs.config import config


async def init(loop):
    await orm.create_pool(loop, **config['db'])#创建数据库连接池，参数导入配置文件
    app = web.Application(loop=loop,middlewares=[logger_factory,response_factory,auth_factory])
    init_jinja2(app, filters = dict(datetime=datetime_filter), path = r"E:\learningpython\web_app\templates")#初始化Jinja2，这里值得注意是设置文件路径的path参数
    add_routes(app,'web_app.app')#导入URL处理函数
    add_static(app)
    srv = await loop.create_server(app.make_handler(),'127.0.0.1',9000)
    logging.info('Server started at http://127.0.0.1:9000...')
    return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()
