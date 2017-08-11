# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb.cursors
import MySQLdb
from twisted.enterprise import adbapi


class ElasticsearchPiepline(object):
    def process_item(self, item, spider):
        item.save_to_es()
        return item


class ZhuhuspiderSynPipeline(object):
    """同步插入数据库"""
    def __init__(self):
        '''初始化数据库'''
        self.__db = "zhihu"
        self.__user = "root"
        self.__passwd = "root"
        self.__host = "127.0.0.1"
        self.__port = 3306
        self.__charset = "utf8"
        self.__connect = None
        self.__cursor = None

    def _connect_db(self):
        """
            dbManager._connect_db()
        连接数据库
        """
        params = {
            "db": self.__db,
            "user": self.__user,
            "passwd": self.__passwd,
            "host": self.__host,
            "port": self.__port,
            "charset": self.__charset
        }
        self.__connect = MySQLdb.connect(**params)
        self.__cursor = self.__connect.cursor()

    def _close_db(self):
        '''
            dbManager._close_db()
        关闭数据库
        '''
        self.__cursor.close()
        self.__connect.close()

    def process_item(self, item, spider):
        inser_sql, params = item.insert_to_db()
        self._connect_db()
        self.__cursor.execute(inser_sql, params)
        self.__connect.commit()
        self._close_db()

    @classmethod
    def from_crawl(cls, crawl):
        return cls()


class ZhuhuspiderPipeline(object):
    """异步插入数据库"""
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host="127.0.0.1",
            db="zhihu",
            user="root",
            passwd="root",
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)
        return cls(dbpool)

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)

    def handle_error(self, failure, item, spider):
        print(failure)

    def do_insert(self, cursor, item):
        insert_sql, params = item.insert_to_db()
        cursor.execute(insert_sql, params)
