#!usr/bin/env python3
# -*- coding: utf-8 -*-

__author__="Seiei"

'''
编写orm模块
'''

import asyncio
import logging
import aiomysql

def log(sql):
    logging.info("SQL: %s"%(sql))

#创建一个全局的连接池，每个HTTP请求都从池中获得数据库连接
#连接池由全局变量__pool存储，缺省情况下将编码设置为utf8，自动提交事务
async def create_pool(loop,**kw):#charset参数是utf8
    logging.info('create database connectiong pool...')
    global __pool #全局变量
    __pool = await aiomysql.create_pool(
        host = kw.get('host','localhost'),
        port = kw.get('port',3306),
        user = kw['user'],
        db = kw['db'],
        password = kw['password'],
        charset = kw.get('charset','utf8'),
        autocommit = kw.get('autocommit',True),
        maxsize = kw.get('maxsize',10),
        minsize = kw.get('minsize',1),
        loop=loop
    )#创建连接所需要的参数

#用于输出元类中创建sql_insert语句中的占位符
def create_args_string(num):
    L=[]
    for x in range(num):
        L.append('?')
    return ','.join(L)

#单独封装select，其他insert,update,delete一并封装，理由如下：
#使用Cursor对象执行insert，update，delete语句时，执行结果由rowcount返回影响的行数，就可以拿到执行结果。
#使用Cursor对象执行select语句时，通过featchall()可以拿到结果集。结果集是一个list，每个元素都是一个tuple，对应一行记录。
async def select(sql,args,size=None):
    log(sql)
    global __pool #引入全局变量
    with await __pool.get() as conn: #打开pool的方法
        cur = await conn.cursor(aiomysql.DictCursor) #创建游标,aiomysql.DictCursor的作用使生成结果是一个dict
        await cur.execute(sql.replace('?',"%s"),args or ()) #执行sql语句，sql语句的占位符是'?',而Mysql的占位符是'%s'
        if size:
            rs = await cur.fetchmany(size)
        else:
            rs = await cur.fetchall()
    await cur.close()
    logging.info('rows returned: %s'%len(rs))
    return rs

#封装INSTERT,UPDATE,DELETE,我一开始的做法
#async def execute(sql,args):
#    log(sql)
#    global __pool
#    with await __pool as conn:
#        try:
#            cur = await conn.cursor()
#            await cur.execute(sql.replace('?','%s'),args)
#            affectline = cur.rowcount
#            await cur.close()
#        except BaseException as e:
#            raise
#        return affectline

#封装INSTERT,UPDATE,DELETE，老师的做法
async def execute(sql, args, autocommit=True):
    log(sql)
    async with __pool.get() as conn:#为什么这里不使用get(),后面就调用不了save
        if not autocommit:
            await conn.begin()
        try:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(sql.replace('?', '%s'), args)
                affected = cur.rowcount
            if not autocommit:
                await conn.commit()
        except BaseException as e:
            if not autocommit:
                await conn.rollback()
            raise
        return affected


#定义Field
class Field(object):
    def __init__(self,name,colum_type,primary_key,default):
        self.name = name
        self.colum_type = colum_type
        self.primary_key = primary_key
        self.default = default
    def __str__(self):
        return '<%s,%s:%s>'%(self.__class__.__name__,self.colum_type,self.name)

class StringField(Field):
    def __init__(self,name=None,ddl='varchar(100)',primary_key=False,default=None):
        super(StringField,self).__init__(name,ddl,primary_key,default)

class BooleanField(Field):
    def __init__(self,name=None,ddl='boolean',primary_key=False,default=None):
        super(BooleanField,self).__init__(name,ddl,primary_key,default)

class IntegerField(Field):
    def __init__(self,name=None,ddl='bigint',primary_key=False,default=0):
        super(IntegerField,self).__init__(name,ddl,primary_key,default)

class FloatField(Field):
    def __init__(self,name=None,ddl='real',primary_key=False,default=0.0):
        super(FloatField,self).__init__(name,ddl,primary_key,default)

class TextField(Field):
    def __init__(self,name=None,ddl='Text',primary_key=False,default=None):
        super(TextField,self).__init__(name,ddl,primary_key,default)

