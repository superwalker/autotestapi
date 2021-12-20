# -*- coding: utf-8 -*-
# @Time    : 2021/11/10 11:47
# @Author  : 余龙艳
# @Notes:调用接口后检查数据库数据断言的通用方法，包括：新增接口/更新接口/查询接口/删除接口检查数据库数据的正确性的方法
from db_fixture.mysql_db import DB
class ASSERTDB:

    # 查询数据库数据与接口返回的数据是否一致判断
    def datasassert(self, resp_value,table_name,select_datas,**keys):
        '''
        :notes: 接口返回的字段与数据库按照查询条件查询返回数据一致
        :author：yulongyan
        :date: 2021-11-23
        :param respvalue: 实际接口返回的接口，格式为字典，例{key1:value1,keyceshi2:value2....}
        :param table_name: 查询数据的表名
        :param searchdatas: 查询的表字段和字段值，格式为字典，例{key1:value1,key2:value2....}
        :param selectdatas: 查询的表的属性值，格式为list，例:['name','id'],查询的sql语言类似于select id,name XXX
        :param sortkeydesc: 查询的表数据排序字段，按照该字段逆序排序
        :param limitcounts: 查询的表数据返回的条数
        :return: 接口返回的字段与数据库按照查询条件查询返回数据一致则返回TRUE,不一致返回FALSE
        '''
        #按照传入的查询条件拼接sql语句
        db = DB();
        result = db.exactselect(table_name,select_datas,**keys)
        db.close()
        #数据库断言
        if resp_value==result:
            return True
        else:
            return False

