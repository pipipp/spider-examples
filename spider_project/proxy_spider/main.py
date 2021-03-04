"""
代理爬虫和代理验证执行模块
"""
# -*- coding:utf-8 -*-
import threading
import logging

from spider_project.proxy_spider.profile.proxy_spider import ProxySpider
from spider_project.proxy_spider.profile.proxy_check import ProxyCheck

from spider_project.proxy_spider.settings import proxy_spider_settings
from spider_project.proxy_spider.settings import proxy_check_settings

__author__ = 'Evan'
logger = logging.getLogger(__name__)


class ProxyHandle(object):

    def __init__(self):
        self.proxy_spider = ProxySpider(config=proxy_spider_settings)  # 实例化代理爬虫类
        self.proxy_check = ProxyCheck(config=proxy_check_settings)  # 实例化代理检查类

    def crawl_xila_proxy(self):
        """
        多线程爬取西拉网站代理IP
        :return:
        """
        threads = []
        logger.info('开始多线程爬取西拉网站代理IP(抓取页数:{}, 线程池:{})...'
                    .format(proxy_spider_settings['MAX_PAGE'], proxy_spider_settings['THREAD_POOL_MAX']))
        for page in range(1, proxy_spider_settings['MAX_PAGE'] + 1):
            t = threading.Thread(target=self.proxy_spider.get_xila_proxy_ip, args=(page,))
            threads.append(t)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()
        logger.info('西拉网站代理IP爬取完毕，共爬取{}个代理IP\n'
                    .format(len([i for i in self.proxy_spider.all_proxy_ip_table.find()])))

    def verify_proxy_ip(self, delete_invalid_proxy=False):
        """
        多线程验证代理IP的有效性
        :param delete_invalid_proxy: [bool] - 如果设置为True，则删除无效的代理
        :return:
        """
        threads = []
        all_proxy = [i for i in self.proxy_check.all_proxy_ip_table.find()]
        logger.info('开始多线程验证所有代理IP的有效性(所有代理数量:{}, 线程池:{})...'
                    .format(len(all_proxy), proxy_check_settings['THREAD_POOL_MAX']))
        for proxy_info in all_proxy:
            t = threading.Thread(target=self.proxy_check.verify_proxy_ip, args=(proxy_info, delete_invalid_proxy))
            threads.append(t)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()
        logger.info('所有代理IP验证完毕，共{}个有效代理IP\n'
                    .format(len([i for i in self.proxy_check.valid_proxy_ip_table.find()])))


def main():
    proxy_handle = ProxyHandle()
    proxy_handle.crawl_xila_proxy()  # 爬取西拉免费代理网站
    proxy_handle.verify_proxy_ip(delete_invalid_proxy=False)  # 验证所有代理IP的有效性


if __name__ == '__main__':
    main()
