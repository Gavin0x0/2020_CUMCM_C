# %%
import numpy as np
import pandas as pd
import matplotlib as mpl
from matplotlib import pyplot as plt
import random
import os
from collections import Counter
# plot字体问题
mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['font.serif'] = ['SimHei']

filename = "参数设定.xlsx"
filePath = os.path.join(os.getcwd(), filename)
Game_data = pd.read_excel(
    filePath, sheet_name='4', usecols=['player_num', 'max_load', 'init_fund', 'ddl', 'base_income', 'water_kg', 'water_price', 'water_consume', 'food_kg', 'food_price', 'food_consume'])

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
# %% 按概率生成天气


def random_pick(some_list, probabilities):
    '''(输出的值，概率区间)'''
    x = random.uniform(0, 1)
    cumulative_probability = 0.0
    for item, item_probability in zip(some_list, probabilities):
        cumulative_probability += item_probability
        if x < cumulative_probability:
            break
    return item

# %%生成随机天气列表


def general_weather(days, kinds, p):
    '''输入的参数是(最大天数,生成的种类数,出现沙暴的概率【0<p<1】)'''
    weather_array = np.zeros((kinds, days))
    p2 = (1-p)/2  # 其他两种天气等概率
    for i in range(kinds):
        for j in range(days):
            weather_array[i, j] = random_pick([0, 1, 2], [p2, p2, p])

    return weather_array


# %% 负重计算


def count_load(water, food):
    '''计算负重(水，食物)'''
    load_total = water*water_kg+food*food_kg
    return load_total


def count_bad_moment(movedays, staydays, minedays):
    '''最差情况所需资源计算,传入(高温移动、沙暴停留、沙暴挖矿的天数),返回 [水，食物] 数量'''
    water_need = movedays*6 * \
        water_consume[1]+staydays*water_consume[2]+minedays*3*water_consume[2]
    food_need = movedays*6 * \
        food_consume[1]+staydays*food_consume[2]+minedays*3*food_consume[2]
    return [water_need, food_need]


def count_start_fund(movedays, staydays, minedays):
    '''计算最差情况下的起始资金,传入(移动、停留、挖矿的天数)'''
    water_need = movedays*6 * \
        water_consume[1]+staydays*water_consume[2]+minedays*3*water_consume[2]
    food_need = movedays*6 * \
        food_consume[1]+staydays*food_consume[2]+minedays*3*food_consume[2]
    total_fund_need = water_price*water_need+food_need*food_price
    return init_fund - total_fund_need


# %% 游戏参数预设


today = 1  # 当前日期
start_to_final = 8  # 起点到终点的距离
start_to_mine = 3  # 起点到矿场的距离

start_to_city = 5  # 起点到村庄的距离
city_to_mine = 2  # 村庄到矿场的距离
mine_to_final = 3  # 矿山到终点

left_water = 0  # 剩余水量
left_food = 0  # 剩余食物
left_fund = init_fund  # 剩余资金

# %% 游戏操作脚本定义


def run_mine(w):
    '''进行挖矿'''
    global left_fund
    global left_water
    global left_food
    '''print('-------进行挖矿-------')
    print('当前资金为:'+str(left_fund)+'+'+str(base_income) +
          '='+str(left_fund+base_income))'''
    left_fund += base_income/3
    left_water -= water_consume[w]*3
    left_food -= food_consume[w]*3


def move_start_final(w):
    '''进行移动[起点向终点](天气情况0/1/2)'''
    global start_to_final
    global left_water
    global left_food
    if w != 2:
        start_to_final -= 1
    left_water -= water_consume[w]*6
    left_food -= food_consume[w]*6


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
    left_water -= water_consume[w]*6
    left_food -= food_consume[w]*6


def move_start_city(w):
    '''起点到村庄(物资足够的情况)'''
    global start_to_city
    global left_water
    global left_food

    if w == 2:
        left_water -= water_consume[w]
        left_food -= food_consume[w]
    else:
        left_water -= water_consume[w]*6
        left_food -= food_consume[w]*6
        start_to_city -= 1


def move_city_mine(w):
    '''村庄到矿场(物资足够的情况)'''
    global city_to_mine
    global left_water
    global left_food

    if w == 2:
        left_water -= water_consume[w]
        left_food -= food_consume[w]
    else:
        left_water -= water_consume[w]*6
        left_food -= food_consume[w]*6
        city_to_mine -= 1


def move_mine_final(w):
    '''矿场直接离开(物资可能不够)'''
    global mine_to_final
    global left_water
    global left_food
    if w == 2:
        left_water -= water_consume[w]
        left_food -= food_consume[w]
    else:
        left_water -= water_consume[w]*6
        left_food -= food_consume[w]*6
        mine_to_final -= 1


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


def buy_something_need(n):
    '''购买缺乏的物资(用于抵御n次沙暴)'''
    global left_water
    global left_food
    global left_fund
    water_need = count_bad_moment(0, n, 0)[0]
    food_need = count_bad_moment(0, n, 0)[1]
    fund_count = (water_need*water_price+food_need*food_price)*4
    left_fund -= fund_count
    left_water += water_need
    left_food += food_need


