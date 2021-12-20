# -*- coding: utf-8 -*-
# @Time    : 2021/11/10 11:47
# @Author  : 余龙艳
# @Notes:
from db_fixture.mysql_db import DB


class INITDB:
    #初始化数据，删除表数据
    def init_deletesql(self,table_name,where_datas):
        '''
        :notes:删除表数据
        :param table_name:清除数据的表名
        :param where_datas:查询的表字段和字段值，格式为字典，例{key1:value1,key2:value2....}
        '''
        db = DB();
        try:
            db.delete(table_name,where_datas)
        except Exception as e:
            print("初始化数据，删除{0}表数据报错，详细信息如下:{1}".format(table_name,e))
        db.close()

    # 初始化数据，更新表数据
    def init_updatesql(self,table_name, set_data,where_datas):
        '''
        :notes:更新表数据
        :param table_name:更新数据的表名
        :param set_data:更新表字段和字段值，格式为字典，例{key1:value1,key2:value2....}
        :param where_datas:查询的表字段和字段值，格式为字典，例{key1:value1,key2:value2....}
        '''
        db=DB();
        try:
            db.update(table_name,set_data,where_datas);
        except Exception as e:
            print("初始化数据，更新{0}表数据报错，详细信息如下:{1}".format(table_name, e))
        db.close()

    # 初始化数据，插入表数据
    def init_insertsql(self,datas):
        '''
        :notes:插入表数据
        :param datas:表名和插入表的数据，格式如：{(table1:{key11:value11,key12:value12...}),(table2:{key21:value21,key22:value22...})}
        '''
        db = DB();
        for table, data in datas.items():
            try:
                for d in data:
                    db.insert(table_name=table, table_data=d)
            except Exception as e:
                print("初始化数据，插入{0}表数据报错，详细信息如下:{1}".format(table, e))
        db.close()

