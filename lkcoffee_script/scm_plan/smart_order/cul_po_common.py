
import pymysql
import yaml
import datetime
from current_stock import stock_list
from transit_data import transit_data
from lkcoffee_script import lk_tools

"""
先删除数据 DELETE FROM t_po_order_strategy, 再执行定时任务 PoStrategyTask

1.计算采购数量时，所有的计算因子 都用“用料单位”计算，算出采购量后
2.再换算为“采购单位”，换算时，若有小数，向上取整

"""

with open('./sql.yml', encoding='utf-8') as f:
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

db_srm = pymysql.connect(
    host=mysql_conf['srm']['host'],
    user=mysql_conf['srm']['user'],
    password=mysql_conf['srm']['pwd'],
    database=mysql_conf['srm']['db'],
    port=mysql_conf['srm']['port']
)

# 使用 cursor() 方法创建一个游标对象 cursor
cursor = db_cooperation.cursor()
cursor_srm = db_srm.cursor()

sql_pred_consume = mysql_sql['cooperation']['query_pred_consume']
sql_ss_cnt = mysql_sql['cooperation']['query_ss_cnt']
sql_loss_amount = mysql_sql['cooperation']['query_loss_amount']
sql_wh = mysql_sql['cooperation']['query_wh']
sql_pred_definite = mysql_sql['cooperation']['query_pred_definite']
sql_pred_v0 = mysql_sql['cooperation']['query_pred_v0']
sql_pred_amount = mysql_sql['cooperation']['query_pred_amount']
sql_day_consume = mysql_sql['cooperation']['query_day_consume']
sql_vlt = mysql_sql['cooperation']['query_vlt']
sql_spec_wh = mysql_sql['cooperation']['query_spec']
sql_purchase_ratio = mysql_sql['cooperation']['query_purchase_ratio']
sql_national_price = mysql_sql['srm']['query_national_price']


def get_date_range(num: int, finish_flag=0):
    # 获取T日, T+num月最后一天的日期
    now_val = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
    year_num = int(now_val.split('-')[0])
    month_num = int(now_val.split('-')[1].lstrip('0')) + num
    if month_num > 12:
        year_num += 1
        month_num = month_num - 12
    if month_num < 10:
        month_val = '0' + str(month_num)
    else:
        month_val = str(month_num)
    if finish_flag == 1 and num == 2:
        # +2计划完成日期
        date_val = str(year_num) + '-' + month_val + '-' + str(15)
    else:
        day_num = lk_tools.datetool.get_month_end_date(year_num, month_num)
        date_val = str(year_num) + '-' + month_val + '-' + str(day_num)
    return now_val, date_val


def cul_sum_num(data):
    # 返回不为空的数据
    if data != () and data is not None:
        num = data[0][0]
        if num != () and num is not None:
            return float(num)
    return 0


def cul_pred_consume(goods_id, wh_range, start_date, end_date):
    # T日至T+n月最后一天的算法预估需求量
    pred_total = 0
    get_dict = {}
    cursor.execute(
        sql_pred_consume.format(
            goods_id, wh_range, start_date, end_date
        )
    )
    sql_data = cursor.fetchall()
    if sql_data != () and sql_data is not None:
        for data_val in sql_data:
            pred_num = round(float(data_val[1]), 15)
            get_dict.update({data_val[0]: pred_num})
            pred_total += pred_num
    return pred_total


def cul_ss_cnt(increment_num, goods_id, wh_range):
    # SS1
    get_dict = {}
    ss_total = 0
    cursor.execute(
        sql_ss_cnt.format(
            "ss_cnt_t" + str(increment_num), goods_id, wh_range
        )
    )
    sql_data = cursor.fetchall()
    if sql_data != () and sql_data is not None:
        for data_val in sql_data:
            ss_num = round(float(data_val[1]), 15)
            get_dict.update({data_val[0]: ss_num})
            ss_total += ss_num
    return ss_total, get_dict


