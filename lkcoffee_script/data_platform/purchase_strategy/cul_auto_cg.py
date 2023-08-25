
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
sql_ro_ss_vlt = mysql_sql['query_ro_ss_vlt']
sql_large_class = mysql_sql['query_auto_cg_large_class']
sql_new_flag = mysql_sql['query_auto_cg_new']
sql_central_use_day = mysql_sql['query_central_use_day']


def cul_result(wh_id, goods_id, use_days):
    cursor.execute(
        sql_central_avg_increase.format(
            use_days, now_date, wh_id, goods_id
        )
    )
    # 中心仓日均调整值, 修改后影响可用天数
    central_increase = cursor.fetchall()[0][0]
    return central_increase


def get_ro_ss_vlt(wh_id, goods_id):
    cursor.execute(
        sql_ro_ss_vlt.format(
            now_date, wh_id, goods_id
        )
    )
    data = cursor.fetchall()[0]
    ro = int(data[0])
    vlt = int(data[1])
    ss = int(data[2])
    return ro, vlt, ss


def get_central_days(goods_id, wh_id):
    # 获取中心仓可用天数
    cursor.execute(
        sql_central_use_day.format(now_date, wh_id, goods_id)
    )
    sql_data = cursor.fetchall()
    if sql_data == () and sql_data is None:
        return ''
    else:
        return sql_data[0][0]


def get_large_class(goods_id):
    # 获取货物大类
    cursor.execute(
        sql_large_class.format(now_date, goods_id)
    )
    large_class_code = cursor.fetchall()[0][0]
    return large_class_code


def is_goods_new(goods_id, wh_id):
    # 判断是否新品
    cursor.execute(
        sql_new_flag.format(now_date, wh_id, goods_id)
    )
    new_flag = str(cursor.fetchall()[0][0])
    if new_flag == '0':
        return False
    else:
        return True


