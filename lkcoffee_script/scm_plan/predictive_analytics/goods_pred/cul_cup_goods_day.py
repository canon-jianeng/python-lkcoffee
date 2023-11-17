import time
from datetime import datetime
import pymysql
import yaml
from lkcoffee_script.scm_plan.predictive_analytics.conf import cup_data
import shop_operating

"""
算法-采购仓库货物预测表（常规品）: t_alg_purchase_wh_com_pred_future
算法-首采未来N天商品杯量预测表（新品）: t_alg_purchase_wh_com_pred_future
数仓-仓库门店详情表: t_bi_warehouse_shop_detail

预测版本管理表: t_version_prediction

商品杯量预测表(月): t_prediction_cup_commodity
商品杯量预测表(日): t_prediction_cup_commodity_day_detail
商品杯量预测表(周): t_prediction_cup_commodity_week_detail

商品总杯量预测表(月): t_prediction_cup_total
商品总杯量预测表(日): t_prediction_cup_total_day_detail
商品总杯量预测表(周): t_prediction_cup_total_week_detail

商品货物预测表(月): t_prediction_cup_commodity_goods
                 t_prediction_cup_commodity_goods_detail
商品货物预测表(日): t_prediction_cup_commodity_goods_day_detail
商品货物预测表(周): t_prediction_cup_commodity_goods_week_detail

货物预测表(月): t_prediction_cup_goods
              t_prediction_cup_goods_detail
货物预测表(日): t_prediction_cup_goods_day_detail
货物预测表(月): t_prediction_cup_goods_week_detail


预测分析周配置表: t_prediction_week_config
商品统计分析表(月): t_prediction_sta_commodity
商品统计分析表(日): t_prediction_sta_commodity_day_detail
商品统计分析表(周): t_prediction_sta_commodity_week_detail
商品货物统计分析表: t_prediction_sta_commodity_goods
货物统计分析: t_prediction_sta_goods
商品总杯量统计分析表: t_prediction_sta_total



商品杯量预测表(月) (历史记录): t_prediction_cup_commodity_history
商品杯量预测表(日) (历史记录): t_prediction_cup_commodity_day_history_detail
商品杯量预测表(周) (历史记录): t_prediction_cup_commodity_week_history_detail
商品总杯量预测表(月) (历史记录): t_prediction_cup_total_history
商品总杯量预测表(日) (历史记录): t_prediction_cup_total_day_history_detail
商品总杯量预测表(周) (历史记录): t_prediction_cup_total_week_history_detail
商品货物预测(月) (历史记录): t_prediction_cup_commodity_goods_history
                         t_prediction_cup_commodity_goods_history_detail
商品货物预测(日) (历史记录): t_prediction_cup_commodity_goods_day_history_detail
商品货物预测(周) (历史记录): t_prediction_cup_commodity_goods_week_history_detail
货物预测(月) (历史记录): t_prediction_cup_goods_history
                      t_prediction_cup_goods_history_detail
货物预测(日) (历史记录): t_prediction_cup_goods_day_history_detail
货物预测(周) (历史记录): t_prediction_cup_goods_week_history_detail
商品准确率分析 (历史记录): t_prediction_accuracy_commodity_history
货物准确率分析 (历史记录): t_prediction_accuracy_goods_history
商品总杯量准确率分析 (历史记录): t_prediction_accuracy_total_history
商品统计分析 (历史记录): t_prediction_sta_commodity_history
商品货物统计分析 (历史记录): t_prediction_sta_commodity_goods_history
货物统计分析 (历史记录): t_prediction_sta_goods_history
商品总杯量统计分析表 (历史记录): t_prediction_sta_total_history

"""

# 商品-货物关系
commodity_goods = {
    5352: [42, 44, 83070, 82796],
    5990: [42, 48214, 82796],
    6192: [42, 44, 83070]
}

now_date = datetime.strptime(time.strftime('%Y-%m-%d', time.localtime()), '%Y-%m-%d').date()

# 单杯用量, 查询日志关键词：【预测分析】获取商品-货物单杯用量数据成功
cup_num_dict = cup_data.cup_num_dict


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
sql_country_num = mysql_sql['query_country_num']
sql_operating_rate = mysql_sql['query_operating_rate']


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
                total_shop = shop_operating.actual_wh_shop(wh_id, dt_val)
            else:
                # 预测售卖门店数
                total_shop = shop_operating.cul_pred_operating_shop(wh_id, dt_val)

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


# predict_date_list = ['2023-06-05', '2023-06-06', '2023-06-07', '2023-06-08', '2023-06-09', '2023-06-10', '2023-06-11']
predict_date_list = ['2023-07-17', '2023-07-18', '2023-07-19', '2023-07-20', '2023-07-21', '2023-07-22', '2023-07-23']
cup_num = 35.26
commodity = 5990
version = 80

pred_list = cul_cup_commodity(commodity, version, predict_date_list)

wh_dict = {}
print('\n' + '现制饮品商品杯量预测（仓库）-周维度/月纬度:')
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
        print(commodity, wh, pred_num_total/pred_shop_total)
        pred_num_total = 0
        pred_shop_total = 0
print(wh_dict)
pred_num_total = 0
shop_num_total = 0
for date_val in wh_dict:
    for commodity in wh_dict[date_val]:
        for wh in wh_dict[date_val][commodity]:
            wh_data = wh_dict[date_val][commodity][wh]
            if wh != '-1':
                pred_num_total += wh_data[0] * wh_data[1]
            else:
                shop_num_total += wh_data[1]
        print('现制饮品商品杯量预测（全国）:', date_val, commodity, pred_num_total / shop_num_total)
        pred_num_total = 0
        shop_num_total = 0


def cul_goods_consume(version, wh_val, goods_id, predict_date_list, commodity_goods, cup_num):
    print(cup_num)
    print('\n' + '货物维度—消耗预测（新品-不含损耗）（仓库）:')
    commodity_list = []
    for commodity in commodity_goods:
        if goods_id in commodity_goods[commodity]:
            commodity_list.append(commodity)
    goods_consume_list = []
    num_total = 0
    if commodity_list:
        for date_val in predict_date_list:
            for commodity_id in commodity_list:
                pred_list = cul_cup_commodity(commodity_id, version, predict_date_list)
                pred_val_list = pred_list[wh_val][date_val][commodity_id]
                if str(wh_val) != '-1':
                    # 消耗预测（新品-不含损耗）计算
                    result = float(pred_val_list[0]) * float(cup_num) * float(pred_val_list[1])
                    num_total += result
                    print(str(commodity_id) + "+" + str(wh_val) + ":" + str(result))
                    # 商品id, 仓库id, 消耗预测（新品-不含损耗）
                    goods_consume_list.append([goods_id, wh_val, commodity_id, result])
                else:
                    pass
            # 消耗预测（新品合计-含损耗）计算
            consume_total = num_total * (1+loss_pred_rate)
            print('\n' + '货物维度—消耗预测（新品合计-含损耗）（仓库）:')
            goods_consume_list.append([goods_id, wh_val, goods_id, consume_total])
            num_total = 0
    return goods_consume_list


# 损耗率
loss_actual_rate = 0.01
loss_pred_rate = 14.8170569648


if __name__ == '__main__':
    pass