def cul_loss_amount(goods_id, wh_range, start_date, end_date):
    # 预计损耗
    get_dict = {}
    loss_total = 0
    cursor.execute(
        sql_loss_amount.format(
            goods_id, wh_range, start_date, end_date
        )
    )
    sql_data = cursor.fetchall()
    if sql_data != () and sql_data is not None:
        for data_val in sql_data:
            loss_num = round(float(data_val[1]), 15)
            get_dict.update({data_val[0]: loss_num})
            loss_total += loss_num
    return loss_total, get_dict


def cul_transit_amount(spec_id, national_flag, wh_list, increment_num):
    # 日志关键词:【智慧订单】获取汇总在途成功
    # 数仓取值: 在途CG、在途FH、在途调拨, 全国取各仓库总和
    # 数仓取值: 在途PO、在途PP, 全国取'-1'
    if national_flag == 1:
        wh_val = '-1'
    else:
        wh_val = str(wh_list[0])
    if increment_num == 1:
        purchase_val = '+1'
    else:
        purchase_val = '+2'
    # 在途CG(type=2)
    cg_amount = transit_data[purchase_val][str(spec_id)]['transit_type_2']
    # 在途FH(type=3)
    fh_amount = transit_data[purchase_val][str(spec_id)]['transit_type_3']
    # 在途调拨(type=4)
    trs_amount = transit_data[purchase_val][str(spec_id)]['transit_type_4']
    # 在途PO(type=1)
    po_amount = transit_data[purchase_val][str(spec_id)]['transit_type_1']
    # 在途PP(type=0)
    pp_amount = transit_data[purchase_val][str(spec_id)]['transit_type_0']
    return pp_amount, po_amount, cg_amount, fh_amount, trs_amount


def cul_current_stock(spec_id, wh_list):
    # 日志关键词:【智慧订单】获取实时库存
    # 数仓取值: 当前库存
    get_dict = {}
    stock_total = 0
    for data_dict in stock_list:
        if str(data_dict['specId']) == spec_id and data_dict['whDeptId'] in wh_list:
            get_dict.update({data_dict['whDeptId']: data_dict['totalNum']})
            stock_total += data_dict['totalNum']
    return stock_total, get_dict


def cul_pred_data(adjust_flag, goods_id, wh_id, mark_type, type_val, start_date, end_date):
    """
    :param adjust_flag: 消耗预测: 0, 调整后消耗预测: 1
    :param goods_id: 货物id
    :param wh_id: 仓库id范围
    :param mark_type: 标记类型，1:新品, 2:常规
    :param type_val: 分类 18:杯量消耗预测, 19:常规消耗预测
    :param start_date: 当前日期
    :param end_date: T+n月最后一天日期, n为1或者2
    :return
    """
    year_val = start_date.split('-')[0]
    if adjust_flag == 0:
        # 消耗预测, 取当前年算法预测V0版本
        cursor.execute(
            sql_pred_v0.format(
                year_val, goods_id, wh_id
            )
        )
        sql_data = cursor.fetchall()
        if sql_data != () and sql_data is not None:
            cup_goods_id = sql_data[0][0]
        else:
            cup_goods_id = ''
    else:
        # 调整后消耗预测, 取算法预测【确定版】
        cursor.execute(
            sql_pred_definite.format(
                year_val, goods_id, wh_id
            )
        )
        sql_data = cursor.fetchall()
        if sql_data != () and sql_data is not None:
            cup_goods_id = sql_data[0][0]
        else:
            cup_goods_id = ''
        if cup_goods_id == '':
            # 消耗预测, 取当前年算法预测V0版本
            cursor.execute(
                sql_pred_v0.format(
                    year_val, goods_id, wh_id
                )
            )
            sql_data = cursor.fetchall()
            if sql_data != () and sql_data is not None:
                cup_goods_id = sql_data[0][0]
            else:
                cup_goods_id = ''

    # 查询预测数据
    pred_total = 0
    if cup_goods_id != '':
        cursor.execute(
            sql_pred_amount.format(
                cup_goods_id, mark_type, type_val, start_date, end_date
            )
        )
        sql_data = cursor.fetchall()
        for data_val in sql_data:
            if data_val[0] is None:
                pred_num = 0
            else:
                pred_num = round(float(data_val[0]), 15)
            pred_total += pred_num
    return pred_total


