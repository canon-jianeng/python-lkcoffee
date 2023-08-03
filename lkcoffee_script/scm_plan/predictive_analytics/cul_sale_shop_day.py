
import pymysql
import datetime
import yaml
from lkcoffee_script import lk_tools

"""
售卖门店数-日纬度 -> 周维度/月维度
"""

with open('./predictive_sql.yml', encoding='utf-8') as f:
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

sql_pred_version = mysql_sql['query_pred_sale_shop_version']
sql_pred_shop_num = mysql_sql['query_pred_sale_shop_num']
sql_sale_shop_num = mysql_sql['query_sale_shop_num']
sql_pred_wh = mysql_sql['query_pred_sale_shop_wh']


def sale_shop_actual(commodity_id, wh_dept_id, shop_way, start_day, end_day):
    # 过去数据
    cursor.execute(
        sql_sale_shop_num.format(commodity_id, wh_dept_id, shop_way, start_day, end_day)
    )
    data = cursor.fetchall()
    print(data)
    # 售卖门店数的数据
    sale_date_dict = {}
    for val in data:
        if val[1] is not None or val[1] != '':
            if val[1] > 0:
                sale_date_dict[val[0]] = val[1]
    return sale_date_dict


def sale_shop_pred(commodity_id, wh_dept_id, shop_way, start_day, end_day, version, year_val, mark_data):
    # 预测数据
    cursor.execute(
        sql_pred_version.format(version, year_val, wh_dept_id, commodity_id, mark_data)
    )
    sale_shop_id = cursor.fetchall()[0][0]
    cursor.execute(
        sql_pred_shop_num.format(sale_shop_id, shop_way, start_day, end_day)
    )
    data = cursor.fetchall()
    print(data)
    # 售卖门店数的数据
    sale_date_dict = {}
    for val in data:
        if val[1] is not None or val[1] != '':
            if val[1] > 0:
                sale_date_dict[val[0]] = val[1]
    return sale_date_dict


def sale_shop_wh_pred(commodity_id, shop_way, day_time, version, year_val, mark_data):
    # 日期对应的各个仓库纬度的数据
    cursor.execute(
        sql_pred_wh.format(version, year_val, commodity_id, mark_data)
    )
    data = cursor.fetchall()
    sale_wh_dict = {}
    if len(data) > 0:
        for val in data:
            cursor.execute(
                sql_pred_shop_num.format(val[0], shop_way, day_time, day_time)
            )
            # 售卖门店数的数据
            wh_amount = cursor.fetchall()[0][1]
            sale_wh_dict[str(val[1])] = wh_amount
    return sale_wh_dict


def cul_day_to_result(version, mark_data, commodity_id, wh_dept_id, shop_way, start_day, end_day):
    # 日纬度 -> 周维度/月纬度
    start_datetime = datetime.datetime.strptime(start_day, '%Y-%m-%d')
    end_datetime = datetime.datetime.strptime(end_day, '%Y-%m-%d')
    now_datetime = datetime.datetime.now()
    now_str = now_datetime.strftime('%Y-%m-%d')
    year_val = now_str.split('-')[0]
    yesterday = (now_datetime - datetime.timedelta(days=1)).strftime('%Y-%m-%d')

    # 【自营/联营】售卖门店数
    if shop_way == '自营':
        type_val = 10
    else:
        type_val = 20

    if mark_data == '新品':
        mark_type = 1
    else:
        mark_type = 2

    result_dict = {}
    if start_datetime >= now_datetime:
        # 这周都是预测数据
        result_dict.update(
            sale_shop_pred(commodity_id, wh_dept_id, type_val, start_day, end_day, version, year_val, mark_type)
        )
    elif end_datetime < now_datetime:
        # 这周都是过去数据
        print("不计算过去数据")
    else:
        # 一部分为过去数据
        result_dict.update(
            sale_shop_actual(commodity_id, wh_dept_id, type_val, start_day, yesterday)
        )
        # 一部分为预测数据
        result_dict.update(
            sale_shop_pred(commodity_id, wh_dept_id, type_val, now_str, end_day, version, year_val, mark_type)
        )

    date_num = len(result_dict)
    amount_total = sum(result_dict.values())
    # 周维度/月纬度-平均售卖门店数
    if date_num == 0:
        average_shop_num = 0
    else:
        average_shop_num = amount_total/date_num
    print(average_shop_num)
    return average_shop_num


def cul_wh_to_country():
    # 日纬度，仓库纬度 -> 全国纬度
    pass


def cul_country_to_wh(modify_num, version, mark_data, commodity_id, shop_way, day_time):
    # 日纬度，全国纬度 -> 仓库纬度
    now_datetime = datetime.datetime.now()
    now_str = now_datetime.strftime('%Y-%m-%d')
    year_val = now_str.split('-')[0]

    # 【自营/联营】售卖门店数
    if shop_way == '自营':
        type_val = 10
    else:
        type_val = 20

    if mark_data == '新品':
        mark_type = 1
    else:
        mark_type = 2

    # 各个仓库的售卖门店数
    result_dict = sale_shop_wh_pred(commodity_id, type_val, day_time, version, year_val, mark_type)
    print(result_dict)
    round_dict = {}
    if len(result_dict) > 0:
        if '-1' in result_dict.keys():
            country_num = result_dict.pop('-1')
        else:
            country_num = 0
        total_amount = sum(result_dict.values())
        for val, amount in result_dict.items():
            if country_num == 0:
                cul_amount = 0
            else:
                cul_amount = modify_num * (amount/country_num)
            print(val, cul_amount)
            result_dict[val] = cul_amount
            # 四舍五入
            round_dict[val] = round(cul_amount, 1)
        country_num = sum(round_dict.values())
        result_dict['-1'] = country_num
        print('-1', country_num)
    return result_dict


if __name__ == '__main__':
    modify = 140
    version_val = 1
    # 全国: '-1'
    wh = '327193'
    mark_val = '常规'
    # 商品id
    commodity = 5352
    # 预测日期
    pred_day = '2023-07-15'
    # 时间范围
    start_time = '2023-07-01'
    end_time = '2023-07-31'
    # 门店运营模式
    shop = '自营'
    # cul_day_to_result(version_val, mark_val, commodity, wh, shop, start_time, end_time)
    cul_country_to_wh(modify, version_val, mark_val, commodity, shop, pred_day)
