import multiprocessing
import os
import time
from datetime import datetime


def subprocess(number):
    # 子进程
    print('这是第%d个子进程' % number)
    pid = os.getpid()  # 得到当前进程号
    print('当前进程号：%s，开始时间：%s' % (pid, datetime.now().isoformat()))




def mainprocess():
    # 主进程
    print('这是主进程，进程编号：%d' % os.getpid())

    pool = multiprocessing.Pool()
    for i in range(8):
        pool.apply_async(subprocess, args=(i,))
    pool.close()
    pool.join()



if __name__ == '__main__':
    # 主测试函数
    mainprocess()