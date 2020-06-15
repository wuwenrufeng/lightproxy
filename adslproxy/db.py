#coding:utf-8
import redis
import random
from adslproxy.config import *

class RedisClient(object):
    def __init__(self,host=REDIS_HOST,port=REDIS_PORT,password=REDIS_PASSWORD,proxy_key=PROXY_KEY):
        """
        初始化Redis连接
        :param host:Redis地址
        :param port:Redis端口
        :param password:Redis密码
        :param proxy_key:Redis哈希表名
        """
        # decode_responses=true表示写入的键值对中的value为str类型，否则是字节类型
        self.db = redis.StrictRedis(host=host,port=port,password=password,decode_responses=True)
        self.proxy_key = proxy_key
    
    def set(self,name,proxy):
        """
        设置代理
        :param name:主机名称
        :param proxy:代理
        :return:设置结果
        """
        # hset key filed value将哈希表key中的字段filed的值设为value
        # filed ->主机名称
        # value ->代理
        return self.db.hset(self.proxy_key, name,proxy)
    
    def get(self,name):
        """
        获取代理
        :param name:主机名称
        :return: 代理
        """
        # hget key filed获取存储在哈希表key中指定字段filed的值
        return self.db.hget(self.proxy_key,name)
    
    def count(self):
        """
        获取代理总数
        :return:代理总数
        """
        # hlen key 获取哈希表key中字段的数量
        return self.db.hlen(self.proxy_key)

    def remove(self,name):
        """
        删除代理
        :param name:主机名称
        :return:删除结果
        """
        # hdel key field1[filed2]删除一个或多个哈希表key里的字段field
        return self.db.hdel(self.proxy_key,name)
    
    def names(self):
        """
        获取主机名称列表
        :return: 获取主机名称列表
        """
        # hkeys key 获取所有哈希表key中的字段field
        return self.db.hkeys(self.proxy_key)
    
    def proxies(self):
        """
        获取代理列表
        :return: 代理列表
        """
        # hvals key 获取哈希表key中的所有值value
        return self.db.hvals(self.proxy_key)

    def random(self):
        """
        随机获取代理
        :return:代理
        """
        proxies = self.proxies()
        return random.choice(proxies)

    def all(self):
        """
        获取所有字典
        :return:字典
        """
        # hgetall key 获取在哈希表key中的所有字段和值
        return self.db.hgetall(self.proxy_key)