def cul_pred_data_total(adjust_flag, goods_id, wh_list, mark_type, type_val, start_date, end_date):
    pred_total = 0
    for wh in wh_list:
        pred_total += cul_pred_data(adjust_flag, goods_id, wh, mark_type, type_val, start_date, end_date)
    return pred_total


def cul_day_consume(goods_id, wh_range):
    # T-1, T-2, T-3, T-4周日均消耗
    day_total1, day_total2, day_total3, day_total4 = 0, 0, 0, 0
    cursor.execute(
        sql_day_consume.format(
            goods_id, wh_range
        )
    )
    sql_data = cursor.fetchall()
    if sql_data != () and sql_data is not None:
        for data_val in sql_data:
            pred_num1 = round(float(data_val[0]), 15)
            day_total1 += pred_num1
            pred_num2 = round(float(data_val[1]), 15)
            day_total2 += pred_num2
            pred_num3 = round(float(data_val[2]), 15)
            day_total3 += pred_num3
            pred_num4 = round(float(data_val[3]), 15)
            day_total4 += pred_num4
    return day_total1, day_total2, day_total3, day_total4


def cul_end_order_day(goods_id, increment_num):
    date_list = get_date_range(increment_num, 1)
    # 当天日期
    now_date = datetime.datetime.strptime(date_list[0], '%Y-%m-%d')
    # 计划完成日期
    finish_plan_date = datetime.datetime.strptime(date_list[1], '%Y-%m-%d')
    print('+{}计划完成日期'.format(increment_num), date_list[1])
    po_vlt = 0
    cursor.execute(
        sql_vlt.format(goods_id)
    )
    sql_data = cursor.fetchall()
    if sql_data != () and sql_data is not None:
        po_vlt = sql_data[0][0]
    # 计划完成日期 - 当前日期 < vlt, "是否紧急PO"为是
    days = (finish_plan_date - now_date).days
    if days < po_vlt:
        print("是否紧急PO{}: 是".format(increment_num), days, po_vlt)
    else:
        print("是否紧急PO{}: 否".format(increment_num), days, po_vlt)
    # PO最晚下单日 = 计划完成日期 - po_vlt
    end_order_date = finish_plan_date - datetime.timedelta(days=po_vlt)
    print("PO{}最晚下单日".format(increment_num), end_order_date, '\n')


