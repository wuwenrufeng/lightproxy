#coding:utf-8
from adslproxy.api import server
from adslproxy.db import RedisClient

if __name__ == '__main__':
    redis = RedisClient(host='114.116.13.33',password='mredis333')
    server(redis=redis)
# redis = RedisClient(host='114.116.13.33',password='mredis333')
# random = redis.random()
# print(random)