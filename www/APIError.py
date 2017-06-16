#!usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Seiei'

'''
定义接口错误，以便输出错误信息
'''

class APIError(Exception):
    '''
    基础的APIError，包含错误类型(必要)，数据(可选)，信息(可选)
    '''
    def __init__(self,error,data = '',message = ''):
        super(APIError,self).__init__(message)
        self.error = error
        self.data = data
        self.message = message

class APIValueError(APIError):
    '''
    Indicate the input value has error or invalid. The data specifies the error field of input form.
    表明输入数据有问题，data说明输入的错误字段
    '''
    def __init__(self,field,message = ''):
        super(APIValueError,self).__init__('Value: invalid',field,message)

class APIResourceNotfoundError(APIError):
    '''
    Indicate the resource was not found. The data specifies the resource name.
    表明找不到资源，data说明资源名字
    '''
    def __init__(self,field,message = ''):
        super(APIResourceNotFoundError,self).__init__('Value: Notfound',field,message)

class APIPermissionError(APIError):
    '''
    Indicate the api has no permission.
    接口没有权限
    '''
    def __init__(self,message = ''):
        super(APIPermissionError,self).__init__('Permission: forbidden','Permission',message)