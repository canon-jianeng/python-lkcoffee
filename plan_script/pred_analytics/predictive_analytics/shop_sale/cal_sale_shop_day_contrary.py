
import pymysql
import datetime
import yaml
import lk_tools

"""

售卖门店数，周维度/月维度 -> 日纬度

"""

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

sql_pred_version = mysql_sql['query_pred_sale_shop_version']
sql_pred_shop_num = mysql_sql['query_pred_sale_shop_num']
sql_sale_shop_num = mysql_sql['query_sale_shop_num']


def sale_shop_actual(commodity_id, wh_dept_id, shop_way, start_day, end_day):
    # 过去数据
    cursor.execute(
        sql_sale_shop_num.format(commodity_id, wh_dept_id, shop_way, start_day, end_day)
    )
    data = cursor.fetchall()
    # print(data)
    # 售卖门店数的数据
    sale_date_dict = {}
    for val in data:
        if val[1] is not None or val[1] != '':
            if val[1] > 0:
                sale_date_dict[str(val[0])] = val[1]
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
    # print(data)
    # 售卖门店数的数据
    sale_date_dict = {}
    for val in data:
        if val[1] is not None or val[1] != '':
            if val[1] > 0:
                sale_date_dict[str(val[0])] = val[1]
    return sale_date_dict


def cul_result_to_day(modify_num, version, mark_data, commodity_id, wh_dept_id, shop_way, start_day, end_day):
    # 周维度/月纬度 -> 日纬度
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
    last_dict = {}
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
        last_dict.update(
            sale_shop_actual(commodity_id, wh_dept_id, type_val, start_day, yesterday)
        )
        # 一部分为预测数据
        result_dict.update(
            sale_shop_pred(commodity_id, wh_dept_id, type_val, now_str, end_day, version, year_val, mark_type)
        )
    print(last_dict)
    print(result_dict)

    if last_dict:
        last_amount = sum(last_dict.values())
    else:
        last_amount = 0

    # 该周/月售卖门店数不为0的天数【包含过去日期】
    date_num = len(last_dict) + len(result_dict)
    print('售卖门店数不为0的天数', date_num)
    # 修改后门店总数 = 修改后的周/月维度售卖门店数*该周/月售卖门店数不为0的天数【包含过去日期】-过去日期的售卖门店数
    total_num = modify_num * date_num - last_amount
    # ∑该周/月包含的日期【不包含过去日期】对应的售卖门店数
    amount_total = sum(result_dict.values())
    print('预测日期售卖门店数', amount_total)
    for val, amount in result_dict.items():
        # 日纬度-售卖门店数 = 修改后门店总数 * 比例
        if amount_total == 0:
            day_amount = 0
            rate_val = 0
        else:
            # 比例 = 该日原来的售卖门店数 / ∑该周/月包含的日期【不包含过去日期】对应的售卖门店数
            rate_val = round(amount/amount_total, 10)
            day_amount = round(total_num * rate_val, 10)
        result_dict[val] = day_amount
        print(val, day_amount, '比例', rate_val)
    return result_dict


modify_val = 300
# 版本
version_val = 2
# 全国: '-1'
wh = '327193'
mark_val = '常规'
# 商品id
commodity = 5352
# 时间范围
start_time = '2023-07-01'
end_time = '2023-07-31'
# 门店运营模式
shop = '联营'
cul_result_to_day(modify_val, version_val, mark_val, commodity, wh, shop, start_time, end_time)