def get_national_flag(goods_id):
    # 仓库：全国所有“已完善”，且非“已停业”的城市仓
    wh_list = []
    cursor.execute(
        sql_wh
    )
    wh_data = cursor.fetchall()
    for val in wh_data:
        wh_list.append(val[0])
    wh_range = str(wh_list).replace('[', '(').replace(']', ')')
    # 获取货物规格和供应商id
    cursor.execute(
        sql_spec_wh.format(goods_id, wh_range)
    )
    spec_data = cursor.fetchall()
    spec_dict = {}
    for data_val in spec_data:
        spec_supplier = str(data_val[0]) + '_' + str(data_val[1])
        if spec_supplier in spec_dict:
            spec_dict[spec_supplier].append(data_val[2])
        else:
            spec_dict.update({spec_supplier: [data_val[2]]})
    print(spec_dict, '\n')
    # 判断是否全国PO
    for spec_supplier in spec_dict.keys():
        spec_val = spec_supplier.split('_')
        spec_id = spec_val[0]
        supplier_id = spec_val[1]
        wh_list = spec_dict[spec_supplier]
        # 查询用料单位换算采购单位
        cursor.execute(
            sql_purchase_ratio.format(spec_id)
        )
        purchase_data = cursor.fetchall()
        purchase_ratio = float(purchase_data[0][0]) * float(purchase_data[0][1])
        print('用料单位换算采购单位', purchase_ratio)
        # 查询报价单
        cursor_srm.execute(
            sql_national_price.format(spec_id, supplier_id)
        )
        price_data = cursor_srm.fetchall()
        if price_data != () and price_data is not None:
            price_new = price_data[0]
            # 报价城市为全国(-1), 且"是否全国同一价"为"是"
            if str(price_new[0]) == '-1' and str(price_new[1]) == '1':
                print(
                    '全国PO为"是"', '规格id:{}'.format(spec_id), '供应商id:{}'.format(supplier_id),
                    '仓库列表:{}'.format(wh_list), '\n'
                )
                cul_purchase_amount(goods_id, spec_id, purchase_ratio, wh_list, 1)
            else:
                print(
                    '全国PO为"否"', '规格id:{}'.format(spec_id), '供应商id:{}'.format(supplier_id),
                    '仓库列表:{}'.format(wh_list), '\n'
                )
                cul_purchase_amount(goods_id, spec_id, purchase_ratio, wh_list, 0)
        else:
            print(
                '全国PO为"否"', '规格id:{}'.format(spec_id), '供应商id:{}'.format(supplier_id),
                '仓库列表:{}'.format(wh_list), '\n'
            )
            cul_purchase_amount(goods_id, spec_id, purchase_ratio, wh_list, 0)


