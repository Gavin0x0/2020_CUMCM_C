# %%
import numpy as np
import pandas as pd
import matplotlib as mpl
from matplotlib import pyplot as plt
import os
# plot字体问题
mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['font.serif'] = ['SimHei']

filename = "参数设定.xlsx"
filePath = os.path.join(os.getcwd(), filename)
Game_data = pd.read_excel(
    filePath,   sheet_name='3', usecols=['player_num', 'max_load', 'init_fund', 'ddl', 'base_income', 'water_kg', 'water_price', 'water_consume', 'food_kg', 'food_price', 'food_consume'])

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
# 天气随机
# %%生成所有天气矩阵


def general_weather(days):
    '''输入的参数是最大天数'''
    weather_array = np.zeros((2**days, days))
    for i in range(2**days):
        a = list(map(int, list(str(bin(i))[2:days+2])))
        if len(a) < days:
            weather_array[i, days-len(a):] = a
        else:
            weather_array[i, :] = a
    return weather_array


# %% 负重计算


def count_load(water, food):
    '''计算负重(水，食物)'''
    load_total = water*water_kg+food*food_kg
    return load_total


def count_bad_moment(movedays, staydays, minedays):
    '''最差情况所需资源计算,传入(移动、停留、挖矿的天数),返回 [水，食物] 数量'''
    water_need = (movedays*4+staydays) * \
        water_consume[1]+minedays*3*water_consume[0]
    food_need = (movedays*4+staydays) * \
        food_consume[1]+minedays*3*food_consume[0]
    return [water_need, food_need]


def count_start_fund(movedays, staydays, minedays):
    '''计算最差情况下的起始资金,传入(移动、停留、挖矿的天数)'''
    water_need = (movedays*4+staydays+minedays*3)*water_consume[1]
    food_need = (movedays*4+staydays+minedays*3)*food_consume[1]
    total_fund_need = water_price*water_need+food_need*food_price
    return init_fund - total_fund_need


# %% 游戏开始


today = 1  # 当前日期
start_to_final = 3  # 起点到终点的距离
start_to_mine = 3  # 起点到矿场的距离
mine_to_final = 2  # 矿场到终点的距离
left_water = 0  # 剩余水量
left_food = 0  # 剩余食物
left_fund = init_fund  # 剩余资金


def run_mine(w):
    '''进行挖矿'''
    global left_fund
    global left_water
    global left_food
    '''print('-------进行挖矿-------')
    print('当前资金为:'+str(left_fund)+'+'+str(base_income) +
          '='+str(left_fund+base_income))'''
    left_fund += base_income/2
    left_water -= water_consume[w]*3
    left_food -= food_consume[w]*3


def move_start_final(w):
    '''进行移动[起点向终点](天气情况0/1)'''
    global start_to_final
    global left_water
    global left_food
    start_to_final -= 1
    left_water -= water_consume[w]*4
    left_food -= food_consume[w]*4


def move_start_mine_final(w):
    '''进行移动[起点路过矿场到终点](天气情况0/1)'''
    global start_to_mine
    global mine_to_final
    global left_water
    global left_food

    if start_to_mine > 0:
        start_to_mine -= 1
    else:
        mine_to_final -= 1
    left_water -= water_consume[w]*4
    left_food -= food_consume[w]*4


def stop_move(w):
    '''原地度过一天,(天气情况0/1)'''
    global left_water
    global left_food
    '''a = 'null'
    if w == 0:
        a = '晴朗'
    elif w == 1:
        a = '高温'
    print('--------------------------------')
    print('第 '+str(today)+' 天结束，天气是'+a)
    print('消耗的水量为 ：'+str(water_consume[w]))
    print('消耗的食物为 ：'+str(food_consume[w]))'''
    left_water -= water_consume[w]
    left_food -= food_consume[w]


def show_now():
    '''展示当前状态'''
    print('剩余资金为 ：'+str(left_fund))
    print('剩余水量为 ：'+str(left_water))
    print('剩余食物为 ：'+str(left_food))


