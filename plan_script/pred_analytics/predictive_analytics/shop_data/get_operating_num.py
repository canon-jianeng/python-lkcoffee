
import os
import datetime
import yaml
import pymysql
import lk_tools

"""
杯量预测: 只取营业门店数
算法预测: 优先取售卖门店数, 若没有售卖门店数, 则取营业门店数

"""

# 获取上级目录
# upper_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
# file_path = upper_dir + '/conf/predictive_sql.yml'
file_path = '../conf/predictive_sql.yml'
with open(file_path, encoding='utf-8') as f:
    yml_data = yaml.load(f, Loader=yaml.CLoader)
    mysql_sql = yml_data['sql']
    mysql_conf = yml_data['mysql']


month_dict = {
    1: 'january_num',
    2: 'february_num',
    3: 'march_num',
    4: 'april_num',
    5: 'may_num',
    6: 'june_num',
    7: 'july_num',
    8: 'august_num',
    9: 'september_num',
    10: 'october_num',
    11: 'november_num',
    12: 'december_num'
}


# 打开数据库连接
db_cooperation = pymysql.connect(
    host=mysql_conf['cooperation']['host'],
    user=mysql_conf['cooperation']['user'],
    password=mysql_conf['cooperation']['pwd'],
    database=mysql_conf['cooperation']['db'],
    port=mysql_conf['cooperation']['port']
)

# 使用 cursor() 方法创建一个游标对象 cursor
cursor = db_cooperation.cursor()

sql_pred_shop = mysql_sql['query_pred_shop']
sql_actual_shop = mysql_sql['query_actual_shop']
sql_cp01_num = mysql_sql['query_cp01_num']
sql_cp02_num = mysql_sql['query_cp02_num']
sql_operating_rate = mysql_sql['query_operating_rate']
sql_country_shop_definite = mysql_sql['query_country_shop_definite']
sql_country_shop_v0 = mysql_sql['query_country_shop_v0']


def pred_wh_init_shop(wh_id):
    # 查询营业门店数-初始日期 (t_bi_warehouse_shop_detail 表), 作为过去日期和预测日期的初始日期计算门店数增量
    cursor.execute(sql_pred_shop.format(wh_id))
    data = cursor.fetchall()
    record_date = ''
    shop_num = 0
    # 昨天日期
    cur_date_1 = (datetime.datetime.now() - datetime.timedelta(days=1)).date()
    for value in data:
        if value[0] < cur_date_1:
            # 小于昨天的日期, 获取最近存在数据的日期
            shop_num = value[1]
            record_date = value[0]
            print(record_date, shop_num)
            break
        else:
            # 大于昨天的日期, 只获取昨天日期
            if value[0] == cur_date_1:
                shop_num = value[1]
                record_date = value[0]
                break
    return record_date, shop_num


def country_month_shop(month_int: int):
    # 营业门店数-全国纬度
    country_list = []
    cursor.execute(sql_country_shop_definite)
    country_definite = cursor.fetchall()
    if country_definite == ():
        cursor.execute(sql_country_shop_v0)
        country_v0 = cursor.fetchall()
        for country_val in country_v0:
            if month_int == country_val[0]:
                country_list = list(country_val)
                break
    else:
        for country_val in country_definite:
            if month_int == country_val[0]:
                country_list = list(country_val)
                break
    return country_list


def country_shop_increment(month_num: int):
    # 任意一个月的全国营业门店数增量
    # 查询全国营业门店数 (t_open_shop_plan 表)
    cur_list = country_month_shop(month_num)
    last_list = country_month_shop(month_num-1)
    # 全国增量门店数
    country_num = float((cur_list[2] - last_list[2]) / cur_list[1])
    # print(month_num, cur_list[2], last_list[2], cur_list[1])
    return country_num


def country_increment_total(init_str, cur_str):
    # 全国营业门店数的所有增量数
    increment_shop = 0
    init_date = lk_tools.datetool.str_to_date(init_str)
    cur_date = lk_tools.datetool.str_to_date(cur_str)
    # 判断是否相同年月
    if (init_date.year == cur_date.year
            and init_date.month == cur_date.month):
        interval_day = (cur_date - init_date).days
        increment_num = country_shop_increment(cur_date.month)
        # 初始日期到当前日期的天数 * 月增量
        increment_shop = interval_day * increment_num
    else:
        # 初始日期到初始日期的月末的天数 * 月增量
        interval_day = (lk_tools.datetool.get_month_end(init_str) - init_date).days
        increment_num = country_shop_increment(init_date.month)
        increment_shop += interval_day * increment_num
        print('月份: {}, 增量天数: {}, 每日增量数: {}'.format(
            init_date.month, interval_day, increment_num))
        # 初始日期和当前日期相差的月份，月增量 * 天数
        month_data = lk_tools.datetool.get_diff_month_num(init_str, cur_str)
        for month_val in month_data:
            increment_num = country_shop_increment(month_val['month'])
            increment_shop += month_val['days'] * increment_num
            print('月份: {}, 增量天数: {}, 每日增量数: {}'.format(
                month_val['month'], month_val['days'], increment_num))
        # 当前日期的月初到当前日期的天数 * 月增量
        interval_day = (cur_date - lk_tools.datetool.get_month_start(cur_str)).days + 1
        increment_num = country_shop_increment(cur_date.month)
        increment_shop += interval_day * increment_num
        print('月份: {}, 增量天数: {}, 每日增量数: {}'.format(
            cur_date.month, interval_day, increment_num))
    return increment_shop