#元类
class ModelMetaclass(type):

    def __new__(cls,name,bases,attrs):#当前准备创建的类的对象；类的名字；类继承的父类集合；类的方法集合。
        if name == 'Model': #排除掉对Model类的修改；
            return type.__new__(cls,name,bases,attrs)
        tableName = attrs.get('__table__',None) or name
        logging.info('found a model: %s (table: %s)'%(name,tableName))
        # 获取所有的Field和主键名:
        mappings = dict() #保存映射关系
        fields = [] #保存除主键外的属性
        primarykey = None
        for k,v in attrs.items():
            if isinstance(v,Field):
                logging.info('Found mapping: %s ==> %s'%(k,v))
                mappings[k] = v
                if v.primary_key: #找到主键名
                    if primarykey:
                        raise StandardError('Duplicate primary key for field: k'%k)
                    primarykey = k #此列设为列表的主键
                else:
                    fields.append(k) #保存除主键外的属性
        if not primarykey:
            raise StandardError('primary key not found.')
        for k in mappings.keys():
            attrs.pop(k) #从类属性中删除Field属性,否则，容易造成运行时错误（实例的属性会遮盖类的同名属性）
        escaped_fields = list(map(lambda f: "`%s`"%f,fields))#转换为sql语法
        #创建供Model类使用属性
        attrs['__mappings__'] = mappings # 保存属性和列的映射关系
        attrs['__table__'] = tableName #表的名字
        attrs['__primary_key__'] = primarykey # 主键属性名
        attrs['__fields__'] = fields # 除主键外的属性名
        attrs['__select__'] = 'select `%s`,%s from %s'%(primarykey,','.join(escaped_fields),tableName)
        attrs['__insert__'] = 'insert into `%s` (%s, `%s`) values (%s)' % (tableName, ', '.join(escaped_fields), primarykey, create_args_string(len(escaped_fields) + 1))#占位符
        attrs['__update__'] = 'update `%s` set %s where `%s`=?'%(tableName,','.join(map(lambda f: '`%s`=?'%(mappings.get(f).name or f),fields)),primarykey)#查询列的名字，也看一下在Field定义上有没有定义名字，默认None
        attrs['__delete__'] = 'delete from `%s` where `%s`=?'%(tableName,primarykey)
        return type.__new__(cls,name,bases,attrs)

#基类Model
class Model(dict,metaclass=ModelMetaclass):
    
    def __init__(self,**kw):
        super(Model,self).__init__(**kw)

    def __getattr__(self,key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError('"Model" object has no atttibute: %s'%key)

    def __setattr__(self,key,value):
        self[key] = value

    def getValue(self,key):
        return getattr(self,key,None) #直接调回内置函数，注意这里没有下划符,注意这里None的用处,是为了当user没有赋值数据时，返回None，调用于update

    def getValueOrDefault(self,key):
        value = getattr(self,key,None) #第三个参数None，可以在没有返回数值时，返回None，调用于save
        if not value:
            field = self.__mappings__[key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                logging.debug('using default value for %s: %s'%(key, str(value)))
        return value

    @classmethod
    async def findall(cls,where=None,args=None,**kw):
        sql = [cls.__select__]
        if where:
            sql.append('where')
            sql.append(where)
        if args is None:
            args = []
        orderBy = kw.get('orderBy',None)
        if orderBy:
            sql.append('order by')
            sql.append(orderBy)
        limit = kw.get('limit',None)
        if limit:
            sql.append('limit')
            if isinstance(limit,int):
                sql.append('?')
                args.append(limit)
            elif isinstance(limit,tuple) and len(limit) == 2:
                sql.append('?, ?')
                args.extend(limit) #tuple融入list
            else:
                raise ValueError('Invalid limit value: %s'%str(limit))
        rs = await select(' '.join(sql),args)
        return [cls(**r) for r in rs] #调试的时候尝试了一下return rs，输出结果一样

    @classmethod
    async def findnumber(cls,selectField,where=None,args=None):
        sql = ['select %s __num__ from `%s`'%(selectField,cls.__table__)]
        if where:
            sql.append('where')
            sql.append(where)
        rs = await select(' '.join(sql),args,1)
        if len(rs) == 0:
            return None
        return rs[0]['__num__']

    @classmethod
    async def find(cls,primarykey):
        sql = '%s where `%s`=?'%(cls.__select__,primarykey)
        rs = await select(sql,[primarykey],1)
        if len(rs) == 0:
            return None
        return cls(**rs[0])

    async def save(self):
        args = list(map(self.getValueOrDefault, self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        rows = await execute(self.__insert__, args)
        if rows != 1:
            logging.warn('failed to insert record: affected rows: %s' % rows)

    async def update(self):
        args = list(map(self.getValue,self.__fields__))
        args.append(self.getValue(self.__primary_key__))
        rows = await execute(self.__update__,args)
        if rows != 1:
            logging.warn('faild to update by primary key: affected rows: %s'%rows)

    async def remove(self):
        args = [self.getValue(self.__primary_key__)]#这里不能使用list()-->'int' object is not iterable
        rows = await execute(self.__delete__,args)
        if rows != 1:
            logging.warn('faild to remove by primary key: affected rows: %s'%rows)
