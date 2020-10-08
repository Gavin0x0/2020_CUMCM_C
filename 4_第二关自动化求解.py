# %%
import numpy as np
import pandas as pd
import xlrd
import os


filename = "参数设定.xlsx"
filePath = os.path.join(os.getcwd(), filename)
# 第一关，第二关游戏参数相同
Game_data = pd.read_excel(
    filePath,   sheet_name='1', usecols=['player_num', 'max_load', 'init_fund', 'ddl', 'base_income', 'water_kg', 'water_price', 'water_consume', 'food_kg', 'food_price', 'food_consume', 'weather'])

player_num = Game_data.loc[0, 'player_num']
max_load = Game_data.loc[0, 'max_load']
init_fund = Game_data.loc[0, 'init_fund']
ddl = Game_data.loc[0, 'ddl']
base_income = Game_data.loc[0, 'base_income']

water_kg = Game_data.loc[0, 'water_kg']
water_price = Game_data.loc[0, 'water_price']
water_consume = []
for i in range(3):
    water_consume.append(Game_data.loc[i, 'water_consume'])
food_kg = Game_data.loc[0, 'food_kg']
food_price = Game_data.loc[0, 'food_price']
food_consume = []
for i in range(3):
    food_consume.append(Game_data.loc[i, 'food_consume'])
weather = []
for i in range(int(ddl)):
    weather.append(Game_data.loc[i, 'weather'])

todo_list = []  # 操作列表
todo_num = 0  # 操作数


# %% 游戏地图设定

def excel_to_matrix(path):
    table = xlrd.open_workbook(path).sheets()[1]  # 第一个sheet表是关卡1，第二个表是关卡2
    row = table.nrows  # 行数
    col = table.ncols  # 列数
    datamatrix = np.zeros((row, col))  # 生成一个nrows行ncols列，且元素均为0的初始矩阵
    for x in range(col):
        cols = np.matrix(table.col_values(x))  # 把list转换为矩阵进行矩阵操作
        datamatrix[:, x] = cols  # 按列把数据存进矩阵中
    # 数据归一化(跳过)
    game_map = datamatrix  # 生成一个nrows行ncols列，且元素均为0的初始矩阵，作为game_map
    for i in range(col):
        for j in range(row):
            game_map[j, i] = int(game_map[j, i])
            game_map[i, j] = game_map[j, i]
    return game_map


map_filename = "一二关地图.xlsx"
map_filePath = os.path.join(os.getcwd(), map_filename)
Game_map = excel_to_matrix(map_filePath)
'''手动设定以下参数'''
shop_site = [39, 62]  # 村庄位置
mine_site = [30, 55]  # 矿场位置
final_site = 64  # 终点位置

# %% 路径选择器
# 表格第一行和第一列是地点序号


def path_choose(game_map, local):
    path = [i+1 for i, x in enumerate(game_map[1:, local]) if x == 1]
    return path

# %% 负重计算


def count_load(water, food):
    '''计算负重(水，食物)'''
    load_total = water*water_kg+food*food_kg
    return load_total

# %% 游戏开始


today = 1  # 当前日期
local_site = 1  # 所在区域
left_fund = init_fund  # 剩余资金 = 初始资金
left_water = 0  # 剩余水量
left_food = 0  # 剩余食物


def buy_something(plus):
    '''购置物资，plus为购置物资的价格倍数'''
    # 获取全局变量
    global left_fund
    global left_water
    global left_food
    global todo_num
    water_price_now = water_price*plus
    food_price_now = food_price*plus
    load_now = count_load(left_water, left_food)
    load_left = max_load - load_now  # 最大负重 - 当前负重 = 剩余空间
    print('--------------------------------')
    print('进入商店  当前水价：'+str(water_price_now) +
          '可购买('+str(left_fund/water_price_now)+')' +
          '可装载('+str(load_left/water_kg)+')' +
          '  当前食物价：'+str(food_price_now) +
          '可购买('+str(left_fund/food_price_now)+')' +
          '可装载('+str(load_left/food_kg)+')')
    print('剩余资金为 ：'+str(left_fund))
    print('剩余水量为 ：'+str(left_water))
    print('剩余食物为 ：'+str(left_food))
    #input_str = input('输入你要购买的水和食物的数量(用空格隔开，不买则输入0):')
    input_str = todo_list[todo_num]
    print('购买的水和食物：'+str(input_str))
    todo_num += 1
    if input_str == '0':
        print('-------跳过购买-------')
    else:
        if ' ' in input_str:
            a = [int(n) for n in input_str.split(' ')]
            left_food_temp = left_fund - a[0] * \
                water_price_now-a[1]*food_price_now
            if left_food_temp < 0:
                print('资金不足，购买失败！')
                buy_something(plus)
            else:
                if count_load(a[0], a[1]) <= load_left:
                    left_water += a[0]
                    left_food += a[1]
                    left_fund = left_food_temp
                    print('-------购买成功-------')
                    print('剩余资金为 ：'+str(left_fund))
                    print('剩余水量为 ：'+str(left_water))
                    print('剩余食物为 ：'+str(left_food))
                    buy_something(plus)
                else:
                    print('背包空间不足，购买失败！')
                    buy_something(plus)
        else:
            print('输入错误，重新购买')
            buy_something(plus)