def expand_month_increment(wh_id, year_int, month_int):
    # 任意一个月的拓展营业门店数增量【仓库纬度】
    # 对应月的天数
    cur_month_num = lk_tools.datetool.get_month_days(year_int, month_int)
    # 自营门店
    cursor.execute(sql_cp01_num.format(month_dict[month_int], year_int, wh_id))
    data = cursor.fetchall()
    if data is None or len(data) == 0:
        self_interval_num = 0
    else:
        self_interval_num = float(data[0][0] / cur_month_num)
    # 联营门店
    cursor.execute(sql_cp02_num.format(month_dict[month_int], year_int, wh_id))
    data = cursor.fetchall()
    if data is None or len(data) == 0:
        agent_interval_num = 0
    else:
        agent_interval_num = float(data[0][0] / cur_month_num)
    # print(self_interval_num, agent_interval_num)
    return self_interval_num + agent_interval_num


def wh_expand_increment(wh_id, init_str, cur_str):
    # 仓库纬度，取拓展计划的增量门店数
    increment_shop = 0
    init_date = lk_tools.datetool.str_to_date(init_str)
    cur_date = lk_tools.datetool.str_to_date(cur_str)
    # 判断是否相同年月
    if (init_date.year == cur_date.year
            and init_date.month == cur_date.month):
        interval_day = (cur_date - init_date).days
        increment_num = expand_month_increment(wh_id, cur_date.year, cur_date.month)
        # 初始日期到当前日期的天数 * 月增量
        increment_shop = interval_day * increment_num
        print('月份: {}, 增量天数: {}, 每日增量数: {}'.format(
                cur_date.month, interval_day, increment_num))
    else:
        # 初始日期到初始日期的月末的天数 * 月增量
        interval_day = (lk_tools.datetool.get_month_end(init_str) - init_date).days
        increment_num = expand_month_increment(wh_id, init_date.year, init_date.month)
        increment_shop += interval_day * increment_num
        print('月份: {}, 增量天数: {}, 每日增量数: {}'.format(
            init_date.month, interval_day, increment_num))
        # 初始日期和当前日期相差的月份，月增量 * 天数
        month_data = lk_tools.datetool.get_diff_month_num(init_str, cur_str)
        for month_val in month_data:
            increment_num = expand_month_increment(wh_id, month_val['year'], month_val['month'])
            increment_shop += month_val['days'] * increment_num
            print('月份: {}, 增量天数: {}, 每日增量数: {}'.format(
                month_val['month'], interval_day, increment_num))
        # 当前日期的月初到当前日期的天数 * 月增量
        interval_day = (cur_date - lk_tools.datetool.get_month_start(cur_str)).days + 1
        increment_num = expand_month_increment(wh_id, cur_date.year, cur_date.month)
        increment_shop += interval_day * increment_num
        print('月份: {}, 增量天数: {}, 每日增量数: {}'.format(
            cur_date.month, interval_day, increment_num))
    return increment_shop


def cul_wh_rate(wh_id, month_val):
    # 营业门店数-仓库纬度
    cursor.execute(sql_operating_rate.format(wh_id, month_val))
    data = cursor.fetchall()
    if data:
        rate = data[0][1]
    else:
        rate = 0
    return rate


def cul_pred_operating_shop(wh_id, date_val):
    # 营业率
    rate = country_month_shop(lk_tools.datetool.str_to_date(date_val).month)[3]

    cur_date = datetime.datetime.strptime(date_val, '%Y-%m-%d').date()
    shop_tuple = pred_wh_init_shop(wh_id)
    record_date = shop_tuple[0]
    shop_num = shop_tuple[1]

    # 预测营业门店数
    if str(wh_id) == '-1':
        # 全国纬度, 取开店计划的增量门店数
        country_increase_num = country_increment_total(
            lk_tools.datetool.date_to_str(record_date), lk_tools.datetool.date_to_str(cur_date))
        total_shop = int((float(shop_num) + country_increase_num) * float(rate))
    else:
        # 仓库纬度，取拓展计划的增量门店数
        wh_increase_num = wh_expand_increment(
            wh_id, lk_tools.datetool.date_to_str(record_date), lk_tools.datetool.date_to_str(cur_date))
        total_shop = int((float(shop_num) + wh_increase_num) * float(rate))
    print(wh_id, total_shop)
    return total_shop


if __name__ == '__main__':
    cul_pred_operating_shop('327193', '2023-11-06')
