#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Seiei'

'''
编写web框架测试
'''

from aiohttp import web
import asyncio
from web_app.webframe import add_routes,add_static
from web_app.middleware_factories import init_jinja2,datetime_filter,logger_factory,response_factory
import logging; logging.basicConfig(level=logging.INFO)


async def init(loop):
    app = web.Application(loop=loop,middlewares=[logger_factory,response_factory])
    init_jinja2(app,filters=dict(datetime=datetime_filter))
    add_routes(app,'web_app.webframe_test_handler')
    add_static(app)
    srv = await loop.create_server(app.make_handler(),'127.0.0.1',9000)
    logging.info('Server started at http://127.0.0.1:9000...')
    return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()