def run_mine():
    '''进行挖矿'''
    global left_fund
    global local_site
    print('-------进行挖矿-------')
    print('当前资金为:'+str(left_fund)+'+'+str(base_income) +
          '='+str(left_fund+base_income))
    left_fund += base_income


def move_site():
    '''进行移动,返回值为资源消耗倍率，移动则消耗双倍'''
    global local_site
    global todo_num
    #site_to = int(input('输入你前往的地区(不移动则输入0):'))
    site_to = todo_list[todo_num]
    print('前往：'+str(site_to))
    todo_num += 1
    if site_to == 0:
        return 1
    else:
        if site_to not in path_choose(Game_map, local_site):
            print('无法到达该地区，请重新输入')
            return move_site()
        else:
            print('从'+str(local_site)+'到达'+str(site_to))
            local_site = site_to
            return 2


def do_something():
    '''执行当天任务'''
    global todo_num
    show_now()
    if local_site in shop_site:  # 如果在村庄可以进行购买再移动
        buy_something(2)
        spend_oneday(move_site())
    elif local_site in mine_site:  # 如果在矿场可以进行挖矿或移动
        #if_mine = int(input('当前在矿场，是否挖矿(1:是 0:否):'))
        if_mine = todo_list[todo_num]
        print('是否挖矿：'+str(if_mine))
        todo_num += 1
        if if_mine:
            run_mine()
            spend_oneday(3)
        else:
            spend_oneday(move_site())
    else:
        if weather[today-1] == 2:  # 遇到沙暴无法移动
            print('第 '+str(today)+' 天有沙暴，无法移动')
            spend_oneday(1)
        else:
            spend_oneday(move_site())


def spend_oneday(plus):
    '''度过一天,plus为资源消耗的倍数'''
    global today
    global left_water
    global left_food
    a = 'null'
    if weather[today-1] == 0:
        a = '晴朗'
    elif weather[today-1] == 1:
        a = '高温'
    elif weather[today-1] == 2:
        a = '沙暴'
    print('--------------------------------')
    print('第 '+str(today)+' 天结束，天气是'+a)
    print('消耗的水量为 ：'+str(water_consume[weather[today-1]]*plus))
    print('消耗的食物为 ：'+str(food_consume[weather[today-1]]*plus))
    left_water = left_water - water_consume[weather[today-1]]*plus
    left_food = left_food - food_consume[weather[today-1]]*plus
    today += 1


def show_now():
    '''展示当前状态'''
    a = 'null'
    if weather[today-1] == 0:
        a = '晴朗'
    elif weather[today-1] == 1:
        a = '高温'
    elif weather[today-1] == 2:
        a = '沙暴'
    print('--------------------------------')
    print('当前是第 '+str(today)+' 天，天气是'+a)
    print('当前在区域 '+str(local_site))
    print('剩余资金为 ：'+str(left_fund))
    print('剩余水量为 ：'+str(left_water))
    print('剩余食物为 ：'+str(left_food))
    print('可前往：'+str(path_choose(Game_map, local_site)))


def if_dead():
    '''判断是否死亡'''
    if left_food < 0:
        return True
    elif left_water < 0:
        return True
    else:
        return False


planA = []  # 直接前往终点
planB = ['184 324', '0', 2, 10, 11, 20, 21, 29, 30, 1, 1, 0, 39,
         '250 71', '0', 47, 55, 1, 1, 1, 1, 1, 1, 1, 1, 0, 62,
         '104 115', '0', 55, 1, 1, 1, 1, 0, 63, 64]  # 当前最优解
planC = ['223 265', '0', 2, 3, 4, 5, 13, 22, 30, 0, 0, 1, 1, 1, 0, 39,
         '226 160', '0', 46, 55, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1,
         '104 115', '0', 55, 1, 1, 1, 1, 0, 63, 64]  # 尝试优化，失败
planD = ['223 265', '0', 2, 3, 4, 5, 13, 22, 30, 1, 1, 1, 1, 0, 39,
         '246 162', '0', 46, 54, 62, '15 39', '0', 55, 1, 1, 1, 1, 1, 1, 1, 1, 0, 56, 64]  # 尝试优化，非最优解


todo_list = planB
if __name__ == '__main__':
    local_site_table = []
    left_fund_table = []
    left_water_table = []
    left_food_table = []
    buy_something(1),
    for i in range(int(ddl)):
        do_something()
        local_site_table.append(local_site)
        left_fund_table.append(left_fund)
        left_water_table.append(left_water)
        left_food_table.append(left_food)
        if if_dead():
            break
        if local_site == final_site:
            break
    if local_site == final_site:
        print('走出沙漠，游戏结束')
        print('最终资产:'+str(left_fund+left_water *
                          water_price*0.5+left_food*food_price*0.5))
        print(str(local_site_table))
        print(str(left_fund_table))
        print(str(left_water_table))
        print(str(left_food_table))
    else:
        print('没能走出沙漠，游戏终止')

# %%
