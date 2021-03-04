# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
import json

from scrapy.exporters import CsvItemExporter
from collections import OrderedDict


class CsvPipeline(object):
    """
    写入有序的数据到CSV表格
    """
    def __init__(self):
        self.file = open('./result/crawl_result.csv', 'wb')
        self.exporter = CsvItemExporter(self.file, encoding='gbk')
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        item = OrderedDict(item)  # 转换为有序的字典
        item = json.dumps(item, ensure_ascii=False)  # 转换为JSON格式
        self.exporter.export_item(eval(item))  # 输出到CSV表格
        return item


class TextPipeline(object):
    """
    清洗过滤数据
    """
    def process_item(self, item, spider):
        """
        删除多余的空白行
        :param item:
        :param spider:
        :return:
        """
        for key, value in item.items():
            if isinstance(value, str):
                item[key] = value.strip()
            elif isinstance(value, (tuple, list)):
                item[key] = [i.strip() for i in value]
        return item


class MongoPipeline(object):
    """
    保存爬虫数据到Mongodb
    """
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.client = None
        self.db = None

    @classmethod
    def from_crawler(cls, crawler):
        """
        使用类方法，返回带有MONGO_URI和MONGO_DB值的类实例
        :param crawler:
        :return: 类实例
        """
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )

    def open_spider(self, spider):
        """
        打开Mongodb连接
        :param spider:
        :return:
        """
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def process_item(self, item, spider):
        """
        保存所有数据到Mongodb
        :param item:
        :param spider:
        :return:
        """
        name = item.__class__.__name__
        items = dict(item)
        self.db[name].update_one(items, {"$set": items}, upsert=True)  # 数据去重
        return item

    def close_spider(self, spider):
        """
        关闭Mongodb连接
        :param spider:
        :return:
        """
        self.client.close()
