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
        try:
            with self.conn.cursor() as cursor:
                 # 取消表的外键约束
                cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
                cursor.execute(real_sql)
            self.conn.commit()
        except Exception as e:
            print("清除{0}表报错，报错信息如下：{1}".format(table_name,e))

        # 清除表数据

    # 删除表数据
    def delete(self, table_name,where_datas):
        '''
        :notes:删除表数据，无返回
        :param table_name:更新数据的表名
        :param where_datas:查询的表字段和字段值，格式为字典，例{key1:value1,key2:value2....}
        '''
        # 按照传入的条件拼接sql语句
        real_sql = "delete  from " + table_name + ";"
        if where_datas:
            selectcondition = ''
            for key in where_datas:
                selectcondition = selectcondition + key + '=' + "'" + where_datas[key] + "'" + ' AND '
            selectcondition = selectcondition.rstrip(' AND ')
            real_sql = "delete  from " + table_name + " WHERE "+selectcondition+";"
        # 执行sql语句
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(real_sql)
            self.conn.commit()
        except Exception as e:
            print("删除{0}表报错，报错信息如下：{1}".format(table_name,e))

    # 更新表数据
    def update(self, table_name, set_data,where_datas):
        '''
        :notes:更新表数据，无返回
        :param table_name:更新数据的表名
        :param set_data:更新表字段和字段值，格式为字典，例{key1:value1,key2:value2....}
        :param where_datas:查询的表字段和字段值，格式为字典，例{key1:value1,key2:value2....}
        '''
        setcondition=''
        # 按照传入的条件拼接sql语句
        for key in set_data:
            setcondition = setcondition + key + '=' + "'" + set_data[key] + "'" + ' , '
        setcondition=setcondition.rstrip(' , ')

        searchcondition=''
        if where_datas:
            for key in where_datas:
                searchcondition =searchcondition + key + '=' + "'" + where_datas[key] + "'" + ' AND '
            searchcondition = searchcondition.rstrip(' AND ')
            real_sql = "update " + table_name + " set "+setcondition+" WHERE " + searchcondition + ";"
        else:
            real_sql = "update " + table_name + " set "+setcondition+ ";"
        # 执行sql语句
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(real_sql)
            self.conn.commit()
        except Exception as e:
            print("更新{0}表报错，报错信息如下：{1}".format(table_name,e))

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
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(real_sql)
            self.conn.commit()
        except Exception as e:
            print("新增{0}表报错，报错信息如下：{1}".format(table_name,e))

    #精确查询表数据
    def exactselect(self,table_name,select_datas,**keys):
        '''
        :notes:接口返回的字段与数据库按照查询条件查询返回数据一致
        :author：yulongyan
        :date:2021-11-23
        :param table_name:查询数据的表名
        :param selectdatas:查询的表的属性值，格式为list，例:['name','id'],查询的sql语言类似于select id,name XXX
        :param **keys可变参数
               where_datas:查询的表字段和字段值，格式为字典，例{key1:value1,key2:value2....}
               sortkeydesc:查询的表数据排序字段，按照该字段逆序排序
               limitcounts:查询的表数据返回的条数
        :return:接口返回的字段与数据库按照查询条件查询返回数据一致则返回TRUE,不一致返回FALSE
        '''
        #按照传入的查询条件拼接sql语句
        selectcondition=""
        selectparam=''
        for data in select_datas:
            selectparam = data + ',' + selectparam
        selectparam = selectparam.rstrip(' , ')
        selectsql = 'SELECT ' + selectparam + ' FROM ' + table_name
        for key in keys:
            if key=='where_datas':
                for k in keys[key]:
                    selectcondition = selectcondition + k + '=' + "'" + keys[key][k] + "'" + ' AND '

                selectcondition = selectcondition.rstrip(' AND ')
                selectsql = selectsql + ' WHERE ' + selectcondition
            if key=="sortkeydesc":
                selectsql=selectsql+' ORDER BY '+keys[key]
            if key=="limitcounts":
                selectsql=selectsql+' DESC LIMIT '+str(keys[key])

        # 执行sql语句
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(selectsql)
            self.conn.commit()
        except Exception as e:
            print("精准查询{0}表报错，报错信息如下：{1}".format(table_name,e))
        return cursor.fetchall()

    #模糊查询表数据
    def dimselect(self,table_name,select_datas,**keys):
        '''
        :notes:接口返回的字段与数据库按照查询条件查询返回数据一致
        :author：yulongyan
        :date:2021-11-23
        :param table_name:查询数据的表名
        :param selectdatas:查询的表的属性值，格式为list，例:['name','id'],查询的sql语言类似于select id,name XXX
        :param **keys可变参数
               searchdatas:查询的表字段和字段值，格式为字典，例{key1:value1,key2:value2....}
               sortkeydesc:查询的表数据排序字段，按照该字段逆序排序
               limitcounts:查询的表数据返回的条数
        :return:接口返回的字段与数据库按照查询条件查询返回数据一致则返回TRUE,不一致返回FALSE
        '''
        #按照传入的查询条件拼接sql语句
        selectcondition=""
        selectparam=''
        for data in select_datas:
            selectparam = data + ',' + selectparam
        selectparam = selectparam.rstrip(' , ')
        selectsql = 'SELECT ' + selectparam + ' FROM ' + table_name
        for key in keys:
            if key=='where_datas':
                for k in keys[key]:
                    selectcondition = selectcondition + k + ' like ' + "'%" + keys[key][k] + "%'" + ' AND '
                # for k,v in keys:
                #     selectcondition=selectcondition + k + ' like ' + "'%" + v + "%'" + ' AND '
                selectcondition = selectcondition.rstrip(' AND ')
                selectsql = selectsql + ' WHERE ' + selectcondition
            if key=="sortkeydesc":
                selectsql=selectsql+' ORDER BY '+keys[key]
            if key=="limitcounts":
                selectsql=selectsql+' DESC LIMIT '+str(keys[key])
        # 执行sql语句
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(selectsql)
            self.conn.commit()
        except Exception as e:
            print("模糊查询{0}表报错，报错信息如下：{1}".format(table_name,e))
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
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            print("执行sql语句，报错信息如下：{0}".format(e))
        return cursor.fetchall()

        # 执行sql语句

    def executevaluesql(self, sql, **key):
        """
        :notes:执行sql语句，并获取结果
        :author：zhouyu
        :date:2021-12-27
        :param sql:执行的sql语句
        :param key:sql参数  dict格式 例：{'merchant_id': 31}
        :return:返回sql执行后返回的结果，返回数据类型为列表
        """
        try:

            with self.conn.cursor() as cursor:
                cursor.execute(sql,key)
            self.conn.commit()
        except Exception as e:
            print("执行sql语句，报错信息如下：{0}".format(e))
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
                try:
                    self.insert(table, d)
                except Exception as e:
                    print("{0}表，初始化数据，报错信息如下：{1}".format(table, e))
        self.close()



    #模糊查询表数据
    def MultiQuery(self,table_name,select_datas,**keys):

        '''
        :notes:接口返回的字段与数据库按照查询条件查询返回数据一致
        :author：zhouyu
        :date:2021-12-21
        :param table_name:查询数据的表名
        :param selectdatas:查询的表的属性值，格式为list，例:['name','id'],查询的sql语言类似于select id,name XXX
        :param **keys可变参数
               searchdatas:查询的表字段和字段值，格式为字典，例{key1:value1,key2:value2....}
               sortkeydesc:查询的表数据排序字段，按照该字段降序排序
               sortkeyASC:查询的表数据排序字段，按照该字段升序排序
               limitcounts:查询的表数据返回的条数
               section: 类型dict, 取区间范围 比如创建时间 开始和结束时间范围,支持多字段取区间范围
                        例：'section':{'created_at':'1636992000,1637251199','rx_create_duration':'1,200'}
                                      created_at:取值范围字段名称
                                      '1636992000,1637251199'：范围值
               parallel：list类型，支持where条件中子句（）绑定，
                        例如'parallel': [{'phone': '王', 'user_drugs_name': '王'},{'rx_id':'1','doctor_name':'李'}]
                        转化为where 条件为 (phone like '%王%' or user_drugs_name like '%王%' ) and (rx_id like '%1%' or doctor_name like '%李%' )
        :return:接口返回的字段与数据库按照查询条件查询返回数据一致则返回TRUE,不一致返回FALSE
        '''

        #按照传入的查询条件拼接sql语句
        selectcondition=""
        selectparam=''
        for data in select_datas:
            selectparam = data + ',' + selectparam
        selectparam = selectparam.rstrip(' , ')

        selectsql = 'SELECT ' + selectparam + ' FROM ' + table_name
        for key in keys:
            if key=='where_datas':
                for k,v in keys[key].items():
                    if k=='merchant_id':
                        selectcondition=' AND '+ selectcondition + k + ' = '  + str(v) + ' AND '
                    else:
                        selectcondition =  selectcondition + k + ' like ' + "'%" + str(v) + "%'" + ' AND '
                # print(selectcondition)
                # {'where_datas': {'merchant_id': 31}, 'sortkeydesc': 'created_at'}
                selectcondition = selectcondition.rstrip(' AND ')
                selectsql = selectsql + ' WHERE 1=1 ' + selectcondition


            sectioncond=''
            if key=="section":
                 for k,v in keys[key].items():
                     v=v.split(',',1)
                     sectioncond=sectioncond +' AND '+k+' > '+ v[0] +' and '+ k +' < '+v[1]
                     # print(sectioncond)
            sectioncond = sectioncond.rstrip(' AND ')
            selectsql = selectsql + sectioncond

            strat = ''
            if key =="parallel":
                applist = []
                for k in keys['parallel']:

                    parallelcondition = ''
                    for m, n in k.items():

                        parallelcondition = parallelcondition +m+" like '%"+n+"%' or "

                    parallelcondition = parallelcondition.rstrip(' or ')
                    parallelcondition=' and ('+parallelcondition+' )'
                    applist.append(parallelcondition)


                strat=strat.join(applist)

            selectsql = selectsql + strat
            # print(selectsql)

            if key=="sortkeydesc":
                selectsql=selectsql+' ORDER BY '+keys[key] + ' desc'
            # print(selectsql)

            if key=="sortkeyASC":
                selectsql=selectsql+' ORDER BY '+keys[key] + ' asc'
            # print(selectsql)

            if key=="limitcounts":
                selectsql=selectsql+'  LIMIT '+str(keys[key])


        print('执行sql为： '+str(selectsql))


        # 执行sql语句
        try:

            with self.conn.cursor() as cursor:
                cursor.execute(selectsql)
            self.conn.commit()
        except Exception as e:
            print("模糊查询{0}表报错，报错信息如下：{1}".format(table_name,e))
        return cursor.fetchall()



# if __name__=='__main__':
#     A=DB()
    # table_name = 'mf_merchant_user_drugs'
    # select_datas = ['*']
    # aa={'merchant_id': 31}
    # re=A.MultiQuery(table_name,select_datas)
    # A.close()
    # print(re)
