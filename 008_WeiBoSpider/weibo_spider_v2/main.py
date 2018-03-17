# coding: utf-8

from mli_weibo.scheduler import WeiboSpiderScheduler
import settings

from datetime import datetime


keyword = '巧克力'
date_end = datetime(2017, 1, 1)


def main():
    sch = WeiboSpiderScheduler()
    sch.from_settings(settings)
    keyword_li = ['泡芙','芝士']

    for keyword in keyword_li:
        sch.feed_keyword(keyword, date_end)
    sch.run()

if __name__ == '__main__':
    main()  


    