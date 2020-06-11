# anyproxy
vps动态拨号、搭建vps代理池、扫描收集万维网上开放的代理端口
扫描代理服务器



扫端口我们可以用 nmap 这个工具。nmap 是一个网络扫描的工具，它可以用来扫描对方服务器启用了哪些端口、哪些服务，服务器是否在线，以及猜测服务器可能运行的操作系统。

我们针对一台机器运行 nmap 命令，可以扫出这个机器启用了哪些端口（服务），比如

$ nmap 49.51.193.128

Starting Nmap 7.01 ( https://nmap.org ) at 2019-03-09 20:32 CST
Nmap scan report for 49.51.193.128
Host is up (0.18s latency).
Not shown: 995 closed ports
PORT     STATE    SERVICE
22/tcp   open     ssh
25/tcp   filtered smtp
111/tcp  open     rpcbind
445/tcp  filtered microsoft-ds
1080/tcp open     socks

Nmap done: 1 IP address (1 host up) scanned in 27.34 seconds
要扫出一个网段中的代理服务器，我们可以针对一个网段作扫描，如下

$ nmap 49.51.193.0/24
上面的命令会扫出所有在 49.51.193.0/24这个网段中有哪些在线的机器，每台机器上启用了哪些服务。





检测代理类型



扫出来代理服务器后，我们可以对这些代理服务器做测试，看看它们是什么类型的代理。



代理基本上分成这三种类型：

透明代理

匿名代理

高匿代理



通过字面意思，大致能猜到这三种代理的区别。简单的说，透明代理就是用了之后，对方服务器很清楚的知道你是谁，你来自哪个IP。匿名代理用了之后，对方没法知道你是谁，但是知道你用了代理。而高匿代理比匿名代理隐藏性更高，对方不仅不知道你是谁，也不知道你用了代理。



三者在技术层面的区别，主要在于HTTP请求头的内容不同



透明代理

REMOTE_ADDR = Proxy IP

HTTP_VIA = Proxy IP

HTTP_X_FORWARDED_FOR = Your IP



匿名代理

REMOTE_ADDR = proxy IP

HTTP_VIA = proxy IP

HTTP_X_FORWARDED_FOR = proxy IP



高匿代理

REMOTE_ADDR = Proxy IP

HTTP_VIA = not determined

HTTP_X_FORWARDED_FOR = not determined



检测代理类型的方法也非常简单，只需要自己搭建一个web服务器，在上面跑一个web程序。客户端通过代理向web服务器发起请求，web程序打印出请求头，通过分析请求头的内容就可以知道这个代理是哪种类型的。



下面是我用 Flask 写了一个例子，大致是这么个意思

import json
from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def hello():
    header = {}
    if "REMOTE_ADDR" in request.headers:
        header["REMOTE_ADDR"] = request.headers["REMOTE_ADDR"]
    if "HTTP_VIA" in request.headers:
        header["HTTP_VIA"] = request.headers["HTTP_VIA"]
    if "HTTP_X_FORWARDED_FOR" in request.headers:
        header["HTTP_X_FORWARDED_FOR"] = request.headers["HTTP_X_FORWARDED_FOR"]
    return json.dumps(header)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
运行这个程序，当我们通过代理访问这个web服务，它就会返回代理请求头的信息，我们可以据此判断代理是透明、匿名还是高匿代理。





维护代理池



好，有了代理和代理的类型，我们可以将他们做成一个代理池，提供一个接口给客户，让他们通过接口来获取可用的代理。



当然这些扫出来的代理有效时间长短不一，有的代理也许可以用很久，有的代理可能一会儿时间就失效了。我们需要保证代理池中的代理是有效的，可以定期的去检查代理的有效性，把失效的从列表中去除，把新的有效的加入进来。
