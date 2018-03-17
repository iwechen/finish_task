# coding: utf-8

from __future__ import absolute_import

import time
import threading
import logging
import re
from six.moves import queue 

from .spider import WeiboSpider
from .storage import WeiboStorage

logger = logging.getLogger(__name__)

class WeiboSpiderScheduler(object):
    def __init__(self):


        self.keyword_date = {}

        self._task_queue = queue.Queue()
        self._result_queue = queue.Queue(1000)
        self._topic_queue = queue.Queue(1000)
        self._topic_keyword_queue = queue.Queue(1000)

        self._topic_result_queue = queue.Queue(1000)
        self._spider = WeiboSpider(self._topic_result_queue)
        self._storage = WeiboStorage()
        self._unique_topic_set = set()
        self.__stopped = {}
    
    @classmethod
    def from_settings(cls, settings):
        cls._db_host = settings.MONGODB_HOST
        cls._db_port = settings.MONGODB_PORT
        return cls
    
    def _storage_worker(self):
        while True:
            data = self._result_queue.get()

            if not isinstance(data, dict):
                logger.error("Result queue get error data: %s", data)
                continue
            self._storage.save(data)
            keyword = data['keyword']
            if data['topic'] == 1:
                continue
            if self._storage.min_date[keyword] < self.keyword_date[keyword]:
                logger.debug("Stop keyword=%s", keyword)
                self.stop_keyword(keyword)
    
    def feed_keyword(self, keyword, date_end):
        """
        设置关键词和时间范围
        """
        self._task_queue.put((keyword, date_end))

    def _filter_topic(self):
        '''
        筛选微博内容话题
        '''
        while True:
            body = self._topic_queue.get()
            for card in body['response']['data']['cards']:
                for item in card['card_group']:
                    if item['card_type'] == 9 or item.get('card_type_name') == '微博':
                        text_data = item['mblog']['text']
                        topic_keyword_li = re.findall(r"<a class='k' href='.*?from=feed'>#(.*?)#</a>",text_data,re.S)
                        for topic_keyword in topic_keyword_li:
                            if topic_keyword in self._unique_topic_set:
                                continue
                            self._unique_topic_set.add(topic_keyword)
                            self._topic_keyword_queue.put(topic_keyword)
   
            self._result_queue.put(body)

    def _topic_loop(self):
        '''
        循环获取话题内容
        '''
        while True:
            topic_keyword = self._topic_keyword_queue.get()
            self._spider.query_topic(topic_keyword)
            continue

    def _topic_result_save(self):
        while True:
            data = self._topic_result_queue.get()
            # print(data)
            self._result_queue.put(data)
            continue

    def init(self):
        logger.info("Initializinng scheduler...")
        self._storage.init_conn(self._db_host, self._db_port)

        t = threading.Thread(target=self._storage_worker)
        t.setDaemon(True)
        t.start()
        
        t1 = threading.Thread(target=self._filter_topic)
        t1.setDaemon(True)
        t1.start()
    
        t2 = threading.Thread(target=self._topic_loop)
        t2.setDaemon(True)
        t2.start()

        t3 = threading.Thread(target=self._topic_result_save)
        t3.setDaemon(True)
        t3.start()

    def stop_keyword(self, keyword):
        self.__stopped[keyword] = True
    
    def _main_loop(self):
        self.init()
        while True:
            try:
                keyword, date_end = self._task_queue.get(timeout=3)
                self.keyword_date[keyword] = date_end
            except Exception as e:
                if len(self.__stopped) > 0 and all(self.__stopped.values()):
                    logger.info("All task finished.")
                    break
                else:
                    continue

            if keyword in self.__stopped and self.__stopped[keyword] == True:
                continue
            else:
                self.__stopped[keyword] = False
            
            page = 1
            while True:
                if self.__stopped[keyword]:
                    logger.debug("Loop keyword=%s stopped.", keyword)
                    break
                data = self._spider.query_keyword(keyword, page)
                # if data['topic']==1:
                #     self._result_queue.put(data)
                # else:
                if data['response']['ok'] == 0:
                    self.stop_keyword(keyword)
                    logger.warning(data)
                    continue
                self._topic_queue.put(data)

                page += 1
    
    def run(self):
        self._main_loop()

 