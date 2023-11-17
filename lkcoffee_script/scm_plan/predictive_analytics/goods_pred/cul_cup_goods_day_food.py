import time
from datetime import datetime, timedelta
import pymysql
import yaml
from ..shop_data import get_sale_num

"""
商品大类: 食品

"""

# 商品-货物关
commodity_goods = {
    801: [83622],
    800: [83623]
}

now_date = datetime.strptime(time.strftime('%Y-%m-%d', time.localtime()), '%Y-%m-%d').date()


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

sql_pred_cup_commodity = mysql_sql['query_pred_cup_commodity']
sql_actual_cup_commodity = mysql_sql['query_actual_cup_commodity']


def get_cup_num(commodity_id, version_val, dt_list):
    pred_dict = {}
    for predict_dt in dt_list:
        data_wh = (('-1',), ('327193',), ('245971',), ('245871',), ('326932',), ('326327',))
        for wh in data_wh:
            if datetime.strptime(predict_dt, '%Y-%m-%d').date() < now_date:
                cursor.execute(sql_actual_cup_commodity.format(commodity_id, predict_dt, wh[0]))
                data = cursor.fetchall()
                # 查询实际（过去）商品杯量
                if data == ():
                    if wh[0] in pred_dict:
                        pred_dict[wh[0]].update({predict_dt: 0})
                    else:
                        pred_dict.update({
                            wh[0]: {predict_dt: 0}
                        })
                else:
                    for value in data:
                        if wh[0] in pred_dict:
                            pred_dict[wh[0]].update({predict_dt: value[0]})
                        else:
                            pred_dict.update({
                                wh[0]: {predict_dt: value[0]}
                            })
            else:
                cursor.execute(sql_pred_cup_commodity.format(commodity_id, version_val, predict_dt, wh[0]))
                data = cursor.fetchall()
                # 查询预测（未来）商品杯量
                if data == ():
                    if wh[0] in pred_dict:
                        pred_dict[wh[0]].update({predict_dt: 0})
                    else:
                        pred_dict.update({
                            wh[0]: {predict_dt: 0}
                        })
                else:
                    for value in data:
                        if wh[0] in pred_dict:
                            pred_dict[wh[0]].update({predict_dt: value[0]})
                        else:
                            pred_dict.update({
                                wh[0]: {predict_dt: value[0]}
                            })
    # print(pred_dict)
    return pred_dict


def cul_cup_commodity(commodity_id, version_id, predict_dt_list):
    pred_dict = get_cup_num(commodity_id, version_id, predict_dt_list)
    pred_dt_dict = {}
    for wh_id in pred_dict:
        pred_data = pred_dict[wh_id]
        for dt_val in pred_data:
            pred_num = pred_data[dt_val]
            cur_datetime = datetime.strptime(dt_val, '%Y-%m-%d').date()
            # 判断日期是否小于当天，若小于当天则为过去数据
            if cur_datetime < now_date:
                # 实际售卖门店数
                total_shop = get_sale_num.get_actual_sale_shop(wh_id, commodity_id, dt_val)
            else:
                # 预测售卖门店数
                total_shop = get_sale_num.get_pred_sale_shop(wh_id, commodity_id, dt_val)
            if wh_id in pred_dt_dict:
                if commodity_id in pred_dt_dict[wh_id]:
                    pred_dt_dict[wh_id][commodity_id].update({
                        dt_val: [pred_num, int(total_shop)]
                    })
                else:
                    pred_dt_dict[wh_id].update({
                        commodity_id: {
                            dt_val: [pred_num, int(total_shop)]
                        }
                    })
            else:
                pred_dt_dict.update({
                    wh_id: {
                        commodity_id: {
                            dt_val: [pred_num, int(total_shop)]
                        }
                    }
                })
    # print(pred_dt_dict)
    return pred_dt_dict


