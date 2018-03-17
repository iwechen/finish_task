# 新浪微博爬虫

### 数据字段字义



**表名：**user

**说明：**存储了微博用户的相关信息

| 字段名            | 类型     | 说明           |
| ----------------- | -------- | -------------- |
| screen_name       | Str      | 微博名         |
| profile_image_url | str      | 头像地址       |
| statuses_count    | int      | 历史微博总数   |
| description       | str      | 账号介绍       |
| verified          | bool     | 是否为认证账号 |
| verified_reason   | str      | 认证说明       |
| gender            | str      | 性别（f，m）   |
| followers_count   | int      | 粉丝数         |
| follow_count      | int      | 关注数         |
| uid               | str      | 微博账号id     |
| gmt_created       | datetime | 入库时间       |

**表名：**weibo

**说明：** 存储每条微博相关数据

| 字段名           | 类型     | 说明                     |
| ---------------- | -------- | ------------------------ |
| created_at       | datetime | 发微博时间               |
| text             | str      | 微博正文                 |
| reposts_count    | int      | 转发数                   |
| comments_count   | int      | 评论数                   |
| attitudes_count  | int      | 点赞数                   |
| uid              | str      | 博主id,和user表中uid关联 |
| mid              | str      | 微博id                   |
| gmt_created      | datetime | 入库时间                 |
| searched_keyword | str      | 查询的关键词             |

