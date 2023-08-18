
import yaml
import pymysql
import math
from lkcoffee_script import lk_tools

now_time = lk_tools.datetool.get_now_time()
now_date = lk_tools.datetool.get_now_date()
now_year = now_time.year
now_month = now_time.month
now_day = now_time.day

now_month_days = lk_tools.datetool.get_month_end_date(now_year, now_month)
next_month = lk_tools.datetool.get_next_month()

# 当前日期 < 本月15号
if now_day < 15:
    # 【下次调拨日】为本月的15号
    next_transit_date = lk_tools.datetool.make_date(now_year, now_month, 15)
    # 【下下次调拨日】为本月最后一天
    two_more_transit_date = lk_tools.datetool.make_date(now_year, now_month, now_month_days)
else:
    # 【下次调拨日】为本月最后一天
    next_transit_date = lk_tools.datetool.make_date(now_year, now_month, now_month_days)
    # 【下下次调拨日】为下个月的15号
    two_more_transit_date = next_month + '-' + '15'

with open('./sql.yml', encoding='utf-8') as f:
    yml_data = yaml.load(f, Loader=yaml.CLoader)
    mysql_sql = yml_data['sql']
    mysql_conf = yml_data['mysql']

# 打开数据库连接
db_dm = pymysql.connect(
    host=mysql_conf['dataplatform']['host'],
    user=mysql_conf['dataplatform']['user'],
    password=mysql_conf['dataplatform']['pwd'],
    database=mysql_conf['dataplatform']['db'],
    port=mysql_conf['dataplatform']['port']
)

# 使用 cursor() 方法创建一个游标对象 cursor
cursor = db_dm.cursor()

sql_central_avg_increase = mysql_sql['query_central_avg_increase']


def cul_result(use_days, num):
    cursor.execute(
        sql_central_avg_increase.format(
            use_days, now_date, wh_id, goods_id
        )
    )
    # 中心仓日均调整值
    central_increase = cursor.fetchall()[0][0]
    # 计划完成日期
    plan_date = lk_tools.datetool.cul_date(now_date, num)
    return central_increase, plan_date


# 北京仓库
wh_id = 4001
# 原味调味糖浆
goods_id = 4488
RO = 4
SS = 7
VLT = 6

# （当前日+可用天数 ） ＜ 【下次调拨日】，则 计划完成日期 = 当前日 + 可用天数
use_day = lk_tools.datetool.cul_days(now_date, next_transit_date)
print('可用天数<', use_day)

print('（当前日+可用天数 ） ＜ 【下次调拨日】，则 计划完成日期 = 当前日 + 可用天数')
use_day_num = use_day-1
central_avg_increase, plan_finish_date = cul_result(use_day_num, use_day_num)
print('中心仓日均调整值:', math.floor(central_avg_increase))
print('可用天数:', use_day_num)
print('计划完成日期:', plan_finish_date, '\n')


# 【下次调拨日】 ≤ （当前日+可用天数 ）＜  【下下次调拨日】，则 计划完成日期 = 当前日 + 可用天数 - RO
use_day_left = lk_tools.datetool.cul_days(now_date, next_transit_date)
use_day_right = lk_tools.datetool.cul_days(now_date, two_more_transit_date)
print(use_day_left, '<= 可用天数 <', use_day_right)

print('【下次调拨日】 ≤ （当前日+可用天数 ）＜  【下下次调拨日】，则 计划完成日期 = 当前日 + 可用天数 - RO')
use_day_num = use_day_left
central_avg_increase, plan_finish_date = cul_result(use_day_num, use_day_num-RO)
print('中心仓日均调整值:', math.floor(central_avg_increase))
print('可用天数:', use_day_num)
print('计划完成日期:', plan_finish_date, '\n')

use_day_num = use_day_right-1
central_avg_increase, plan_finish_date = cul_result(use_day_num, use_day_num-RO)
print('中心仓日均调整值:', math.floor(central_avg_increase))
print('可用天数:', use_day_num)
print('计划完成日期:', plan_finish_date, '\n')


# 【下下次调拨日】  ≤ （当前日+可用天数 ）＜  【下下次调拨日】+RO+SS，则 计划完成日期 = 当前日 + VLT
use_day_left = lk_tools.datetool.cul_days(now_date, two_more_transit_date)
res_date = lk_tools.datetool.cul_date(two_more_transit_date, RO+SS)
use_day_right = lk_tools.datetool.cul_days(now_date, res_date)
print(use_day_left, '<= 可用天数 <', use_day_right)

print('【下下次调拨日】  ≤ （当前日+可用天数 ）＜  【下下次调拨日】+RO+SS，则 计划完成日期 = 当前日 + VLT')
use_day_num = use_day_left
central_avg_increase, plan_finish_date = cul_result(use_day_num, VLT)
print('中心仓日均调整值:', math.floor(central_avg_increase))
print('可用天数:', use_day_num)
print('计划完成日期:', plan_finish_date, '\n')

use_day_num = use_day_right - 1
central_avg_increase, plan_finish_date = cul_result(use_day_num, VLT)
print('中心仓日均调整值:', math.floor(central_avg_increase))
print('可用天数:', use_day_num)
print('计划完成日期:', plan_finish_date, '\n')


# （当前日+可用天数 ）≥【下下次调拨日】+RO+SS，则 计划完成日期 = 当前日 + 可用天数 - RO - SS
use_day = lk_tools.datetool.cul_days(now_date, res_date)
print(use_day, '<= 可用天数')

print('（当前日+可用天数 ）≥【下下次调拨日】+RO+SS，则 计划完成日期 = 当前日 + 可用天数 - RO - SS')
use_day_num = use_day
central_avg_increase, plan_finish_date = cul_result(use_day_num, use_day_num-RO-SS)
print('中心仓日均调整值:', math.floor(central_avg_increase))
print('可用天数:', use_day_num)
print('计划完成日期:', plan_finish_date, '\n')

use_day_num = use_day + 1
central_avg_increase, plan_finish_date = cul_result(use_day_num, use_day_num-RO-SS)
print('中心仓日均调整值:', math.floor(central_avg_increase))
print('可用天数:', use_day_num)
print('计划完成日期:', plan_finish_date, '\n')
