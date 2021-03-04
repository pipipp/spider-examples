# -*- coding: utf-8 -*-

# Define here the models for your spiders middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import random
import pymongo
from scrapy import signals


class LagouSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spiders middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spiders
        # middleware and into the spiders.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spiders or process_spider_input() method
        # (from other spiders middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spiders, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class LagouDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    @staticmethod
    def get_random_proxy():
        """
        从MongoDB数据库中随机取出一个代理IP
        :return:
        """
        client = pymongo.MongoClient(host='localhost', port=27017)
        database = client['proxy_info']
        valid_proxy_ip_table = database['valid_proxy_ip']
        random_proxy = random.choice([i for i in valid_proxy_ip_table.find()])
        print('Get random proxy: {}'.format(random_proxy))
        return 'https://{}:{}'.format(random_proxy['ip'], random_proxy['port'])

    def process_request(self, request, spider):
        # 给request对象加上proxy
        # proxy = self.get_random_proxy()
        # request.meta['proxy'] = proxy
        pass

    def process_response(self, request, response, spider):
        # 对返回的response处理
        if response.status != 200:
            # 换一个proxy，继续请求
            proxy = self.get_random_proxy()
            request.meta['proxy'] = proxy
            return request
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
