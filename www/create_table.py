#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Seiei'

'''
新创建表
'''

import mysql.connector

conn = mysql.connector.connect(user='root', password='password', database='awesome')
cursor = conn.cursor()
cursor.execute('drop table users')
cursor.execute('create table users (id varchar(50) primary key,email varchar(50),passwd varchar(50),name varchar(50),image varchar(500),admin boolean,create_at real)')
cursor.execute('create table blogs (id varchar(50) primary key,user_id varchar(50),user_name varchar(50),user_image varchar(500),name varchar(50),summary varchar(200),content text,create_at real)')
cursor.execute('create table comments (id varchar(50) primary key,blog_id varchar(50),user_id varchar(50),user_name varchar(50),user_image varchar(500),content text,create_at real)')
cursor.close()
conn.commit()
conn.close()