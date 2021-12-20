# -*-coding:utf-8 -*-
import os
import yaml


class Yaml:
	def read_yaml(self, yaml_path):
		"""
		:author:hanlei
		:date: 2021/12/2
		:param yaml_path:调用时传入yaml路径
		:return:返回yaml文件内容，以列表形式，用两个i嵌套在列表字典中
		"""
		file = os.path.dirname(os.path.dirname(__file__))
		file_data = os.path.abspath(file + yaml_path)
		# print(file_data)
		with open(file_data, encoding="utf-8") as f:
			value = yaml.load(f, Loader=yaml.FullLoader)
			return value

	def os_file(self,path):
		"""
		:author:hanlei
		:date: 2021/12/16
		:path: 传入文件地址
		:return:返回yaml文件内容
		"""
		file = os.path.dirname(os.path.dirname(__file__))
		file_data = os.path.abspath(file + path)
		return file_data

<<<<<<< HEAD

if __name__ == '__main__':
	# print(Yaml().read_yaml("../database/DemoAPI_1.yaml"))
	print(Yaml().os_file('/database/DemoAPI_1.yaml'))













# 实例参考，取值

# file = Yaml().os_file('../database/DemoAPI_1.yaml')
# print(file)

# file = Yaml().read_yaml('../database/DemoAPI_1.yaml')

# # 打印全部
# print(file, '\n')
#
# # 逐行打印
# print(file[0], '\n')
# print(file[1], '\n')
# print(file[2], '\n')
#
# # 取值字典值
# print("字典中的url值：%s" % file[0]['url'])
#
# # 取列表值
# print("列表中的limit值：%s" % file[2]['params'][0]['limit'])


# pytest参数化方法
# parametrize装饰器参数化
# @pytest.mark.parametrize("参数名",列表数据)
# 参数名：用来接收每一项数据，并作为测试用例的参数。
# 列表数据：一组测试数据。
# @pytest.mark.parametrize("tests", file)
# def test_01(tests):
# 	print(tests["ID"], '\n')
# 	print(tests["module"], '\n')
#
#
# test_datas = [
# 	(11, 22, 33),
# 	(22, 33, 55)
# ]
#
# datas_dict = [
# 	{"a": 1, "b": 2, "c": 3},
# 	{"a": 11, "b": 22, "c": 33},
# 	{"a": 111, "b": 222, "c": 333},
# ]
#
#
# # 方式一:直接写
# @pytest.mark.parametrize("a, b, c", [(1, 2, 3), (4, 5, 9)])
# def test_add01(a, b, c):
# 	res = a + b
# 	assert res == c
# 	print(res, '\n')
#
#
# # 方式二:参数为列表中嵌套元组
# @pytest.mark.parametrize("data", test_datas)
# def test_add02(data):
# 	res = data[0] + data[1]
# 	assert res == data[2]
# 	print(res, '\n')
#
#
# # 方式三:参数为列表中嵌套字典
# @pytest.mark.parametrize("data", datas_dict)
# def test_add03(data):
# 	res = data["a"] + data["b"]
# 	assert res == data["c"]
# 	print(res, '\n')
# 	print()
#
#
# if __name__ == '__main__':
# 	pytest.main(['-vs', 'test.py'])  # pytest.main中需要有中括号 传入列表


# unittest ddt参数化方法
# A.第一步引入装饰器@ddt   文件头部import ddt
# B.导入数据@data、里面传的参数要进行拆包,把每次的数据传到方法里case参数
# C.拆分数据@unpack、主要是把元祖和列表解析成多个参数
# D.导入外部数据@file_data
# @ddt.ddt()
# class Demo_Api(unittest.TestCase):
#
# 	@ddt.file_data(file)
# 	@ddt.unpack
# 	def test_api_01(self, **kwargs):
# 		print("输入的值为：%s" % kwargs.get("module"), '\n')
# 		print("输入的值为：%s" % kwargs.get("ID"), '\n')
#
#
# if __name__ == '__main__':
# 	unittest.main()
=======
>>>>>>> 8d59e72bc9764844e9e71ffd1125afe26e20266f
