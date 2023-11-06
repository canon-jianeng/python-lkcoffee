import time
from datetime import date, datetime, timedelta
import pymysql
import yaml

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
{wh: {commodity: {dt, value, shop}}

           周        日
仓库 商品总和         dt
仓库 商品  dt总和     dt

"""

# predict_dt_list = ['2023-06-05', '2023-06-06', '2023-06-07', '2023-06-08', '2023-06-09', '2023-06-10', '2023-06-11']
predict_dt_list = ['2023-07-17']
commodity_id = 5990
version_val = 7
now_date = datetime.strptime(time.strftime('%Y-%m-%d', time.localtime()), '%Y-%m-%d').date()

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

sql_wh_commodity = mysql_sql['query_wh_commodity']
sql_pred_cup_commodity = mysql_sql['query_pred_cup_commodity']
sql_actual_cup_commodity = mysql_sql['query_actual_cup_commodity']
sql_pred_shop = mysql_sql['query_pred_shop']
sql_actual_shop = mysql_sql['query_actual_shop']
sql_cp01_num = mysql_sql['query_cp01_num']
sql_cp02_num = mysql_sql['query_cp02_num']
sql_country_num = mysql_sql['query_country_num']
sql_operating_rate = mysql_sql['query_operating_rate']

pred_dt_list = []

for predict_dt in predict_dt_list:
    list_pred = []
    data_wh = (('-1',), ('327193',), ('245971',), ('245871',), ('326932',), ('326327',))
    for wh in data_wh:
        if datetime.strptime(predict_dt, '%Y-%m-%d').date() < now_date:
            cursor.execute(sql_actual_cup_commodity.format(commodity_id, predict_dt, wh[0]))
            data = cursor.fetchall()
            # 查询实际（过去）商品杯量
            if data == ():
                list_pred.append([wh[0], 0, predict_dt])
            else:
                for value in data:
                    list_pred.append([wh[0], value[0], predict_dt])
        else:
            cursor.execute(sql_pred_cup_commodity.format(commodity_id, version_val, predict_dt, wh[0]))
            data = cursor.fetchall()
            # 查询预测（未来）商品杯量
            if data == ():
                list_pred.append([wh[0], 0, predict_dt])
            else:
                for value in data:
                    list_pred.append([wh[0], value[0], predict_dt])
    pred_dt_list.append(list_pred)
print(pred_dt_list)

flag_ver = 0
# 全国门店数
cursor.execute(sql_country_num)
country_data = cursor.fetchall()
if country_data:
    flag_ver = 1

pred_list = []
for pred_dt in pred_dt_list:
    shop_num = 0
    record_date = ''
    pred_dt_dict = {}
    for data1 in pred_dt:
        cur_datetime = datetime.strptime(data1[2], '%Y-%m-%d')
        cur_date = cur_datetime.date()
        # 前一天
        cur_date_1 = (cur_datetime - timedelta(days=1)).date()
        month_value = cur_date.strftime("%m")
        wh_id = data1[0]
        if data1[1]:
            pred_num = float(data1[1])
        else:
            pred_num = 0
        # 全国增量门店数
        country_num_cur = 0
        country_num_old = 0
        country_date_cur = 0
        for country_val in country_data:
            month_data = month_value.lstrip('0')
            if month_data == str(country_val[0]):
                country_num_cur = country_val[2]
                country_date_cur = country_val[1]
            if str(int(month_data) - 1) == str(country_val[0]):
                country_num_old = country_val[2]
        country_num = int((country_num_cur - country_num_old) / country_date_cur)
        # 判断日期是否小于当天，若小于当天则为过去数据
        if cur_date < now_date:
            flag = 0
            # 实际门店数
            cursor.execute(sql_actual_shop.format(wh_id))
            data = cursor.fetchall()
            # 获取最近存在数据的日期
            for value in data:
                if value[0] == cur_date:
                    flag = 1
                    shop_num = value[1]
                    record_date = value[0]
                    # print(record_date)
                    break
            if flag == 0:
                # 预测初始日期
                cursor.execute(sql_pred_shop.format(wh_id))
                data = cursor.fetchall()
                # 获取最近存在数据的日期
                for value in data:
                    if value[0] < cur_date_1:
                        shop_num = value[1]
                        record_date = value[0]
                        # print(record_date)
                        break
                    else:
                        if value[0] == cur_date_1:
                            shop_num = value[1]
                            record_date = value[0]
                            # print(record_date)
                            break
                month_key = month_dict[month_value]
                # 营业率
                year_val = cur_date.strftime("%Y")
                # 预测营业率需要找去年同期
                month_val = str(int(year_val) - 1) + '-' + month_value
                cursor.execute(sql_operating_rate.format(wh_id, month_val))
                data = cursor.fetchall()
                rate = data[0][1]
                # 自营门店
                cursor.execute(sql_cp01_num.format(month_key, year_val, wh_id))
                data = cursor.fetchall()
                if data is None or len(data) == 0:
                    self_interval_num = 0
                else:
                    self_interval_num = int(data[0][0] / 30)
                # print(self_interval_num)
                # 联营门店
                cursor.execute(sql_cp02_num.format(month_key, year_val, wh_id))
                data = cursor.fetchall()
                if data is None or len(data) == 0:
                    agent_interval_num = 0
                else:
                    agent_interval_num = int(data[0][0] / 30)
                # print(agent_interval_num)
                interval_day = (cur_date - record_date).days
                # 预测营业门店数
                if flag_ver == 1 and str(wh_id) == '-1':
                    total_shop = (shop_num + country_num * interval_day) * rate
                else:
                    total_shop = (shop_num + (self_interval_num + agent_interval_num) * interval_day) * rate
            else:
                total_shop = shop_num
            print(wh_id, cur_date, pred_num, int(total_shop))
        else:
            # 预测初始日期
            cursor.execute(sql_pred_shop.format(wh_id))
            data = cursor.fetchall()
            # 获取最近存在数据的日期
            for value in data:
                if value[0] < cur_date_1:
                    shop_num = value[1]
                    record_date = value[0]
                    # print(record_date)
                    break
                else:
                    if value[0] == cur_date_1:
                        shop_num = value[1]
                        record_date = value[0]
                        # print(record_date)
                        break
            month_key = month_dict[month_value]
            # 营业率
            year_val = cur_date.strftime("%Y")
            month_val = str(int(year_val) - 1) + '-' + month_value
            cursor.execute(sql_operating_rate.format(wh_id, month_val))
            data = cursor.fetchall()
            rate = data[0][1]
            # 自营门店
            cursor.execute(sql_cp01_num.format(month_key, year_val, wh_id))
            data = cursor.fetchall()
            if data is None or len(data) == 0:
                self_interval_num = 0
            else:
                self_interval_num = int(data[0][0]/30)
            # print(self_interval_num)
            # 联营门店
            cursor.execute(sql_cp02_num.format(month_key, year_val, wh_id))
            data = cursor.fetchall()
            if data is None or len(data) == 0:
                agent_interval_num = 0
            else:
                agent_interval_num = int(data[0][0]/30)
            # print(agent_interval_num)
            interval_day = (cur_date-record_date).days
            # 预测营业门店数
            if flag_ver == 1 and str(wh_id) == '-1':
                total_shop = (shop_num + country_num * interval_day) * rate
                # print(shop_num, country_num, interval_day)
            else:
                total_shop = (shop_num + (self_interval_num + agent_interval_num) * interval_day) * rate
                # print(shop_num, self_interval_num, agent_interval_num, interval_day)
            print(wh_id, cur_date, pred_num, int(total_shop))
        pred_dt_dict.update({wh_id: [pred_num, int(total_shop), cur_date]})
    pred_list.append(pred_dt_dict)
print(pred_list)


wh_dict = {}
for pred_val in pred_list:
    pred_num = 0
    shop_num = 0
    if pred_list.index(pred_val) == 0:
        for val in pred_val:
            val_list = pred_val[val]
            pred_num = val_list[0] * val_list[1]
            shop_num = val_list[1]
            wh_dict.update({val: [pred_num, shop_num]})
    else:
        for val in pred_val:
            val_list = pred_val[val]
            wh_list = wh_dict[val]
            pred_num = wh_list[0] + val_list[0] * val_list[1]
            shop_num = wh_list[1] + val_list[1]
            wh_dict.update({val: [pred_num, shop_num]})
print(wh_dict)

# print(wh_dict)
print('\n' + '现制饮品商品杯量预测（仓库）:')
for key_val in wh_dict:
    wh_data = wh_dict[key_val]
    if str(key_val) != '-1':
        print(str(key_val) + ":" + str(wh_data[0]/wh_data[1]))

pred_num_total = 0
shop_num_total = 0
for key_val in wh_dict:
    wh_data = wh_dict[key_val]
    if str(key_val) != '-1':
        pred_num_total += wh_data[0]
    else:
        shop_num_total += wh_data[1]
print(shop_num_total)
print('现制饮品商品杯量预测（全国）:' + str(pred_num_total/shop_num_total))
