# coding: utf-8
import pymongo
import json
import logging
from datetime import datetime
import uuid

from .utils import to_abs_date

logger = logging.getLogger(__name__)

class WeiboStorage(object):
    min_date = {}

    def __init__(self):
        self._conn = None

    def init_conn(self, host, port):
        if self._conn is None:
            self._conn = pymongo.MongoClient(host=host, port=port)
            self.db = self._conn['weibo']
            self.db.user.create_index('uid', unique=True)
            self.db.weibo.create_index('mid', unique=True)

    def _update_min_date(self, keyword, date):
        """更新min_date"""
        if keyword not in self.min_date:
            self.min_date[keyword] = date
        else:
            self.min_date[keyword] = min(self.min_date[keyword], date)

    def save(self, data):
        """
        保存网页抓取的信息
        """
        keyword = data['keyword']
        body = data['response']
        page = data['page']
        save_flag = False
        save_cnt = 0
        # if data['topic'] == 0:
        try:
            for card in body['data']['cards']:
                for item in card.get('card_group', []):
                    if item['card_type'] == 9 or item.get('card_type_name') == '微博':
                        mblog_data = item['mblog']
                        user_data = mblog_data['user']
                        valid_fields = ['created_at', 'id', 'text',
                                        'reposts_count', 'comments_count', 'attitudes_count']
                        weibo_data = {k: mblog_data[k] for k in valid_fields}
                        # 微博发帖人与user表关联
                        weibo_data['uid'] = str(user_data['id'])
                        weibo_data['searched_keyword'] = keyword


                        datetimes = to_abs_date(weibo_data['created_at'])
                        if datetimes == datetime.fromtimestamp(0):
                            logger.warning('datetime error :%s', weibo_data)
                        weibo_data['created_at'] = datetimes

                        if data['topic'] == 0: 
                            # 为微博，不为话题
                            self._update_min_date(keyword, weibo_data['created_at'])
                        self.save_user_info(user_data)
                        self.save_weibo(weibo_data)
                        save_flag = True
                        save_cnt += 1

            logger.info("Crawled %s items for keyword=%s, page=%s ", save_cnt, keyword, page)
        except:
            logger.error("Crawl Error: %s", data, exc_info=True)

        if not save_flag:
            with open('{}_{}.json'.format(keyword, data['page']), 'w') as F:
                F.write(json.dumps(data))

    def save_user_info(self, user_info_dict):
        """
        保存用户信息
        """
        valid_fields = ['id', 'screen_name', 'profile_image_url', 'statuses_count', 'description',
                        'verified', 'verified_reason', 'gender', 'followers_count', 'follow_count']
        valid_user_info = {k: user_info_dict.get(k) for k in valid_fields}
        valid_user_info['uid'] = str(valid_user_info.pop('id'))
        valid_user_info['gmt_created'] = datetime.now()
        if self.db.user.find({'uid': valid_user_info['uid']}).count() == 0:
            self.db.user.insert(valid_user_info)

    def save_weibo(self, weibo_dict):
        """
        保存微博信息
        """
        weibo_dict['mid'] = str(weibo_dict.pop('id'))
        weibo_dict['gmt_created'] = datetime.now()
        if self.db.weibo.find({'mid': weibo_dict['mid']}).count() == 0:
            self.db.weibo.insert(weibo_dict)


def main():
    import json
    with open('./mli_weibo/data.txt') as F:
        data = json.load(F)
        data = {
            'keyword': 'keyword',
            'page': 1,
            'response': data
        }
        storage = WeiboStorage()
        storage.save(data)
        print(storage.min_date)


if __name__ == '__main__':
    main()
