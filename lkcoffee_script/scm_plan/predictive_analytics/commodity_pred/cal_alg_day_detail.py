
import time
from datetime import date, datetime, timedelta
import pymysql
import yaml
from lkcoffee_script import lk_tools
from ..shop_data import get_shop_num

"""
常规品：5352        wxx研发任务商品002    SP4031
货物:  42    GS00040    焦糖味糖浆-默认--杯量
    44    GS00042    玫瑰味糖浆--杯量
    83070    GS00050    咖啡豆--杯量
    82796  GS00406    16oz冰杯--用售比

新品：5990    wxx新建230112    SP4669
货物: 42    GS00040    焦糖味糖浆-默认--杯量
    48214    GS01092        xcy咖啡豆--杯量
    82796  GS00406    16oz冰杯--用售比

用售比消耗预测计算：总杯量*营业门店数*月维度用售比

仓库
南安仓库 (仓库id: 327193, WH00407), (库存单位: 8746, SU00006844)
ZJL压测仓库 (仓库id: 245971, WH00305), (库存单位: 5965, SU00004444)
乌鲁木齐A仓库 (仓库id: 245871, WH00302), (库存单位: 6477, ZZSU00004307)
xx仓库 (仓库id: 326932, WH00393), (库存单位：8633, SU00006704)
武汉仓库 (仓库id: 326327, WH00011), (库存单位: 8503, SU00000011)

算法-采购仓库货物预测表（常规品）: t_alg_purchase_wh_com_pred_future
算法-首采未来N天商品杯量预测表（新品）: t_alg_purchase_wh_com_pred_future
数仓-仓库门店详情表: t_bi_warehouse_shop_detail


日纬度 -> 周纬度
商品明细 -> 商品总量
{wh: {commodity_dt: {value, shop}}

           周        日
仓库 商品总和         dt
仓库 商品  dt总和     dt

"""


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

sql_wh_commodity = mysql_sql['query_wh_commodity']
sql_pred_cup_commodity = mysql_sql['query_pred_cup_commodity']
sql_actual_cup_commodity = mysql_sql['query_actual_cup_commodity']
sql_pred_shop = mysql_sql['query_pred_shop']
sql_actual_shop = mysql_sql['query_actual_shop']
sql_cp01_num = mysql_sql['query_cp01_num']
sql_cp02_num = mysql_sql['query_cp02_num']
sql_operating_rate = mysql_sql['query_operating_rate']


def get_actual_data(start_day, end_day):
    actual_dict = {}
    # 查询实际（过去）商品杯量
    cursor.execute(sql_actual_cup_commodity.format(start_day, end_day))
    data = cursor.fetchall()
    for val in data:
        wh = str(val[0])
        date_val = val[2]
        # 获取门店数
        shop_num = get_shop_num.actual_wh_sale_shop(wh, date_val)
        if wh in actual_dict.keys():
            commodity_date = str(val[1]) + '_' + str(date_val)
            actual_dict[wh].update({
                commodity_date: {'cup_amount': float(val[3]), 'shop_num': shop_num}
            })
        else:
            commodity_date = str(val[1]) + '_' + str(val[2])
            actual_dict.update({
                wh: {commodity_date: {'cup_amount': float(val[3]), 'shop_num': shop_num}}
            })
    print(actual_dict)
    return actual_dict


def get_pred_data(version_id, start_day, end_day):
    pred_dict = {}
    now_date = lk_tools.datetool.get_now_date()
    # 查询预测（未来）商品杯量
    cursor.execute(sql_pred_cup_commodity.format(version_id, start_day, end_day))
    data = cursor.fetchall()
    for val in data:
        wh = str(val[0])
        date_val = val[2]
        # 获取门店数
        shop_num = get_shop_num.actual_wh_sale_shop(wh, date_val)
        if wh in pred_dict.keys():
            commodity_date = str(val[1]) + '_' + str(val[2])
            pred_dict[wh].update({
                commodity_date: {'cup_amount': float(val[3])}
            })
        else:
            commodity_date = str(val[1]) + '_' + str(val[2])
            pred_dict.update({
                wh: {commodity_date: {'cup_amount': float(val[3])}}
            })
    # print(pred_dict)
    return pred_dict


def get_element_with_str(data_list, target_str):
    # 获取列表中包含某个字符串的元素
    return [item for item in data_list if target_str in item]


def cal_cup_day_total(pred_dict, day_val):
    # 计算日纬度, 预测汇总
    for wh in pred_dict:
        commodity_list = get_element_with_str(pred_dict[wh].keys(), day_val)
        for commodity in commodity_list:
            print(commodity, pred_dict[wh][commodity])


def cal_cup_week(version_id, start_day, end_day, commodity):
    now_val = lk_tools.datetool.get_now_date()
    yesterday_val = lk_tools.datetool.get_yesterday_date()
    now_date = lk_tools.datetool.str_to_date(now_val)
    start_date = lk_tools.datetool.str_to_date(start_day)
    if start_date >= now_date:
        # 周/月的日期都是未来日期
        pred_dict = get_pred_data(version_id, start_day, end_day)
    else:
        if end_day >= now_date:
            # 周/月的日期, 存在一部分是过去日期, 一部分是未来日期
            pred_dict = get_pred_data(version_id, now_date, end_day)
            actual_dict = get_actual_data(start_day, yesterday_val)
            pred_dict += actual_dict
        else:
            # 周/月的日期都是过去日期
            pred_dict = {}

    # 计算某个商品的周维度/月维度, 预测明细
    for wh in pred_dict:
        print(wh)
        commodity_list = get_element_with_str(pred_dict[wh].keys(), str(commodity))
        for commodity in commodity_list:
            print(commodity, pred_dict[wh][commodity])


if __name__ == '__main__':
    predict_dt_list = ['2023-11-06', '2023-11-07', '2023-11-08', '2023-11-09', '2023-11-10', '2023-11-11', '2023-11-12']
    commodity_id = 5990
    version_val = 244
    cal_cup_week(get_pred_data(version_val), 5990)