def cul_plan_finish_date(goods_id, wh_id, central_flag):
    large_class = get_large_class(goods_id)
    # 中心仓可用天数
    central_use_day = get_central_days(goods_id, wh_id)
    print('中心仓可用天数: {}'.format(central_use_day))
    goods_new_flag = is_goods_new(goods_id, wh_id)
    ro, vlt, ss = get_ro_ss_vlt(wh_id, goods_id)
    print('RO: {}, VLT: {}, SS: {}'.format(ro, vlt, ss))
    print('下次调拨日: {}, 下下次调拨日: {}'.format(next_transit_date, two_more_transit_date), '\n')

    if goods_new_flag:
        # 新品，则【计划完成日期】和【最晚计划完成日期】不重新计算
        pass
    else:
        # 非新品，则【计划完成日期】和【最晚计划完成日期】需要重新计算
        if central_flag == 1 and large_class == 'SC0003' and central_use_day != '':
            # 仓库为中心仓 且 货物为中心仓模式, 货物大类为"轻食"（大类编号：SC0003）
            # 【当前日】+ 中心仓可用天数 ＜【下次调拨日】，则 计划完成日期 = 当前日 + 中心仓可用天数
            result_days = lk_tools.datetool.cul_days(now_date, next_transit_date)
            print('中心仓可用天数 <', result_days)
            print('场景1:【当前日】+ 中心仓可用天数 ＜【下次调拨日】，则 计划完成日期 = 当前日 + 中心仓可用天数')
            if central_use_day < result_days:
                plan_finish_date = lk_tools.datetool.cul_date(now_date, central_use_day)
                print('计划完成日期:', plan_finish_date, '\n')
                print('最晚计划完成日期:', plan_finish_date, '\n')

            # 【下次调拨日】 ≤ 【当前日】+ 中心仓可用天数 ＜ 【下下次调拨日】，则 计划完成日期 = 当前日 + 中心仓可用天数 - RO
            use_day_left = lk_tools.datetool.cul_days(now_date, next_transit_date)
            use_day_right = lk_tools.datetool.cul_days(now_date, two_more_transit_date)
            print(use_day_left, '<= 中心仓可用天数 <', use_day_right)
            print('场景2:【下次调拨日】 ≤ 【当前日】+ 中心仓可用天数 ＜ 【下下次调拨日】，则 计划完成日期 = 当前日 + 中心仓可用天数 - RO')
            if use_day_left <= central_use_day <= use_day_right:
                plan_finish_date = lk_tools.datetool.cul_date(now_date, central_use_day - ro)
                print('计划完成日期:', plan_finish_date, '\n')
                print('最晚计划完成日期:', plan_finish_date, '\n')

            # 【下下次调拨日】 ≤ 【当前日】+ 中心仓可用天数 ＜ 【下下次调拨日】+RO+SS，则 计划完成日期 = 当前日 + VLT
            use_day_left = lk_tools.datetool.cul_days(now_date, two_more_transit_date)
            res_date = lk_tools.datetool.cul_date(two_more_transit_date, ro + ss)
            use_day_right = lk_tools.datetool.cul_days(now_date, res_date)
            print(use_day_left, '<= 中心仓可用天数 <', use_day_right)
            print('场景3:【下下次调拨日】 ≤ 【当前日】+ 中心仓可用天数 ＜ 【下下次调拨日】+RO+SS，则 计划完成日期 = 当前日 + VLT')
            if use_day_left <= central_use_day <= use_day_right:
                plan_finish_date = lk_tools.datetool.cul_date(now_date, vlt)
                print('计划完成日期:', plan_finish_date, '\n')
                print('最晚计划完成日期:', plan_finish_date, '\n')

            # 【当前日】+ 中心仓可用天数 ≥ 【下下次调拨日】+RO+SS，则 计划完成日期 = 当前日 + 中心仓可用天数 - RO - SS
            use_day = lk_tools.datetool.cul_days(now_date, res_date)
            print(use_day, '<= 中心仓可用天数')
            print('场景4:【当前日】+ 中心仓可用天数 ≥【下下次调拨日】+RO+SS，则 计划完成日期 = 当前日 + 中心仓可用天数 - RO - SS')
            if use_day <= central_use_day:
                plan_finish_date = lk_tools.datetool.cul_date(now_date, central_use_day - ro - ss)
                print('计划完成日期:', plan_finish_date, '\n')
                print('最晚计划完成日期:', plan_finish_date, '\n')
        elif central_flag == 1 and large_class != 'SC0003' and central_use_day != '':
            # 仓库为中心仓 且 货物为中心仓模式, 货物大类为非"轻食"（大类编号：SC0003）
            # 中心仓可用天数 - RO ＜ VLT 时, 计划完成日期 = 当前日 + max(7, 中心仓可用天数-RO)
            result_days = ro + vlt
            print('中心仓可用天数 <', result_days)
            print('场景1: 中心仓可用天数 - RO ＜ VLT 时, 计划完成日期 = 当前日 + max(7, 中心仓可用天数-RO)')
            if central_use_day < result_days:
                plan_finish_date = lk_tools.datetool.cul_date(now_date, max(7, central_use_day-ro))
                print('计划完成日期:', plan_finish_date, '\n')
                print('最晚计划完成日期:', plan_finish_date, '\n')

            # 中心仓可用天数 - RO ≥  VLT
            print('中心仓可用天数 >=', result_days)
            if central_use_day >= result_days:
                if large_class in ['', '', '', '', '']:
                    # "货物大类" 为器具、日耗、办公用品、工服、营销物料，则 计划完成日期 = 当前日 + VLT天数
                    plan_finish_date = lk_tools.datetool.cul_date(now_date, vlt)
                    print('计划完成日期:', plan_finish_date, '\n')
                    print('最晚计划完成日期:', plan_finish_date, '\n')
                else:
                    # 【中心仓可用天数】-RO-SS ＜ VLT，则  【计划完成日期】=当前日 +VLT天数
                    pass
        else:
            pass


if __name__ == '__main__':
    # 仓库为中心仓 且 货物为中心仓模式
    # 武汉仓库
    wh_dept_id = 22001
    # 海盐芝士厚切吐司
    good_id = 13729
    cul_plan_finish_date(good_id, wh_dept_id, 1)

    # 仓库为非中心仓 且 货物为非中心仓模式
    # 广州仓库
    wh_dept_id = 4001
    # 原味调味糖浆
    good_id = 4488
    cul_plan_finish_date(good_id, wh_dept_id, 0)
