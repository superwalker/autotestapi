#!/usr/bin/env python
# _*_ coding:utf-8 _*_
__author__ = 'YinJia'

import os,sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import setting
from pymysql import connect,cursors
from pymysql.err import OperationalError
import configparser as cparser

# --------- 读取config.ini配置文件 ---------------
cf = cparser.ConfigParser()
cf.read(setting.TEST_CONFIG,encoding='UTF-8')
host = cf.get("mysqlconf","host")
port = cf.get("mysqlconf","port")
user = cf.get("mysqlconf","user")
password = cf.get("mysqlconf","password")
db = cf.get("mysqlconf","db_name")

class DB:
    """
    MySQL基本操作
    """
    def __init__(self):
        '''
        :notes:创建数据库连接，执行所有的sql语句时，只建立一次连接
        '''
        try:
            # 连接数据库
            self.conn = connect(host = host,
                                user = user,
                                password = password,
                                db = db,
                                charset = 'utf8mb4',
                                cursorclass = cursors.DictCursor
                                )
        except OperationalError as e:
            print("Mysql Error %d: %s" % (e.args[0],e.args[1]))

   # 清除表数据
    def clear(self,table_name):
        '''
        :notes:清除表数据，无返回
        :param table_name:清除数据的表名
        '''
        real_sql = "delete from " + table_name + ";"
        with self.conn.cursor() as cursor:
             # 取消表的外键约束
            cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
            cursor.execute(real_sql)
        self.conn.commit()
        self.close()

    # 插入表数据
    def insert(self, table_name, table_data):
        '''
        :notes:插入表数据，无返回
        :param table_name:插入数据的表名
        :param table_data:查询的表字段和字段值，格式为字典，例{key1:value1,key2:value2....}
        '''
        for key in table_data:
            table_data[key] = "'"+str(table_data[key])+"'"
        key   = ','.join(table_data.keys())
        value = ','.join(table_data.values())
        real_sql = "INSERT INTO " + table_name + " (" + key + ") VALUES (" + value + ")"
        with self.conn.cursor() as cursor:
            cursor.execute(real_sql)
        self.conn.commit()
        self.close()

    #精确查询表数据
    def exactselect(self,table_name,table_data,sortdesc):
        '''
        :notes:精确查询表数据，获取排序后的结果
        :author：yulongyan
        :date:2021-11-09
        :param table_name:查询数据的表名
        :param table_data:查询的表字段和字段值，格式为字典，例{key1:value1,key2:value2....}
        :param sortdesc:查询数据的排序字段，按照字段的逆序排序
        :return:返回查询表数据的结果，返回数据类型为列表
        '''
        selectsql=""
        for key in table_data:
            table_data[key] = "'"+str(table_data[key])+"'"
            selectsql=selectsql+key+" = "+table_data[key]+" AND "
        selectsql=selectsql.rstrip(' AND ')
        real_sql = "SELECT * FROM " + table_name +" WHERE " + selectsql+" ORDER BY "+sortdesc+" DESC"
        with self.conn.cursor() as cursor:
            cursor.execute(real_sql)
        self.conn.commit()
        self.close()
        return cursor.fetchall()

    #模糊查询表数据
    def dimselect(self,table_name,table_data,sortdesc):
        '''
        :notes:模糊查询表数据，获取排序后的结果
        :author：yulongyan
        :date:2021-11-09
        :param table_name:查询数据的表名
        :param table_data:模糊查询的表字段和字段值，格式为字典，例{key1:value1,key2:value2....}
        :param sortdesc:查询数据的排序字段，按照字段的逆序排序
        :return:返回模糊查询表数据的结果，返回数据类型为列表
        '''
        selectsql=""
        for key in table_data:
            selectsql=selectsql+key+" like '%"+table_data[key]+"%' AND "
        selectsql=selectsql.rstrip(' AND ')
        real_sql = "SELECT * FROM " + table_name +" WHERE " + selectsql+" ORDER BY "+sortdesc+" DESC"
        with self.conn.cursor() as cursor:
            cursor.execute(real_sql)
        self.conn.commit()
        self.close()
        return cursor.fetchall()

    # 执行sql语句
    def executesql(self,sql):
        """
        :notes:执行sql语句，并获取结果
        :author：yulongyan
        :date:2021-11-09
        :param sql:执行的sql语句
        :return:返回sql执行后返回的结果，返回数据类型为列表
        """
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
        self.conn.commit()
        self.close()
        return cursor.fetchall()

    # 关闭数据库
    def close(self):
        self.conn.close()

    # 初始化数据
    def init_data(self, datas):
        '''
        :notes:初始化表数据，先清空表数据，再在表中插入数据，无返回
        :param datas:表名和插入表的数据，格式如：{(table1:{key11:value11,key12:value12...}),(table2:{key21:value21,key22:value22...})}
        '''
        for table, data in datas.items():
            self.clear(table)
            for d in data:
                self.insert(table, d)
        self.close()



if __name__ == '__main__':
    tabledata={"name":"测试门店","status":"1"}
    result=DB().exactselect("mf_shop",tabledata,"id")
    print(result)

    # tabledata={"name":"测试"}
    # result=DB().dimselect("mf_shop",tabledata,"id")
    # print(result)

    # result = DB().executesql("select * from mf_shop limit 10")
    # print(result)


