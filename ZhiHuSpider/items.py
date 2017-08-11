# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from datetime import datetime


class ZhuhuQuestionItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()
    author_name = scrapy.Field()
    author_avatar = scrapy.Field()
    author_gender = scrapy.Field()
    url = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    answer_count = scrapy.Field()
    title = scrapy.Field()
    follower_count = scrapy.Field()
    content = scrapy.Field()
    comment_count = scrapy.Field()
    crawl_time = scrapy.Field()

    def insert_to_db(self):
        # 将数据插入数据库
        insert_sql = """
            insert into question(id, author_name, author_avatar, author_gender, url,
            create_time, update_time, answer_count, title, follower_count, content, comment_count, crawl_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE update_time=VALUES(update_time), answer_count=VALUES(answer_count),
             follower_count=VALUES(follower_count), content=VALUES(content), comment_count=VALUES(comment_count),
             crawl_time=VALUES(crawl_time)
        """

        id = self["id"]
        author_name = self["author_name"]
        author_avatar = self["author_avatar"]
        author_gender = self["author_gender"]
        url = self["url"]
        create_time = datetime.fromtimestamp(int(self["create_time"])).strftime('%Y-%m-%d')
        update_time = datetime.fromtimestamp(int(self["update_time"])).strftime('%Y-%m-%d')
        answer_count = self["answer_count"]
        title = self["title"]
        follower_count = self["follower_count"]
        content = self["content"]
        comment_count = self["comment_count"]
        crawl_time = self["crawl_time"]

        params = (id, author_name, author_avatar, author_gender, url, create_time, update_time, answer_count,
                  title, follower_count, content, comment_count, crawl_time)

        return insert_sql, params