# predict_date_list = ['2023-07-24', '2023-07-25', '2023-07-26', '2023-07-27', '2023-07-28', '2023-07-29', '2023-07-30']
predict_date_list = ['2023-07-17', '2023-07-18', '2023-07-19', '2023-07-20', '2023-07-21', '2023-07-22', '2023-07-23']
# 单杯用量
cup_num = 1
# 预测版本id
version = 80
commodity = 801
goods_id = 83622
# 损耗率
loss_actual_rate = 0.01
loss_pred_rate = 0.025

pred_list = cul_cup_commodity(commodity, version, predict_date_list)


def cul_day_to_total(wh_val, predict_dt_list):
    # 商品预测汇总
    commodity_tuple = ((801,),)
    pred_num = 0
    shop_num = 0
    for dt_val in predict_dt_list:
        for commodity_data in commodity_tuple:
            commodity_id = commodity_data[0]
            pred_dict = cul_cup_commodity(commodity_id, version, predict_date_list)
            pred_data = pred_dict[wh_val][commodity_id][dt_val]
            pred_num += pred_data[0]*pred_data[1]
            shop_num += pred_data[1]
        if shop_num == 0:
            total_num = 0
        else:
            total_num = pred_num/shop_num
        print('商品预测汇总-仓库', dt_val, total_num)
        pred_num = 0
        shop_num = 0


def cul_day_to_result():
    wh_dict = {}
    print('\n' + '现制饮品商品杯量预测（仓库）-周纬度/月维度:')
    pred_num_total = 0
    pred_shop_total = 0
    for wh in pred_list:
        for commodity in pred_list[wh]:
            for date_val in pred_list[wh][commodity]:
                cul_data = pred_list[wh][commodity][date_val]
                pred_num_total += cul_data[0] * cul_data[1]
                pred_shop_total += cul_data[1]
                if date_val in wh_dict:
                    if commodity in wh_dict[date_val]:
                        wh_dict[date_val][commodity].update({wh: cul_data})
                    else:
                        wh_dict[date_val].update({commodity: {wh: cul_data}})
                else:
                    wh_dict.update({
                        date_val: {
                            commodity: {wh: cul_data}
                        }
                    })
            if pred_shop_total == 0:
                cul_num = 0
            else:
                cul_num = pred_num_total/pred_shop_total
            print(commodity, wh, cul_num)
            pred_num_total = 0
            pred_shop_total = 0
    print(wh_dict)
    return wh_dict


def cul_goods_consume(version, wh_val, goods_id, predict_date_list, cup_num):
    commodity_list = []
    for commodity in commodity_goods:
        if goods_id in commodity_goods[commodity]:
            commodity_list.append(commodity)
    print(commodity_list)
    goods_consume_list = []
    num_total = 0
    if commodity_list:
        for date_val in predict_date_list:
            for commodity_id in commodity_list:
                pred_dict = cul_cup_commodity(commodity_id, version, predict_date_list)
                pred_val_list = pred_dict[wh_val][commodity_id][date_val]
                # 消耗预测（新品-含损耗）计算
                result = float(pred_val_list[0]) * float(cup_num) * float(pred_val_list[1]) * (1+loss_pred_rate)
                num_total += result
                print('\n' + '货物维度—消耗预测（新品-含损耗）（仓库）:')
                print(commodity_id, wh_val, date_val, ":" + str(result))
                # 商品id, 仓库id, 消耗预测（新品-不含损耗）
                goods_consume_list.append([goods_id, wh_val, commodity_id, result])
            # 消耗预测（新品合计-含损耗）计算
            print('货物维度—消耗预测（新品合计-含损耗）（仓库）：', num_total)
            goods_consume_list.append([goods_id, wh_val, goods_id, num_total])
            num_total = 0
    return goods_consume_list


if __name__ == '__main__':
    # cul_day_to_result()
    cul_day_to_total('327193', predict_date_list)
    # cul_goods_consume(version, '327193', goods_id, predict_date_list, cup_num)
