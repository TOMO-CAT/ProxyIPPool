# ProxyIPPool
从零开始构建自己的代理IP池；根据代理IP网址抓取新的代理IP；对历史代理IP有效性验证
## 为什么要使用代理IP
在爬虫的过程中，很多网站会采取反爬虫技术，其中最经常使用的就是限制一个IP的访问次数。当你本地的IP地址被该网站封禁后，可能就需要换一个代理来爬虫。其中有很多网站提供免费的代理IP（如www.xicidaili.com），**我们需要做的就是从代理网站抓取代理IP，测试代理IP的有效性后将合适的代理IP加入数据库表中作为我们爬虫的代理IP池**。
## 开发思路
### 1、通过本地IP抓取第一批启动代理IP
我们从代理IP网站抓取代理IP的过程本身就是爬虫，如果短时间内请求次数过多会被网站禁止访问，因此我们需要利用本地IP去抓取第一批代理IP，然后使用代理IP去抓取新的代理IP。
### 2、对第一批启动的代理IP验证有效性后存入数据库
我们在数据库IP.db下建了两个表：proxy_ip_table（存储所有抓取的IP，用于查看抓取IP功能是否正常）和validation_ip_table（存储所有通过验证的IP，用于查看IP有效性）
第一步中获取的代理IP经检验后存入validation_ip_table，检验的实现如下：
```
def ip_validation(self, ip):
    #判断是否高匿:非高匿的ip仍会出卖你的真实ip
    anonymity_flag = False
    if "高匿" in str(ip):
        anonymity_flag = True

    IP = str(ip[0]) + ":" + str(ip[1]);IP
    url = "http://httpbin.org/get" ##测试代理IP功能的网站
    proxies = { "https" : "https://" + IP}   #为什么要用https而不用http我也不清楚
    headers = FakeHeaders().random_headers_for_validation()

    #判断是否可用
    validation_flag = True
    response = None

    try:
        response = requests.get(url = url, headers = headers, proxies = proxies, timeout = 5)
    except:
        validation_flag = False
    if response is None :
        validation_flag = False
        
    if anonymity_flag and validation_flag:
        return True
    else:
        return False
```
##### 3、构建待访问的网址列表并循环抓取，每次抓取的ip_list经验证后存入数据库表
我们构建了待访问的网址列表（暂定100个容易跑完）：
```
self.URLs = [ "https://www.xicidaili.com/nn/%d" % (index + 1) for index in range(100)] 
```
## 包含的模块
### 1、RandomHeaders.py
构造随机请求头，用于模拟不同的网络浏览器，调用方式：
```
from RandomHeaders import FakeHeaders
#返回请求xici代理网站的请求头
xici_headers = FakeHeaders().random_headers_for_xici
```
### 2、DatabaseTable.py
提供数据库的创建表和增删查功能，调用方式：
```
from DatabaseTable import IPPool
tablename = "proxy_ip_table"
#tablename也可以是validation_ip_table
IPPool(tablename).create() #创建表
IPPool(tablename).select(random_flag = False）
# random_flag = True时返回一条随机记录，否则返回全部记录
IPPool(table_name).delete(delete_all = True) #删除全部记录
```
### 3、GetProxyIP.py
核心代码，有几个函数可以实现不同的功能：

* 从0开始完成建表、抓取IP和存入数据库的功能
```
from GetProxyIP import Carwl
Crawl().original_run()
```

* 当代理IP个数不够的时候，根据url_list列表进行抓取，将合适的IP存入列表

```
from GetProxyIP import Carwl
#其他提供代理IP的网站
url_kuaidaili = ["https://www.kuaidaili.com/free/inha/%d" % (index + 1) for index in range(10,20)]
Crawl().get_more_run(url_list)
```
![0e2a6e968d27fd6f6d70c03ced6bdadd.png](en-resource://database/507:1)

* 当IP池太久没用时，需要对IP有效性进行验证，不符合要求的IP需要删除
```
from GetProxyIP import Carwl
Crawl().proxy_ip_validation()
```
![1dc07d4708d6d8ec681fff1dbb952707.png](en-resource://database/509:1)