def buy_something_must_need():
    '''补足物资，每个都补足到240'''
    global left_water
    global left_food
    global left_fund
    water_need = 240 - left_water
    food_need = 240 - left_food
    fund_count = (water_need*water_price+food_need*food_price)*4
    if left_fund < fund_count:
        # print('资金不足，不能补足物资')
        need_num = int(left_fund/(60))
        left_fund -= need_num*(water_price+food_price)*4
        left_water += need_num
        left_food += need_num

    else:
        left_fund -= fund_count
        left_water += water_need
        left_food += food_need


def if_stop_mine(w):
    '''根据当天天气决定是否应该据需挖矿'''
    global left_water
    global left_food
    water_will_left = left_water - water_consume[w]*3
    food_will_left = left_food - food_consume[w]*3
    if water_will_left < count_bad_moment(3, 2, 0)[0] or food_will_left < count_bad_moment(3, 2, 0)[1]:
        return False
    else:
        return True


def plan_1_todo(w_list):
    '''
    策略1：
    八次移动直接前往终点
    至少准备8天高温，4天沙暴的物资，中途可以购买补给
    前五天遇到n次沙暴就补抵御n次沙暴的物资
    如果前5天无沙暴，且前11天沙暴次数大于3次，玩家有可能死亡，死亡率在0.1%以下
    玩家死亡的话 收益记为0
    '''
    global left_water
    global left_food
    global left_fund
    global start_to_final
    # 内部信息初始化
    start_to_final = 8
    today = 1
    left_water = count_bad_moment(8, 4, 0)[0]
    left_food = count_bad_moment(8, 4, 0)[1]
    left_fund = count_start_fund(8, 4, 0)
    if w_list[:11].count(2) < 4:
        while start_to_final > 0:
            if left_food*left_water >= 0:
                move_start_final(w_list[today-1])
                today += 1
            else:
                start_to_final = 0
                left_food = 0
                left_fund = 0
                left_water = 0
                print(w_list)
                print('特殊情况，物资不够，人员死亡')
    elif w_list[:5].count(2) > 0:
        buy_something_need(w_list[:5].count(2))
        while start_to_final > 0:
            if left_food*left_water >= 0:
                move_start_final(w_list[today-1])
                today += 1
            else:
                start_to_final = 0
                left_food = 0
                left_fund = 0
                left_water = 0
                print(w_list)
                print('特殊情况，物资不够，人员死亡')
    else:  # 如果前5天无沙暴，且前11天沙暴次数大于3次
        '''特殊情况，人员可能死亡'''
        while start_to_final > 0:
            if left_food*left_water >= 0:
                move_start_final(w_list[today-1])
                today += 1
            else:
                start_to_final = 0
                left_food = 0
                left_fund = 0
                left_water = 0
                print(w_list)
                print('特殊情况，物资不够，人员死亡')
        # print('另需购置物料，未写完')


def plan_2_todo(w_list):
    '''
    策略2：
    起点拉满物资
    前五天直接到村庄
    买齐物资
    到矿山
    一直挖，挖到物资勉强足够离开（剩抵御两天沙暴，三天高温移动的物资
    然后直接离开
    '''
    global left_water
    global left_food
    global left_fund
    global start_to_city
    global city_to_mine
    global mine_to_final

    # 内部信息初始化
    start_to_city = 5
    city_to_mine = 2
    mine_to_final = 3
    today = 1
    left_water = 240
    left_food = 240
    left_fund = 6400
    while start_to_city > 0:
        move_start_city(w_list[today-1])
        today += 1
    buy_something_must_need()
    while city_to_mine > 0:
        move_city_mine(w_list[today-1])
        today += 1
    while if_stop_mine(w_list[today-1]):
        run_mine(w_list[today-1])
        today += 1
    while mine_to_final > 0:
        if left_food*left_water >= 0:
            move_mine_final(w_list[today-1])
            today += 1
        else:
            mine_to_final = 0
            left_food = 0
            left_fund = 0
            left_water = 0
            # print(w_list)
            # print('特殊情况，物资不够，人员死亡')


        # %% 游戏开始
if __name__ == '__main__':

    run_days = 30  # 设置策略执行的天数
    test_kinds = 50000  # 设置测试集的大小
    bad_day_p = 0.1  # 设置沙暴天气的概率

    def run_plan_1():
        every_fund_list = np.array([])
        for weather in general_weather(run_days, test_kinds, bad_day_p):
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
        Counter(every_fund_list)
        print('该策略死亡率为：'+str(sum(every_fund_list == 0)/test_kinds))

        return every_fund_list

    def run_plan_2():
        every_fund_list = np.array([])
        for weather in general_weather(run_days, test_kinds, bad_day_p):
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
        Counter(every_fund_list)
        print('该策略死亡率为：'+str(sum(every_fund_list == 0)/test_kinds))

        return every_fund_list
# %% 绘图展示
    x = np.arange(0, test_kinds, 1)
    y_1 = run_plan_1()
    y_2 = run_plan_2()
    plt.plot(x, y_1, '.', label='策略一')
    plt.plot(x, y_2, '.', label='策略二')

    plt.title('策略一和策略二随机天气下的收益情况')
    plt.xlabel('天气情况')  # 设置横坐标轴标题
    plt.ylabel('收益情况')
    plt.legend()  # 显示图例，即每条线对应 label 中的内容
    plt.show()


# %%
