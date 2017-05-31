#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__='Seiei'

'''
编写Web App骨架
'''

import logging; logging.basicConfig(level=logging.INFO)
import asyncio
from aiohttp import web

async def index(request):
    return web.Response(body=b'<h1>Awesome</h1>',content_type='text/html')

async def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route(method='GET',path='/',handler=index)
    srv = await loop.create_server(app.make_handler(),'127.0.0.1',9000)
    logging.info('server start at http://127.0.0.1:9000')
    return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()