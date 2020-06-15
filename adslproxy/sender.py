#coding:utf-8
# 在拨号主机端运行的拨号脚本，要求：定时拨号；获取ip后进行有效检测；更新redis数据
import re
import time
import requests
from requests.exceptions import ConnectionError,ReadTimeout
from adslproxy.db import RedisClient
from adslproxy.config import *
import platform
import subprocess

# 主要作用：执行拨号，并将新的IP测试通过之后更新到远程Redis散列表里
class Sender(object):
    def get_ip(self,ifname=ADSL_IFNAME):
        """
        获取本机IP
        :param ifname:网卡名称
        :return:ip
        """
        (status,output) = subprocess.getstatusoutput('ifconfig')
        if status == 0:
            # 加入re.S修饰符，使.匹配包括换行符在内的所有字符
            pattern = re.compile(ifname + '.*?inet.*?(\d+\.\d+\.\d+\.\d+).*?netmask',re.S)
            result = re.search(pattern,output)
            if result:
                ip = result.group(1)
                return ip
    
    def test_proxy(self,proxy):
        """
        测试代理
        :param proxy:代理
        :return:测试结果
        """
        proxies = {
            'http':'http://' + proxy,
            'https':'https://' + proxy
        }
        try:
            response = requests.get(TEST_URL,proxies=proxies,timeout=TEST_TIMEOUT)
            if response.status_code == 200:
                return True
        except (ConnectionError,ReadTimeout):
            return False
    
    def remove_proxy(self):
        """
        移除代理
        :return:None
        """
        self.redis = RedisClient()
        self.redis.remove(CLIENT_NAME)
        print('Successfully Removed Proxy')
    
    def set_proxy(self,proxy):
        """
        设置代理
        :param proxy:代理
        :return: None
        """
        self.redis = RedisClient()
        if self.redis.set(CLIENT_NAME,proxy):
            print('Successfully Set Proxy',proxy)
    
    def adsl(self):
        """
        拨号主进程
        :return:None
        """
        while True:
            print('ADSL Start, Remove Proxy, Please wait')
            # 将远程Redis散列表中的本机对应的代理移除，避免拨号时本主机的残留代理被取到
            try:
                self.remove_proxy()
            except:
                while True:
                    (status,output) = subprocess.getstatusoutput(ADSL_BASH)
                    if status == 0:
                        self.remove_proxy()
                        break
            # 拨号脚本：stop之后再start
            (status,output) = subprocess.getstatusoutput(ADSL_BASH)
            if status == 0:
                print('ADSL Successfully')
                ip = self.get_ip()
                if ip:
                    print('Now IP',ip)
                    print('Testing Proxy,Please wait')
                    proxy = '{ip}:{port}'.format(ip=ip,port=PROXY_PORT)
                    print('proxy info:',proxy)
                    if self.test_proxy(proxy):
                        print('Valid Proxy')
                        # 代理有效时，更新Redis散列表
                        self.set_proxy(proxy)
                        time.sleep(ADSL_CYCLE)
                    else:
                        print('Invaild Proxy')
                else:
                    print('Get Ip Failed,Please Check')
                    time.sleep(ADSL_CYCLE)
            else:
                print('ADSL Failed,Please Check')
                time.sleep(ADSL_CYCLE)
    
def run():
    sender = Sender()
    sender.adsl()

if __name__ == '__main__':
    run()


            