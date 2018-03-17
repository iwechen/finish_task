# coding: utf-8

from datetime import datetime, timedelta, date, time

import logging
logger = logging.getLogger(__name__)


def to_abs_date(rel_date_str):
    """相对时间转换为绝对时间
        刚刚
        X小时前
        昨天 XX:XX
        月-日
        年-月-日
    """
    now = datetime.now()
    today = now.date()
    if rel_date_str.count('-') == 2:
        # 年-月-日
        try:
            abs_date = datetime.strptime(rel_date_str, "%y-%m-%d")
        except:
            abs_date = datetime.strptime(rel_date_str, "%Y-%m-%d")
    elif rel_date_str.count('-') == 1:
        # 月-日
        dt = datetime.strptime(rel_date_str, '%m-%d')
        abs_date = dt.replace(year=now.year)
    elif '小时前' in rel_date_str:
        hour_delta = int(rel_date_str[:-3].strip())
        abs_date = (now - timedelta(hours=hour_delta)).date()
    elif '昨天' in rel_date_str:
        abs_date = today - timedelta(days=1)
    elif rel_date_str == '刚刚' or '分钟前' in rel_date_str:
        abs_date = today
    else:
        abs_date = datetime.fromtimestamp(0)
        logger.error("date string parse error: %s", rel_date_str)
    
    if isinstance(abs_date, date):
        abs_date = datetime.combine(abs_date, time.min)
    return abs_date

def main():
    to_abs_date('昨天')

if __name__ == '__main__':
    main()
