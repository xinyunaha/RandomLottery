# Version 1.0
# Created by xinyunaha on 2020-12-17 13:12
import time
import bisect
import random

a = 0
b = 0
c = 0
d = 0
e = 0
f = 0

times = 1000000
start_time = time.time()
data = {'A': 50, 'B': 30, 'C': 20, 'D': 5, 'E': 1, 'F': 0}
key_list = list(data.keys())
value_list = [data[key] for key in key_list]
for i in range(times):
    print(f'\r测试次数->{i + 1}/{times},耗时->{round(time.time() - start_time, 2)}s', end='')
    prefix_sum = []
    tmp_sum = 0
    for value in value_list:
        tmp_sum += value
        prefix_sum.append(tmp_sum)
    t = random.randint(0, tmp_sum - 1)
    pick_value = key_list[bisect.bisect_right(prefix_sum, t)]
    if pick_value == 'A':
        a += 1
    elif pick_value == 'B':
        b += 1
    elif pick_value == 'C':
        c += 1
    elif pick_value == 'D':
        d += 1
    elif pick_value == 'E':
        e += 1
    elif pick_value == 'F':
        f += 1
    else:
        print('err')

print('')
print('综合中奖率:')
all_width = 0
for i in list(data.values()):
    all_width += i
print('A ->{}%'.format(round(data['A'] / all_width * 100, 3)))
print('B ->{}%'.format(round(data['B'] / all_width * 100, 3)))
print('C ->{}%'.format(round(data['C'] / all_width * 100, 3)))
print('D ->{}%'.format(round(data['D'] / all_width * 100, 3)))
print('E ->{}%'.format(round(data['E'] / all_width * 100, 3)))
print('F ->{}%'.format(round(data['F'] / all_width * 100, 3)))
print('运行结果如下:')
print(f'A -> {a}次\t{round((a / times) * 100, 3)}%')
print(f'B -> {b}次\t{round((b / times) * 100, 3)}%')
print(f'C -> {c}次\t{round((c / times) * 100, 3)}%')
print(f'D -> {d}次\t{round((d / times) * 100, 3)}%')
print(f'E -> {e}次\t{round((e / times) * 100, 3)}%')
print(f'F -> {f}次\t{round((f / times) * 100, 3)}%')




# import pymysql
# import yaml
#
#
# def GetConfig():
#     try:
#         with open("I://Python//RandomLottery//config.yaml", 'r', encoding='utf-8') as ymlfile:
#             f = yaml.load_all(ymlfile, Loader=yaml.SafeLoader)
#             for conf in f:
#                 return conf
#     except FileNotFoundError:
#         print("未找到文件")
#         exit()
#
#
# class DatabaseHelper:
#     def __init__(self):
#         self.config = GetConfig()['Database']
#         self.client = pymysql.connect(host=str(self.config['Host']),
#                                       user=str(self.config['Username']),
#                                       password=str(self.config['Password']),
#                                       db=str(self.config['DBName']),
#                                       charset='utf8',
#                                       cursorclass=pymysql.cursors.DictCursor)
#
#
# DatabaseHelper()
