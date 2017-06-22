#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
创建监视修改重启程序
'''

__author__ = 'Seiei'

import os, time, sys, subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


def log(s):
    print('[Monitor] %s' % s)


command = ['echo', 'ok'] #重启操作文件的信息
process = None

#退出程序
def kill_process():
    global process
    if process:
        log('Kill process [%s]...' % process.pid)
        process.kill()
        process.wait()
        log('Process ended with code %s.' % process.returncode)
        process = None

#开始程序
def start_process():
    global process, command
    log('Start process %s...' % ' '.join(command))
    process = subprocess.Popen(command, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)

#重启程序
def restart_process():
    kill_process()
    start_process()

#编辑MyFileSystemEventHander
class MyFileSystemEventHander(FileSystemEventHandler):

    def __init__(self, fn):
        super(MyFileSystemEventHander, self).__init__()
        self.restart = fn #导入重启函数restart_process，没括号

    def on_any_event(self, event):
        if event.src_path.endswith('.py'): #监视`.py`后缀文件发生改变
            log('Python source file changed: %s' % event.src_path)
            self.restart()


#监视
def start_watch(path, callback):
    observer = Observer()
    
    observer.schedule(MyFileSystemEventHander(restart_process), path, recursive=True)
    observer.start()
    log('Watching directory %s...' % path)
    start_process()
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()



if __name__ == '__main__':
    argv = sys.argv[1:] #用于在命令行取程序外部输入参数
    if not argv:
        print('Usage: ./pymonitor your-script.py')
        exit(0)
    if argv[0] != 'python':
        argv.insert(0, 'python')
    command = argv
    path = os.path.abspath('.')#监视路径
    start_watch(path, None)