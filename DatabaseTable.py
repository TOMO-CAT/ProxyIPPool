"""
Created on Tue Jan 29 10:21:51 2019

@author: TOMOCAT

"""

"""
cursor为游标，常用于脚本的处理

调用方法：
from database import IPPool
pool=IPPool(table_name)
pool.push(ip_list)# 存入
pool.pull(random_flag)# 取出,random_flag 为True时随机取一个
pool.delete(ip) # 删除，delete_all = True时删除所有记录

"""


import sqlite3 ##可以在 Python 程序中使用 SQLite 数据库
import time

class IPPool(object):
    ##存储ip的数据库，包括两张表ip_table和all_ip_table
    ##insert和建表语句绑定在一起

    def __init__(self,table_name):
        self.__table_name = table_name
        self.__database_name = "IP.db"   ##IPPool对应的数据库为IP.db
    ##初始化类，传入参数table_name
    
    
    def create(self):
        conn = sqlite3.connect(self.__database_name, isolation_level = None)
        conn.execute(
            "create table if not exists %s(IP CHAR(20) UNIQUE, PORT INTEGER, ADDRESS CHAR(50), TYPE CHAR(50), PROTOCOL CHAR(50))"
            % self.__table_name)
        print("IP.db数据库下%s表建表成功" % self.__table_name)
    ##建表语句

    
    def insert(self, ip):
        conn = sqlite3.connect(self.__database_name, isolation_level = None)
        #isolation_level是事务隔离级别，默认是需要自己commit才能修改数据库，置为None则自动每次修改都提交
        for one in ip:
            conn.execute(
                "insert or ignore into %s(IP, PORT, ADDRESS, TYPE, PROTOCOL) values (?,?,?,?,?)"
                % (self.__table_name),
                (one[0], one[1], one[2], one[3], one[4]))
        conn.commit() #提交insert 但是已经设置isolaion_level为None，所以应该不需要
        conn.close()

    def select(self,random_flag = False):
        conn = sqlite3.connect(self.__database_name,isolation_level = None)
        ##连接数据库
        cur=conn.cursor()
        #cursor用于接受返回的结果
        
        if random_flag:
            cur.execute(
                "select * from %s order by random() limit 1"
                % self.__table_name)
            result = cur.fetchone()
            #如果是random_flag为T则随机抽取一条记录并返回
        else:
            cur.execute("select * from %s" % self.__table_name)
            result = cur.fetchall()
        cur.close()
        conn.close()
        return result
    
    def delete(self, IP = ('1',1,'1','1','1'), delete_all=False):
        conn = sqlite3.connect(self.__database_name,isolation_level = None)
        if not delete_all:
            n = conn.execute("delete from %s where IP=?" % self.__table_name,
                        (IP[0],))
            #逗号不能省，元组元素只有一个的时候一定要加
            print("删除了",n.rowcount,"行记录")
        else:
            n = conn.execute("delete from %s" % self.__table_name)
            print("删除了全部记录，共",n.rowcount,"行")
        conn.close()
  
    

'''sqlite3如何读取本地db文件：
conn = sqlite3.connect('C:\\Users\\YANG\\Desktop\\抓取代理IP\\IP.db',isolation_level = None) #连接本地数据库
cur = conn.cursor()
cur.execute("select * from ip_table limit 10")
cur.fetchall()
'''

'''
测试模块功能：
test_ip_table = IPPool('test_ip_table')
test_ip_table.create()
test_ip_table.insert([(1,2,3,4,5),(1,2,2,2,2)]);test_ip_table.select()  ##主键冲突时第二条记录不插入
test_ip_table.insert([('120.198.243.52', 80, '高匿名', 'HTTP', '广东省移动'),('118.193.155.186', 80, '高匿名', 'HTTP', '香港特别行政区中国电信国际数据中心')]) ##插入两条记录
##test_ip_table.insert(['120.198.243.52', 80, '高匿名', 'HTTP', '广东省移动']) ##去掉括号后会报错,因为是for one in IP
test_ip_table.select()
test_ip_table.delete(delete_all = True)
'''