def plan_1_todo(w_list):
    '''策略1：不管天气情况直接前往终点,最多需要3天'''
    global start_to_final
    global today
    global left_water
    global left_food
    global left_fund
    # 内部信息初始化
    start_to_final = 3
    today = 1
    left_water = count_bad_moment(3, 0, 0)[0]
    left_food = count_bad_moment(3, 0, 0)[1]
    left_fund = count_start_fund(3, 0, 0)
    while start_to_final > 0:
        move_start_final(w_list[today-1])
        today += 1


def plan_2_todo(w_list):
    '''策略2：第一次遇到高温就停一次，最多需要4天'''
    global start_to_final
    global today
    global left_water
    global left_food
    global left_fund
    meet_bad_days = 0  # 遭遇坏天气的次数
    # 内部信息初始化
    start_to_final = 3
    today = 1
    left_water = count_bad_moment(3, 1, 0)[0]
    left_food = count_bad_moment(3, 1, 0)[1]
    left_fund = count_start_fund(3, 1, 0)

    while start_to_final > 0:
        if meet_bad_days < 1:
            if w_list[today-1] == 1:
                stop_move(w_list[today-1])
                meet_bad_days += 1
            else:
                move_start_final(w_list[today-1])
        else:
            move_start_final(w_list[today-1])
        today += 1


def plan_3_todo(w_list, n):
    '''策略3：前n次遇到高温就停一次，最多需要n+3天【0<n<7】'''
    global start_to_final
    global today
    global left_water
    global left_food
    global left_fund
    meet_bad_days = 0  # 遭遇坏天气的次数
    # 内部信息初始化
    start_to_final = 3
    today = 1
    left_water = count_bad_moment(3, n, 0)[0]
    left_food = count_bad_moment(3, n, 0)[1]
    left_fund = count_start_fund(3, n, 0)

    while start_to_final > 0:
        if meet_bad_days < n:
            if w_list[today-1] == 1:
                stop_move(w_list[today-1])
                meet_bad_days += 1
            else:
                move_start_final(w_list[today-1])
        else:
            move_start_final(w_list[today-1])
        today += 1


def plan_4_todo(w_list):
    '''策略4：前往挖矿，前三天直接前往矿场，高温不挖矿，晴朗挖矿，剩2天时撤离'''
    global start_to_mine
    global mine_to_final
    global today
    global left_water
    global left_food
    global left_fund
    # 内部信息初始化
    start_to_mine = 3
    mine_to_final = 2
    today = 1
    left_water = count_bad_moment(5, 0, 5)[0]
    left_food = count_bad_moment(5, 0, 5)[1]
    left_fund = count_start_fund(5, 0, 5)
    while mine_to_final > 0:
        if today < 9:
            if today > 3:  # 三天后开始处于矿场
                if w_list[today-1] == 0:
                    run_mine(0)
                else:
                    stop_move(1)
            else:
                move_start_mine_final(w_list[today-1])
        else:
            move_start_mine_final(w_list[today-1])
        today += 1