def cul_purchase_amount(goods_id, spec_id, purchase_ratio, wh_list, national_flag, increment_num=2):
    """
    :param goods_id: 货物id
    :param spec_id: 货物规格id
    :param purchase_ratio: 用料采购单位换算
    :param national_flag: 全国PO, 是-1, 否-0
    :param wh_list: 仓库列表
    :param increment_num: T+n月, n为1或者2
    :return
    """
    wh_range = str(wh_list).replace('[', '(').replace(']', ')')

    if increment_num == 1:
        # 获取T日, T+0月最后一天
        date_list = get_date_range(0)
        print(date_list)
        pred_consume = cul_pred_consume(goods_id, wh_range, date_list[0], date_list[1])
        print('T日至T+0月底的算法预估需求量', pred_consume)
        print('+0周期需求量(采购单位)', pred_consume/purchase_ratio, '\n')
        # T-1, T-2, T-3, T-4周日均消耗
        day_consume = cul_day_consume(goods_id, wh_range)
        print('T-1周日均消耗(采购单位)', round(day_consume[0] / purchase_ratio, 5))
        print('T-2周日均消耗(采购单位)', round(day_consume[1] / purchase_ratio, 5))
        print('T-3周日均消耗(采购单位)', round(day_consume[2] / purchase_ratio, 5))
        print('T-4周日均消耗(采购单位)', round(day_consume[3] / purchase_ratio, 5), '\n')

    # 获取T日, T+1月最后一天或者T+2月最后一天
    date_list = get_date_range(increment_num)
    start_date = date_list[0]
    end_date = date_list[1]
    pred_consume = cul_pred_consume(goods_id, wh_range, start_date, end_date)
    ss_cnt = cul_ss_cnt(increment_num, goods_id, wh_range)
    loss_amount = cul_loss_amount(goods_id, wh_range, start_date, end_date)
    transit_list = cul_transit_amount(spec_id, national_flag, wh_list, increment_num)
    transit_total = transit_list[0] + transit_list[1] + transit_list[2] + transit_list[3] + transit_list[4]
    transit_amount1 = transit_list[2] + transit_list[3] + transit_list[4]
    current_stock = cul_current_stock(spec_id, wh_list)

    purchase_num, purchase_ratio_num = 0, 0
    if increment_num == 1:
        # +1采购量 = T日至T+1月底的算法预估需求量 + SS1 + 预计损耗1 - 当前库存 - (在途CG/FH1 + 在途调拨1 + 在途PO1 + 在途PP1)
        purchase_num = pred_consume + ss_cnt[0] + loss_amount[0] - current_stock[0] - transit_total
        purchase_ratio_num = purchase_num / purchase_ratio
        print('+1采购量 = T日至T+1月底的算法预估需求量 + SS1 + 预计损耗1 - 当前库存 - (在途CG/FH1 + 在途调拨1 + 在途PO1 + 在途PP1)')
        # print('+{}采购量(用料单位)'.format(increment_num), purchase_num)
        print('+{}采购量(采购单位)'.format(increment_num), purchase_ratio_num)
    elif increment_num == 2:
        purchase_amount1 = cul_purchase_amount(
            goods_id, spec_id, purchase_ratio, wh_list,
            national_flag=national_flag,
            increment_num=1
        )
        # +2采购量 = T日至T+2月底的算法预估需求量 + SS2 + 预计损耗2 - 当前库存 - (在途CG/FH2 + 在途调拨2 + 在途PO2 + 在途PP2) - (+1采购量)
        purchase_num = pred_consume + ss_cnt[0] + loss_amount[0] - current_stock[0] - transit_total - purchase_amount1
        # 用料单位换算采购单位
        purchase_ratio_num = purchase_num / purchase_ratio
        print(date_list)
        print('+2采购量 = T日至T+2月底的算法预估需求量 + SS2 + 预计损耗2 - 当前库存 - (在途CG/FH2 + 在途调拨2 + 在途PO2 + 在途PP2) - (+1采购量)')
        # print('+{}采购量(用料单位)'.format(increment_num), purchase_num)
        print('+2采购量(采购单位)'.format(increment_num), purchase_ratio_num)

    print('T日至T+{}月底的算法预估需求量'.format(increment_num), pred_consume)
    print(ss_cnt[1])
    print('SS{}'.format(increment_num), ss_cnt[0])
    print(loss_amount[1])
    print('预计损耗{}'.format(increment_num), loss_amount[0])
    print('截止+{}损耗量(采购单位)'.format(increment_num), loss_amount[0] / purchase_ratio)
    print('在途数量', transit_total)
    print('截止+{}在途量(采购单位)'.format(increment_num), transit_amount1 / purchase_ratio)
    print('截止+{}PO在途(采购单位)'.format(increment_num), transit_list[1] / purchase_ratio)
    print(current_stock[1])
    print('当前库存(期末可用库存)', current_stock[0], '\n')

    # 全国需要各仓相加，不是取'-1'
    pred_new = cul_pred_data_total(0, goods_id, wh_list, 1, 18, start_date, end_date)
    print('查询+{}周期新品预测数据'.format(increment_num), pred_new/purchase_ratio)
    pred_new_adjust = cul_pred_data_total(1, goods_id, wh_list, 1, 18, start_date, end_date)
    print('查询调整后+{}周期新品预测数据'.format(increment_num), pred_new_adjust/purchase_ratio)
    pred_common = cul_pred_data_total(0, goods_id, wh_list, 2, 19, start_date, end_date)
    print('查询+{}周期常规品预测数据'.format(increment_num), pred_common/purchase_ratio)
    pred_common_adjust = cul_pred_data_total(1, goods_id, wh_list, 2, 19, start_date, end_date)
    print('查询调整后+{}周期常规品预测数据'.format(increment_num), pred_common_adjust/purchase_ratio, '\n')

    return purchase_num


if __name__ == '__main__':
    # 玫瑰味糖浆
    cul_end_order_day(44, increment_num=1)
    cul_end_order_day(44, increment_num=2)
    # xcy咖啡豆
    get_national_flag(48214)
