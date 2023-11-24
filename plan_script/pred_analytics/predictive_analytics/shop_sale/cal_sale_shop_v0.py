
import pymysql
import datetime
import yaml
import lk_tools

"""
V0版本, 常规品售卖门店数-日纬度
"""


def pre_day_sale_num(wh_dept_id, commodity_id, date_val, shop_way):
    cul_datetime = datetime.datetime.strptime(date_val, '%Y-%m-%d')
    now_datetime = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    if cul_datetime >= now_datetime:
        day_num = (cul_datetime-now_datetime).days
    else:
        print("只计算大于当天的日期")
        return

    # 当天日期
    cul_date = now_datetime.strftime('%Y-%m-%d')
    date_split = cul_date.split('-')
    cul_month = date_split[1]
    cul_year = date_split[0]

    # 历史 14 天
    last_day = lk_tools.datetool.get_last_reduce_date(cul_date, 14)
    # 前一天
    yesterday = lk_tools.datetool.get_last_reduce_date(cul_date, 1)

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

    with open('../conf/predictive_sql.yml', encoding='utf-8') as f:
        yml_data = yaml.load(f, Loader=yaml.CLoader)
        mysql_sql = yml_data['cul_sale_shop']
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

    sql_increment_shop = mysql_sql['query_increment_shop']
    sql_actual_shop_num = mysql_sql['query_actual_shop_num']
    sql_sale_shop_num = mysql_sql['query_sale_shop_num']
    sql_open_shop_definite = mysql_sql['query_open_shop_definite']
    sql_open_shop_v0 = mysql_sql['query_open_shop_v0']
    sql_open_shop_detail = mysql_sql['query_open_shop_detail']

    # 历史14天【自营/联营】售卖该商品的门店数
    if shop_way == '自营':
        type_val = 10
    else:
        type_val = 20
    cursor.execute(
        sql_sale_shop_num.format(commodity_id, wh_dept_id, type_val, last_day, yesterday)
    )
    data = cursor.fetchall()
    print(data)

    # 历史14天【自营/联营】售卖该商品的门店数
    last_sale_amount = 0
    # 售卖门店数的日期
    sale_date_list = []
    for val in data:
        if val[1] is not None or val[1] != '':
            last_sale_amount += val[1]
            if val[1] > 0:
                sale_date_list.append(val[0])

    # 历史14天平均售卖门店数
    if len(sale_date_list) == 0:
        average_sale_num = 0
    else:
        average_sale_num = last_sale_amount/len(sale_date_list)

    # 扩展门店数(仓库)
    expend_num = 0
    if shop_way == '自营':
        shop_mode = 'CP01'
        shop_val = 'self_num'
    else:
        shop_mode = 'CP02'
        shop_val = 'agent_num'
    cursor.execute(
        sql_increment_shop.format(month_dict[cul_month], shop_mode, wh_dept_id, cul_year)
    )
    data = cursor.fetchall()
    print(data)
    for val in data:
        if val[0] is not None or val[0] != '':
            expend_num += val[0]

    cur_month = int(cul_month.lstrip('0'))
    # 获取上个月
    last_month_date = (now_datetime.replace(day=1) - datetime.timedelta(days=1)).strftime('%Y-%m').split('-')
    last_year = last_month_date[0]
    last_month = int(last_month_date[1].lstrip('0'))
    # 判断是否跨年
    if last_year == cul_year:
        # 判断开店计划是否存在确定版
        cursor.execute(sql_open_shop_definite.format(cul_year))
        definite_flag = cursor.fetchall()[0][0]
        if definite_flag is None or definite_flag == '':
            # 不存在确定版, 获取 v0 版本
            cursor.execute(sql_open_shop_v0.format(cul_year))
            open_shop_id = cursor.fetchall()[0][0]
        else:
            open_shop_id = definite_flag
        # 门店数（全国）-开店计划
        cursor.execute(sql_open_shop_detail.format(shop_val, open_shop_id, cur_month))
        cur_month_num = cursor.fetchall()[0][0]
        cursor.execute(sql_open_shop_detail.format(shop_val, open_shop_id, last_month))
        last_month_num = cursor.fetchall()[0][0]
    else:
        # 判断当前年开店计划是否存在确定版
        cursor.execute(sql_open_shop_definite.format(cul_year))
        definite_flag = cursor.fetchall()[0][0]
        if definite_flag is None or definite_flag == '':
            # 不存在确定版, 获取 v0 版本
            cursor.execute(sql_open_shop_v0.format(cul_year))
            cur_open_shop_id = cursor.fetchall()[0][0]
        else:
            cur_open_shop_id = definite_flag
        # 判断上一年开店计划是否存在确定版
        cursor.execute(sql_open_shop_definite.format(last_year))
        definite_flag = cursor.fetchall()[0][0]
        if definite_flag is None or definite_flag == '':
            # 不存在确定版, 获取 v0 版本
            cursor.execute(sql_open_shop_v0.format(last_year))
            last_open_shop_id = cursor.fetchall()[0][0]
        else:
            last_open_shop_id = definite_flag
        # 门店数（全国）
        cursor.execute(sql_open_shop_detail.format(shop_val, cur_open_shop_id, cur_month))
        cur_month_num = cursor.fetchall()[0][0]
        cursor.execute(sql_open_shop_detail.format(shop_val, last_open_shop_id, last_month))
        last_month_num = cursor.fetchall()[0][0]

    # 当月天数
    cur_month_day = lk_tools.datetool.get_month_days(int(cul_year), int(cul_month))
    # 门店数增量
    if wh_dept_id == '-1':
        increment_num = (cur_month_num - last_month_num) / cur_month_day
    else:
        increment_num = expend_num / cur_month_day

    # 历史14天【自营/联营】门店总数
    last_shop_total = 0
    cursor.execute(
        sql_actual_shop_num.format(shop_val, wh_dept_id, last_day, yesterday)
    )

    data = cursor.fetchall()
    print(data)
    for val in data:
        if val[0] in sale_date_list:
            last_shop_total += val[1]

    print('历史14天平均售卖门店数:', average_sale_num)
    print('门店数增量:', increment_num)
    print('历史14天售卖该商品的门店数:', last_sale_amount)
    print('历史14天门店总数', last_shop_total)
    # 【自营/联营】售卖门店数 = 历史14天平均售卖门店数 + 门店数增量 *（历史14天【自营/联营】售卖该商品的门店数 /  历史14天【自营/联营】门店总数）
    if last_shop_total == 0:
        increment_shop = 0
    else:
        increment_shop = increment_num * (float(last_sale_amount) / float(last_shop_total))
    sale_shop_num = float(average_sale_num) + float(increment_shop)
    print(cul_date, sale_shop_num)

    for num in range(day_num):
        result_num = sale_shop_num + increment_shop*(num+1)
        result_date = (now_datetime + datetime.timedelta(days=num+1)).strftime('%Y-%m-%d')
        print(result_date, result_num)


# 全国: '-1'
wh = '327193'
commodity = 5990
date = '2023-11-17'
shop = '自营'
pre_day_sale_num(wh, commodity, date, shop)