if __name__ == '__main__':
    # 设置策略执行的天数
    run_days = 10

    def run_plan_1():
        every_fund_list = np.array([])
        for weather in general_weather(run_days):
            plan_1_todo(list(map(int, list(weather.tolist()))))
            final_fund = left_fund+left_water * \
                water_price*0.5+left_food*food_price*0.5
            every_fund_list = np.append(every_fund_list, final_fund)
            # print('最终资产:'+str(final_fund))
        # 求均值
        fund_mean = np.mean(every_fund_list)
        # 求方差
        fund_var = np.var(every_fund_list)
        # 求标准差
        fund_std = np.std(every_fund_list, ddof=1)
        # 最大最小值
        min_fund = np.min(every_fund_list)
        max_fund = np.max(every_fund_list)
        print('该策略的最高收益为：'+str(max_fund))
        print('该策略的最低收益为：'+str(min_fund))
        print('该策略收益指数为：'+str(fund_mean))
        print('该策略风险指数为：'+str(fund_std))
        return every_fund_list

    def run_plan_2():
        every_fund_list = np.array([])
        for weather in general_weather(run_days):
            plan_2_todo(list(map(int, list(weather.tolist()))))
            final_fund = left_fund+left_water * \
                water_price*0.5+left_food*food_price*0.5
            every_fund_list = np.append(every_fund_list, final_fund)
            # print('最终资产:'+str(final_fund))
        # 求均值
        fund_mean = np.mean(every_fund_list)
        # 求方差
        fund_var = np.var(every_fund_list)
        # 求标准差
        fund_std = np.std(every_fund_list, ddof=1)
        # 最大最小值
        min_fund = np.min(every_fund_list)
        max_fund = np.max(every_fund_list)
        print('该策略的最高收益为：'+str(max_fund))
        print('该策略的最低收益为：'+str(min_fund))
        print('该策略收益指数为：'+str(fund_mean))
        print('该策略风险指数为：'+str(fund_std))
        return every_fund_list

    def run_plan_3(n):
        every_fund_list = np.array([])
        for weather in general_weather(run_days):
            plan_3_todo(list(map(int, list(weather.tolist()))), n)
            final_fund = left_fund+left_water * \
                water_price*0.5+left_food*food_price*0.5
            every_fund_list = np.append(every_fund_list, final_fund)
            # print('最终资产:'+str(final_fund))
        # 求均值
        fund_mean = np.mean(every_fund_list)
        # 求方差
        fund_var = np.var(every_fund_list)
        # 求标准差
        fund_std = np.std(every_fund_list, ddof=1)
        # 最大最小值
        min_fund = np.min(every_fund_list)
        max_fund = np.max(every_fund_list)
        print('该策略的最高收益为：'+str(max_fund))
        print('该策略的最低收益为：'+str(min_fund))
        print('该策略收益指数为：'+str(fund_mean))
        print('该策略风险指数为：'+str(fund_std))
        return every_fund_list

    def run_plan_4():
        every_fund_list = np.array([])
        for weather in general_weather(run_days):
            plan_4_todo(list(map(int, list(weather.tolist()))))
            final_fund = left_fund+left_water * \
                water_price*0.5+left_food*food_price*0.5
            every_fund_list = np.append(every_fund_list, final_fund)
            # print('最终资产:'+str(final_fund))
        # 求均值
        fund_mean = np.mean(every_fund_list)
        # 求方差
        fund_var = np.var(every_fund_list)
        # 求标准差
        fund_std = np.std(every_fund_list, ddof=1)
        # 最大最小值
        min_fund = np.min(every_fund_list)
        max_fund = np.max(every_fund_list)
        print('该策略的最高收益为：'+str(max_fund))
        print('该策略的最低收益为：'+str(min_fund))
        print('该策略收益指数为：'+str(fund_mean))
        print('该策略风险指数为：'+str(fund_std))
        return every_fund_list
    x = np.arange(0, 2**run_days, 1)
    y_1 = run_plan_1()
    y_2 = run_plan_2()

    # plt.figure(figsize=(16, 9))  # 图像尺寸
    plt.plot(x, y_1, '.-', label='策略一')
    plt.plot(x, y_2, '.-', label='策略二')

    for i in range(2, 8):
        y = run_plan_3(i)
        plt.plot(x, y, '.-', label='策略三 n='+str(i))
    y_4 = run_plan_4()
    plt.plot(x, y_4, '.-', label='策略四')
    plt.title('策略一至策略四每种天气下的收益情况对比')
    plt.xlabel('天气情况')  # 设置横坐标轴标题
    plt.ylabel('收益情况')
    plt.legend()  # 显示图例，即每条线对应 label 中的内容
    plt.show()


# %%
