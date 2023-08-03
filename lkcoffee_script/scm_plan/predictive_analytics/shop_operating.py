
import datetime
import yaml
import pymysql
from lkcoffee_script import lk_tools

month_dict = {
    '01': 'january_num',
    '02': 'february_num',
    '03': 'march_num',
    '04': 'april_num',
    '05': 'may_num',
    '06': 'june_num',
    '07': 'july_num',
    '08': 'august_num',
    '09': 'september_num',
    '10': 'october_num',
    '11': 'november_num',
    '12': 'december_num'
}

with open('./predictive_sql.yml', encoding='utf-8') as f:
    yml_data = yaml.load(f, Loader=yaml.CLoader)
    mysql_sql = yml_data['sql']
    mysql_conf = yml_data['mysql']

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

sql_pred_cup_commodity = mysql_sql['query_pred_cup_commodity']
sql_actual_cup_commodity = mysql_sql['query_actual_cup_commodity']
sql_pred_shop = mysql_sql['query_pred_shop']
sql_actual_shop = mysql_sql['query_actual_shop']
sql_cp01_num = mysql_sql['query_cp01_num']
sql_cp02_num = mysql_sql['query_cp02_num']
sql_country_num = mysql_sql['query_country_num']
sql_operating_rate = mysql_sql['query_operating_rate']


def pred_wh_init_shop(wh_id, date_val):
    # 查询预测初始日期 (t_bi_warehouse_shop_detail 表)
    cursor.execute(sql_pred_shop.format(wh_id))
    data = cursor.fetchall()
    record_date = ''
    shop_num = 0
    for value in data:
        if value[0] < cur_date_1:
            # 小于昨天的日期, 获取最近存在数据的日期
            shop_num = value[1]
            record_date = value[0]
            break
        else:
            # 大于昨天的日期, 只获取昨天日期
            if value[0] == cur_date_1:
                shop_num = value[1]
                record_date = value[0]
                break
    return record_date, shop_num


def pred_country_shop(month_num: int):
    country_num_cur = 0
    country_num_last = 0
    country_date_num = 0
    # 查询全国门店数 (t_open_shop_plan 表)
    cursor.execute(sql_country_num)
    country_data = cursor.fetchall()
    # print(country_data)
    for country_val in country_data:
        if month_num == country_val[0]:
            country_num_cur = country_val[2]
            country_date_num = country_val[1]
        if (month_num - 1) == country_val[0]:
            country_num_last = country_val[2]
    # 全国增量门店数
    country_num = int((country_num_cur - country_num_last) / country_date_num)
    # print(country_num)
    return country_num


def actual_wh_shop(wh_id, date_val):
    date_tuple = date_val.split('-')
    # 实际门店数(查询过去有数据的日期，按每月增量进行计算出对应日期的数量)
    cursor.execute(sql_actual_shop.format(wh_id, date_tuple[0]))
    data = cursor.fetchall()
    if len(data) > 0:
        shop_num = data[0][1]
        date_val = data[0][0]
    else:
        shop_num = 0
    print(wh_id, shop_num)
    return shop_num


def expand_shop_increment(year_val, month_key, wh_id):
    # 对应月的天数
    cur_month_num = lk_tools.datetool.get_month_end_date(int(year_val), int(month_key))
    # 自营门店
    cursor.execute(sql_cp01_num.format(month_key, year_val, wh_id))
    data = cursor.fetchall()
    if data is None or len(data) == 0:
        self_interval_num = 0
    else:
        self_interval_num = int(data[0][0] / cur_month_num)
    # print(self_interval_num)
    # 联营门店
    cursor.execute(sql_cp02_num.format(month_key, year_val, wh_id))
    data = cursor.fetchall()
    if data is None or len(data) == 0:
        agent_interval_num = 0
    else:
        agent_interval_num = int(data[0][0] / cur_month_num)
    # print(agent_interval_num)
    return self_interval_num+agent_interval_num


def cul_pred_operating_shop(wh_id, date_val, flag_country=0):
    # 日期
    year_val = date_val.split("-")[0]
    month_value = date_val.split("-")[1]
    month_key = month_dict[month_value]
    month_val = str(int(year_val) - 1) + '-' + month_value
    # 昨天
    now_date = datetime.datetime.now()

    cur_date_1 = (now_date - datetime.timedelta(days=1)).date()
    # 营业率
    cursor.execute(sql_operating_rate.format(wh_id, month_val))
    data = cursor.fetchall()
    if data:
        rate = data[0][1]
    else:
        rate = 0

    cur_date = datetime.datetime.strptime(date_val, '%Y-%m-%d').date()
    shop_tuple = pred_wh_init_shop(wh_id)
    record_date = shop_tuple[0]
    shop_num = shop_tuple[1]
    # 判断是否同一个月
    # if cur_date
    # 初始日期到月末的天数*月增量
    # 相差几个月，月的增量*天数
    # 当前日期的月初到当前日期的天数*月增量
    # 预测日期到预测初始日期的天数
    interval_day = (cur_date - record_date).days

    increment_num = 0

    # 预测营业门店数
    if flag_country == 1 and str(wh_id) == '-1':
        country_num = pred_country_shop(int(month_value.lstrip('0')))
        total_shop = (shop_num + country_num * interval_day) * rate
    else:
        total_shop = (shop_num + increment_num * interval_day) * rate
    print(wh_id, total_shop)
    return total_shop


if __name__ == '__main__':
    pred_wh_init_shop('245871')
    pred_country_shop(7)
    actual_wh_shop('245871', '2023-07-17')
    cul_pred_operating_shop('245871', '2023-07-19')
