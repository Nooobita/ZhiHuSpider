# -*- coding: utf-8 -*-
import scrapy
import time
import datetime
import json
from PIL import Image
from scrapy.selector import Selector
# try:
#     import urlparse as parse
# except Exception:
#     from urllib import parse

from ZhuHuSpider.items import ZhuhuQuestionItem


class ZhihuSpider(scrapy.Spider):
    """知乎爬虫"""
    name = "zhihu"
    allowed_domains = ["www.zhihu.com"]
    # 开始连接
    start_urls = ['https://www.zhihu.com/']

    # 设置请求头
    headers = {
        "Host": "www.zhihu.com",
        "Referer": "https://www.zhihu.com/",
    }

    # 自定义设置
    # custom_settings = {
    #     "COOKIES_ENABLED": True
    # }

    def start_requests(self):
        """重写爬虫开始的函数，完成登录"""
        return [scrapy.Request("https://www.zhihu.com/#signin", headers=self.headers,  callback=self.pre_login)]

    def pre_login(self, response):
        """登录前的准备，获取xsr、请求验证码"""
        response = Selector(response)
        xsrf = response.xpath("//input[@name='_xsrf']/@value").extract()
        # 页面一共有3个xsrf，如果存在就取第一一个
        if xsrf:
            xsrf = xsrf[0]

            data = {
                "_xsrf": xsrf,
                "email": "404673940@qq.com",
                "password": "cheng5214372",
                "captcha": ""
            }

            captcha_time = int(time.time())*1000
            captcha_url = "https://www.zhihu.com/captcha.gif?r={0}&type=login".format(captcha_time)
            yield scrapy.Request(captcha_url, headers=self.headers, callback=self.login, meta={"post_data":data})

    def login(self, response):
        """登录"""
        data = response.meta.get("post_data")

        # 保存验证码
        with open("captcha.jpg", "wb") as img:
            img.write(response.body)

        try:
            image = Image.open("captcha.jpg")
            image.show()
            image.close()
        except Exception as error:
            pass

        captcha = raw_input("请输入验证码\n")
        post_url = "https://www.zhihu.com/login/email"
        data["captcha"] = captcha
        yield scrapy.FormRequest(post_url, headers=self.headers, formdata=data, callback=self.check_login)

    def check_login(self, response):
        """验证是否登录成功，成功开始访问连接"""
        res = json.loads(response.body)
        if res['msg'] == u'登录成功':
            for url in self.start_urls:
                yield scrapy.Request(url, dont_filter=True, headers=self.headers, callback=self.get_article)

    def get_article(self, response):
        """
        """
        cookie = response.request.headers["Cookie"]
        authorization = self.get_cookie(cookie, 'z_c0')

        article_url = "https://www.zhihu.com/api/v3/feed/topstory?limit=10&after_id=0"

        self.headers["authorization"] = "Bearer " + authorization

        yield scrapy.Request(article_url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        """解析请求返回的数据"""
        res_json = json.loads(response.body)
        is_end = res_json["paging"]["is_end"]
        next_url = res_json["paging"]["next"]

        # 提取question的具体字段
        for question in res_json["data"]:
            zhihu_item = ZhuhuQuestionItem()
            try:
                zhihu_item['id'] = question["target"]["question"]["id"] if "question" in question["target"] else question["target"]['id']
                zhihu_item['author_name'] = question["target"]["question"]["author"]["name"] if "question" in question["target"] else question["target"]["author"]['name']
                zhihu_item['author_avatar'] = question["target"]["question"]["author"]["avatar_url"] if "question" in question["target"] else question["target"]["author"]['avatar_url']
                zhihu_item['author_gender'] = question["target"]["question"]["author"].get("gender", '') if "question" in question["target"] else question["target"]["author"].get("gender", "")
                zhihu_item['url'] = self.deal_url(question["target"]["question"]["url"]) if "question" in question["target"] else question["target"]['url']
                zhihu_item['create_time'] = question["target"]["question"]["created"] if "question" in question["target"] else question["target"]['created']
                zhihu_item['update_time'] = question["target"]["updated_time"] if "updated_time" in question["target"] else question["updated_time"]
                zhihu_item['answer_count'] = question["target"]["question"]["answer_count"] if "question" in question["target"] else question["target"]['answer_count']
                zhihu_item['title'] = question["target"]["question"]["title"] if "question" in question["target"] else question["target"]['title']
                zhihu_item['follower_count'] = question["target"]["question"]["follower_count"] if "question" in question["target"] else question["target"]['follower_count']
                zhihu_item['content'] = question["target"].get("excerpt", "")
                zhihu_item['comment_count'] = question["target"]["question"]["comment_count"] if "question" in question["target"] else question["target"]['comment_count']
                zhihu_item["crawl_time"] = datetime.datetime.now()
            except Exception as e:
                with open("error_log.txt", "a+") as error:
                    error.write("--------------------->\n")
                    error.write(e.message + '\n')
                    error.write("row:" + str(question) + "\n")
                    error.write("json:" + str(res_json) + "\n")
            else:
                yield zhihu_item

        if not is_end:
            yield scrapy.Request(next_url, headers=self.headers, callback=self.parse)

    def deal_url(self, url):
        """处理url"""
        return url.replace("questions", "question").replace("api.", "")

    def get_cookie(self, cookies, cookie_name):
        """
            (str) -> 
        cookies -> str
        cookie_name
        获取cookie值
        """
        cookie_dict = dict()
        cookie_list = cookies.split(';')
        for cookie in cookie_list:
            cookie_tupe = cookie.split("=", 1)
            key = cookie_tupe[0].strip()
            cookie_dict[key] = cookie_tupe[1].strip()
        return cookie_dict.get(cookie_name, '')


