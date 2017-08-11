# -*- coding=utf8 -*-
import scrapy.cmdline
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
scrapy.cmdline.execute(["scrapy", "crawl", "zhihu"])