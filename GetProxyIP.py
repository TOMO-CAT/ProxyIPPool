# -*- coding: utf-8 -*-
"""
Created on Fri Feb  8 01:47:15 2019
@author: YANG
作用：从xicidaili中爬取代理IP并保存在数据库中
"""




from fake_useragent import UserAgent 
import requests
from RandomHeaders import FakeHeaders
from DatabaseTable import IPPool
import random
from bs4 import BeautifulSoup
import re



'''
proxy_ip_table: 只抓取xici网前100页的数据(以后需要更多ip可以跑后面的表)
validation_ip_table: 检验有效的ip存入该表
'''
class Crawl(object):
    
    def __init__(self):
        self.__DATABASE_NAME = "IP.db"   ##最终存放ip的数据库
        self.__TABLE_NAME = "proxy_ip_table" ##最终存放代理ip的数据库表
        self.URLs = [ "https://www.xicidaili.com/nn/%d" % (index + 1) for index in range(100)] 
        ## 注意网站写http与https可能会在使用代理IP时出现问题
        self.__VALIDATION_IP_TABLE_NAME = "validation_ip_table" #通过测试后可用的高匿代理IP
    
    def crawl(self,url, headers, proxies = False, retry_times = 3):
        #自定义crawl()函数：爬取网页内容，实现多次重试和解码的问题
        
        response = None #None永远表示False
        
        #proxy_ip = IPPool(self.__TABLE_NAME).select(random_flag=True)
        
        for cnt in range(retry_times): ##实现多次重试
            try:
                if not proxies:
                    response = requests.get(
                        url=url, headers=headers, timeout=5)
                else:
                    response = requests.get(
                        url=url, headers=headers, proxies=proxies, timeout=5)
                    ##设置代理
                break
            except Exception:
                continue
            
        if response is None:
            print(u"请求该url出错:%s" % url)
            return None
        try:
            html = response.content.decode("utf-8")
            return html
        except Exception:
            return None
        
    def parse(self,html):
        #解析html得到该网页的IP列表
        
        if html is None:
            return
        # ??直接return的话有什么优势?
        all_ip = []
        soup = BeautifulSoup(html, "lxml")
        tds = soup.find_all("td")
        for index, td in enumerate(tds):
            #print(u"解析html进度：{}/{}".format(index + 1, len(tds)))
            if re.match(r"^\d+\.\d+\.\d+\.\d+$",
                        re.sub(r"\s+|\n+|\t+", "", td.text)):
                item = []
                item.append(re.sub(r"\s+|\n+|\t+", "", td.text))
                item.append(re.sub(r"\s+|\n+|\t+", "", tds[index + 1].text))
                item.append(re.sub(r"\s+|\n+|\t+", "", tds[index + 2].text))
                item.append(re.sub(r"\s+|\n+|\t+", "", tds[index + 3].text))
                item.append(re.sub(r"\s+|\n+|\t+", "", tds[index + 4].text))
                all_ip.append(item)
            #else:
                #print(u"该td是不匹配的项!")
        return all_ip
    
    def __create_ip_table(self):
        #创建存储爬取的代理IP的数据库表和通过验证的代理IP数据库表
        IPPool(self.__TABLE_NAME).create()
        IPPool(self.__VALIDATION_IP_TABLE_NAME).create()
        
        
    
    def save_ip(self, url, headers, proxies):
        #将ip列表保存到数据库
        html = self.crawl(url, headers, proxies) #获取url的html
        
        #self.__create_ip_table() #创建存储代理IP的数据库表
        
        if html is None:
            return
        ip_list = self.parse(html)
        
        if ip_list is None or len(ip_list) < 1:
            return 
        if len(ip_list) == 1:
            IPPool(table_name = self.__TABLE_NAME).insert([ip_list])
        else:
            IPPool(table_name = self.__TABLE_NAME).insert(ip_list)

    def proxies(self):
        '''构造代理IP,需要提供代理IP保存的数据库名称和表名'''
        ip = IPPool(self.__VALIDATION_IP_TABLE_NAME).select(random_flag = True)
        if ip:
            IP = str(ip[0]) + ":" + str(ip[1])
            return {"http": "http://" + IP}
        else:
            return None
    
    
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
    '''测试ip_validation功能
    ip = IPPool("proxy_ip_table").select(random_flag = True);ip
    IP = str(ip[0]) + ":" + str(ip[1]);IP
    url = "http://httpbin.org/get" ##测试代理IP功能的网站
    proxies = {"https" : "https://" + IP};proxies     ##得用https不然会报错
    headers = FakeHeaders().random_headers_for_validation();headers
    response = requests.get(url = url, headers = headers, proxies = proxies, timeout = 5); response
    
    proxies = {"http" : "http://" + IP};proxies       ##得用http不然会报错
    url_xici = "https://www.xicidaili.com/nn/234"
    headers = FakeHeaders().random_headers_for_xici();headers
    response = requests.get(url = url_xici, headers = headers, proxies = proxies, timeout = 5);response
    response.content.decode("utf-8")
    '''
 
       
    def save_valuable_ip(self,ip_list):
        #对抓取到的IP列表进行判断，有效且高匿的存入validation_ip_table
        cnt = 0 #遍历抓取到的ip
        
        if len(ip_list) == 0:
            print("ip_list为空，请检查网址是否有误")
            return
        
        ip_cnt = len(ip_list)
        validation_ip_cnt = len(IPPool(self.__VALIDATION_IP_TABLE_NAME).select())
        print(u"当前有效ip有{}个".format(validation_ip_cnt))
        count = 0 #统计有效得ip个数
        
        while cnt < ip_cnt:
            # ip有效则
            print(u"正在检测第{}个ip的有效性".format(cnt+1))
            if self.ip_validation(ip_list[cnt]):
                IPPool(self.__VALIDATION_IP_TABLE_NAME).insert([ip_list[cnt]])
                count += 1
            cnt += 1
        
        validation_ip_cnt_2 = len(IPPool(self.__VALIDATION_IP_TABLE_NAME).select())
        print(u"增加有效ip{}个，ip有效率{:.2f}%,有效ip个数为{}".format(count, count/ip_cnt * 100, validation_ip_cnt_2))
        ##{:.2f}保留两位小数

    def get_proxy_ip(self):
        cnt = 0
        url_cnt = len(self.URLs) #总共的url数
        
        while cnt < url_cnt:
            url = self.URLs[cnt]
            cnt += 1
            print(u"开始第{}个url解析，进度{}/{}".format(cnt,cnt,url_cnt))
            headers = FakeHeaders().random_headers_for_xici()
            proxies = self.proxies()
            
            ip_cnt_before = len(IPPool(self.__TABLE_NAME).select()) # 解析url之前的IP数
            
            #解析网页
            html = self.crawl(url, headers, proxies) 
            #得到ip_list  
            if html is None:
                continue #继续解析下一个网址
            ip_list = self.parse(html)
            #将ip_list存入proxy_ip_table中
            
            
            if ip_list is None or len(ip_list) < 1:
                print(u"请求{}没有返回IP列表，可能是503错误，请检查!".format(url))
                continue #跳过这个url，进入下一个循环
                
            if len(ip_list) == 1:
                IPPool(table_name = self.__TABLE_NAME).insert([ip_list])
            else:
                IPPool(table_name = self.__TABLE_NAME).insert(ip_list)
            ip_cnt_after = len(IPPool(self.__TABLE_NAME).select())
            print(u"当前解析的url为{},ip池中的代理ip个数由{}增长为{}".format(url,ip_cnt_before,ip_cnt_after))
            
            #检验ip_list
            self.save_valuable_ip(ip_list)
    
    def original_run(self):
        '''
        第一次启动程序
        包括建表、初始代理IP获取和不断抓取代理IP并验证
        '''
        self.__create_ip_table() #创建存储代理IP的数据库表
        
        #先利用本地ip获取初始的代理ip;跑五次，保证有足够多的初始代理IP
        print("现在开始爬取代理IP网站，抓取代理IP后保存到数据库中，获取第一批代理IP")
        url = random.choice(self.URLs)
        self.save_ip(url = url, headers = FakeHeaders().random_headers_for_xici(), proxies = False)
         
        #对初始代理ip有效性进行验证并存储到validation_ip_table
        #当初始代理ip没有抓取到时，返回错误提示
        ip_list = IPPool(self.__TABLE_NAME).select()
        
        if len(ip_list) == 0:
            print(u"当前proxy_ip_table中无任何IP，请检查是否是{}无法访问!".format(url))
            return
        
        self.save_valuable_ip(ip_list)
        
        #说明初始状态
        ip_num = len(IPPool(self.__TABLE_NAME).select())
        print(u"初始代理ip个数为{}个，现在开始抓取代理IP".format(ip_num))
        
        
        self.get_proxy_ip()
        
        
    def get_more_run(self,url_list):
        #当代理IP个数较少时，获得更多可用的代理IP
        #请求头headers是用于xici代理网站的，如果出错可能要重新设置headers
        cnt = 0
        url_cnt = len(url_list) #总共的url数
        
        while cnt < url_cnt:
            url = url_list[cnt]
            cnt += 1
            print(u"开始第{}个url解析，进度{}/{}".format(cnt,cnt,url_cnt))
            #如果选择解析其他网页，可能会有问题
            headers = FakeHeaders().random_headers_for_xici()
            proxies = self.proxies()
            ip_cnt_before = len(IPPool(self.__TABLE_NAME).select()) # 解析url之前的IP数
            
            #解析网页(利用try解决无法解析html的问题)
            html = self.crawl(url, headers, proxies) 
            
            #得到ip_list  
            if html is None or html == '':
                print("无法获取html内容，请检查{}能否正常访问!".format(url))
                continue #继续解析下一个网址
                
            ip_list = self.parse(html)
            
            #将ip_list存入proxy_ip_table中
            if ip_list is None or len(ip_list) < 1:
                print(u"请求{}没有返回IP列表，可能是503错误，请检查!".format(url))
                continue #跳过这个url，进入下一个循环
            
            if len(ip_list) == 1:
                IPPool(table_name = self.__TABLE_NAME).insert([ip_list])
            else:
                IPPool(table_name = self.__TABLE_NAME).insert(ip_list)
            ip_cnt_after = len(IPPool(self.__TABLE_NAME).select())
            print(u"当前解析的url为{},ip池中的代理ip个数由{}增长为{}".format(url,ip_cnt_before,ip_cnt_after))
            
            #检验ip_list
            self.save_valuable_ip(ip_list)
    
    def proxy_ip_validation(self):
        #对以前存储在validation_ip_table表中的ip进行再次检验，不满足条件的直接删除
        ip_list = IPPool(self.__VALIDATION_IP_TABLE_NAME).select()
        ip_cnt = len(ip_list)
        print(u"共有{}个代理IP，开始进行IP有效性校验!".format(ip_cnt))
        
        cnt = 0
        delete_cnt = 0 #删除掉的ip个数
        
        while cnt < ip_cnt:
            # ip有效则
            print(u"正在检测第{}个ip的有效性".format(cnt+1))
            if self.ip_validation(ip_list[cnt]) == False:
                #如果ip非有效则删除该ip
                IPPool(self.__VALIDATION_IP_TABLE_NAME).delete(ip_list[cnt])
                delete_cnt += 1
            cnt += 1
        
        validation_ip_cnt_2 = len(IPPool(self.__VALIDATION_IP_TABLE_NAME).select())
        print(u"删除无效ip{}个，ip无效率{:.2f}%,最终有效ip个数为{}".format(delete_cnt, delete_cnt/ip_cnt * 100, validation_ip_cnt_2))
        ##{:.2f}保留两位小数       
    


'''初始化
IPPool("validation_ip_table").delete(delete_all = True)
IPPool("proxy_ip_table").delete(delete_all = True)
'''
     
        
      
   
'''测试模块功能————利用本地ip拿到第一批代理ip
test = Crawl()
url = random.choice(test.URLs);url
headers = FakeHeaders().random_headers_for_xici();headers
test.save_ip(url,headers,proxies = False)

IPPool("proxy_ip_table").select()
#IPPool("proxy_ip_table").delete(delete_all = True)
'''
