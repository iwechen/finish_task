# coding: utf-8

import requests
import time
import re
import threading
import random
from six.moves import queue 
import logging
logger = logging.getLogger(__name__)

# proxies = { "http":'http://120.77.35.48:8899'}
proxies = None

headers = {
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1',
    'Accept': 'application/json, text/plain, */*',
    'Referer': None,
    'X-Requested-With': 'XMLHttpRequest',
    'Connection': 'keep-alive',
}


class WeiboSpider(object):
    name = "weibo_spider"

    def __init__(self, _topic_result_queue=None):
        self._session = requests.Session()
        self._session.headers.update(headers)

        self._is_login = False
        self._task_queue = queue.Queue(10)
        if _topic_result_queue:
            self._topic_result_queue = _topic_result_queue
        else:
            self._topic_result_queue = queue.Queue(100)
        self.init()

    def login(self, username, password):
        """
        登录微博
        """
        pass

    def get_user_info(self, user_id):
        """
        获取用户信息
        """
        pass

    def _load_topic(self,params,topic_keyword):
        url = 'https://m.weibo.cn/api/container/getIndex'
        response_dict = {}
        topic_loop_dict = {}
        time.sleep(random.randint(1, 5))
        logger.info("Crawl topic %s", params)
        r = self._session.get(url = url,proxies = proxies,params = params,headers = headers)
        response = r.json()
        Referer = r.url
        response_dict['response'] = response
        response_dict['keyword'] = "#" + topic_keyword +"#"
        response_dict['page'] = 000
        response_dict['topic'] = 1
        try:
            since_id = response['data']['pageInfo']['since_id']
            containerid = response['data']['pageInfo']['containerid']
        except Exception as e:
            logger.info('Topic=%s Finish!', topic_keyword)
        else:
            topic_loop_dict['since_id'] = since_id
            topic_loop_dict['containerid'] = containerid
            topic_loop_dict['value'] = topic_keyword
            topic_loop_dict['from'] = 'feed'
            topic_loop_dict['type'] = 'topic'
            
            self._task_queue.put(topic_loop_dict)

        self._topic_result_queue.put(response_dict)


    def query_topic(self, topic_keyword):
        """
        获取微博内容话题
        """
        
        params = {
            'from': 'feed',
            'type': 'topic',
            'value': topic_keyword
            }
        self._load_topic(params,topic_keyword)


    def _topic_loop(self):
        '''
        筛选话题
        '''
        while True:
            params = self._task_queue.get()
            topic_keyword = params['value']
            self._load_topic(params,topic_keyword)
           
    def init(self):
        t = threading.Thread(target=self._topic_loop)
        t.setDaemon(True)
        t.start()

    def query_keyword(self, keyword, page):
        """
        根据关键词搜索微博
        """
        logger.debug('Search keyword=%s, page=%s', keyword, page)
        params = {
            'type': 'all',
            'queryVal': keyword,
            'luicode': '10000011',
            'lfid': '106003type=1',
            'title': keyword,
            'containerid': '100103type=1&q=' + keyword,
            'page': page
        }
        url = 'https://m.weibo.cn/api/container/getIndex'
        response_dict = {}
        r = self._session.get(url=url, proxies = proxies,params=params, headers=headers)
        headers['Referer'] = r.url
        response = r.json()

        if response['ok'] == 0:
            if 'errno' in response.keys():
                logger.warning("Retry: keyword=%s, page=%s, response=%s", keyword, page, response)
                time.sleep(5)
                return self.query_keyword(keyword, page)
        
        response_dict['response'] = response
        response_dict['keyword'] = keyword
        response_dict['page'] = page
        response_dict['topic'] = 0
        # self._task_queue.put(response_dict)
        return response_dict

    def main(self):
        for page in range(100, 110):

            keyword = '面包'
            # page = 6
            a = self.query_keyword(keyword, page)


if __name__ == '__main__':
    ws = WeiboSpider()
    ws.main()
