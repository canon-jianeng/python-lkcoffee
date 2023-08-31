
import json
import yaml
import pymysql
from current_stock import stock_list
from transit_data import transit_data
from lkcoffee_script import lk_tools


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

db_dm = pymysql.connect(
    host=mysql_conf['dm']['host'],
    user=mysql_conf['dm']['user'],
    password=mysql_conf['dm']['pwd'],
    database=mysql_conf['dm']['db'],
    port=mysql_conf['dm']['port']
)

# 使用 cursor() 方法创建一个游标对象 cursor
cursor = db_cooperation.cursor()
cursor_srm = db_srm.cursor()
cursor_dm = db_dm.cursor()

sql_pred_consume = mysql_sql['cooperation']['query_pred_consume']
sql_ss_cnt = mysql_sql['cooperation']['query_ss_cnt']
sql_loss_amount = mysql_sql['cooperation']['query_loss_amount']
sql_wh = mysql_sql['cooperation']['query_wh']
sql_pred_definite = mysql_sql['cooperation']['query_pred_definite']
sql_pred_v0 = mysql_sql['cooperation']['query_pred_v0']
sql_pred_amount = mysql_sql['cooperation']['query_pred_amount']
sql_day_consume = mysql_sql['cooperation']['query_day_consume']
sql_vlt = mysql_sql['cooperation']['query_vlt']
sql_spec_wh = mysql_sql['cooperation']['query_spec_wh']
sql_spec_version = mysql_sql['cooperation']['query_spec_version']
sql_spec_replace = mysql_sql['cooperation']['query_spec_replace']
sql_spec = mysql_sql['cooperation']['query_spec']
sql_purchase_ratio = mysql_sql['cooperation']['query_purchase_ratio']
sql_national_price = mysql_sql['srm']['query_national_price']
sql_shop_consume = mysql_sql['cooperation']['query_shop_consume']
sql_wh_consume = mysql_sql['cooperation']['query_wh_consume']
sql_large_class_id = mysql_sql['cooperation']['query_large_class_id']
sql_new_scene = mysql_sql['cooperation']['query_new_scene']
sql_po_new_param = mysql_sql['cooperation']['query_po_new_param']
sql_po_new_wh_param = mysql_sql['cooperation']['query_po_new_wh_param']
sql_po_sub_new_param = mysql_sql['cooperation']['query_po_sub_new_param']
sql_po_sub_new_wh_param = mysql_sql['cooperation']['query_po_sub_new_wh_param']
sql_central_data = mysql_sql['dm']['query_central_data']


def get_central_wh(goods_id, wh_id):
    # DM系统 "配置表列表" 的【自动CG仓货模式配置】
    cursor_dm.execute(sql_central_data)
    config_data = cursor_dm.fetchall()[0][0]
    data_json = json.loads(config_data)
    is_cdc, is_cdc_model = 0, 0
    for data_val in data_json:
        if data_val['cdc_wh_dept_id'] == float(wh_id) and data_val['goods_id'] == float(goods_id):
            is_cdc = data_val['is_cdc']
            is_cdc_model = data_val['is_cdc_model']
            print(is_cdc, is_cdc_model)
    return int(is_cdc), int(is_cdc_model)


def is_food_type(goods_id):
    cursor.execute(
        sql_large_class_id.format(goods_id)
    )
    large_class_id = cursor.fetchall()[0][0]
    # 配置中心【新品、次新品CG货物是食品的大类ID】: luckycooperation.orderstrategy.config
    # 判断 "商品大类" 是否为"食品"
    if large_class_id in [171, 224]:
        return True
    else:
        return False


def get_new_scene(goods_id, wh_id, new_flag):
    # 新品场景和计划完成日期
    scene_date = {}
    cursor.execute(
        sql_new_scene.format(goods_id, wh_id, new_flag)
    )
    sql_data = cursor.fetchall()
    for val in sql_data:
        scene_date[str(val[0])] = val[1].split(',')
    return scene_date


def get_po_new_param(goods_id, goods_type):
    # 新品字段（取全国数据）
    cursor.execute(
        sql_po_new_param.format(goods_id, goods_type)
    )
    po_new_tuple = cursor.fetchall()[0]
    return list(po_new_tuple)


def get_po_new_wh_param(goods_id, wh_id, goods_type):
    # 新品字段（取仓库数据）
    cursor.execute(
        sql_po_new_wh_param.format(goods_id, wh_id, goods_type)
    )
    po_new_tuple = cursor.fetchall()[0]
    return list(po_new_tuple)


def get_po_sub_new_param(goods_id, goods_type):
    # 次新品字段（取全国数据）
    cursor.execute(
        sql_po_sub_new_param.format(goods_id, goods_type)
    )
    po_sub_new_tuple = cursor.fetchall()[0]
    return list(po_sub_new_tuple)


def get_po_sub_new_wh_param(goods_id, wh_id, goods_type):
    # 次新品字段（取仓库数据）
    cursor.execute(
        sql_po_sub_new_wh_param.format(goods_id, wh_id, goods_type)
    )
    po_sub_new_tuple = cursor.fetchall()[0]
    return list(po_sub_new_tuple)


def new_scene_date(scene, plan_finish_date_list):
    # 新品场景
    date_list = []
    min_date = min(plan_finish_date_list)
    max_date = max(plan_finish_date_list)
    # 场景1: 同个货物只有一个上市计划
    if scene == '1':
        left_date = min_date
        right_date = min_date
        date_list = [left_date, right_date]
    # 场景2: 同个货物有多个上市计划，且"计划上市日期"相同
    elif scene == '2':
        left_date = min_date
        right_date = min_date
        date_list = [left_date, right_date]
    # 场景3: 同个货物有多个上市计划，且"计划上市日期"不同，且min("计划上市日期")和max("计划上市日期")的间隔 ≤ 11天（冷启动周期重合）
    elif scene == '3':
        left_date = min_date
        right_date = max_date
        date_list = [left_date, right_date]
    # 场景4: 同个货物有多个上市计划，且"计划上市日期"不同，且min("计划上市日期")和max("计划上市日期")的间隔 ＞ 11天（冷启动周期不重合）
    elif scene == '4':
        left_date = min_date
        right_date = min_date
        date_list = [left_date, right_date]
    return date_list


def sub_new_scene_date(scene, plan_finish_date_list):
    # 次新品的场景
    min_date = min(plan_finish_date_list)
    # 场景1: 同个货物只有一个上市计划
    if scene == '1':
        plan_date = min_date
    # 场景2: 同个货物有多个上市计划，且"计划上市日期"相同
    elif scene == '2':
        plan_date = min_date
    # 场景3: 同个货物有多个上市计划，且"计划上市日期"不同，且min("计划上市日期")和max("计划上市日期")的间隔 ≤ 11天（冷启动周期重合）
    elif scene == '3':
        plan_date = min_date
    # 场景4: 同个货物有多个上市计划，且"计划上市日期"不同，且min("计划上市日期")和max("计划上市日期")的间隔 ＞ 11天（冷启动周期不重合）
    elif scene == '4':
        plan_date = min_date
    # 场景5: 同个货物有多个上市计划，且"计划上市日期"不同，且包含新品和次新品
    elif scene == '5':
        plan_date = min_date
    else:
        plan_date = min_date
    return plan_date


def cul_shop_consume(goods_id, wh_id, start_date, end_date):
    # 门店消耗
    cursor.execute(
        sql_shop_consume.format(goods_id, wh_id, start_date, end_date)
    )
    shop_consume = cursor.fetchall()[0][0]
    return shop_consume


def cul_wh_out_num(goods_id, wh_id, start_date, end_date):
    # 仓库出库
    cursor.execute(
        sql_wh_consume.format(goods_id, wh_id, start_date, end_date)
    )
    wh_consume = cursor.fetchall()[0][0]
    return wh_consume


def get_cg_fh_trs(spec_wh_list, transit_type):
    transit_amount = 0
    data_list = []
    for transit_val in transit_data[transit_type]:
        for spec_wh in spec_wh_list:
            spec_id = str(transit_val['specId'])
            if spec_id == str(spec_wh[0]) and str(transit_val['whDeptId']) == str(spec_wh[1]):
                # 过滤重复数据
                if spec_wh not in data_list:
                    data_list.append(spec_wh)
                    print('在途CG(type=2)数量: {}'.format(transit_val['ztNum']),
                          '规格id: {}'.format(spec_wh[0]), '仓库id: {}'.format(spec_wh[1]))
                    transit_amount += transit_val['ztNum']
    return transit_amount


def get_po_pp(spec_wh_list, transit_type, national_flag):
    transit_amount = 0
    if national_flag == 1:
        wh_val = '-1'
    else:
        wh_val = str(spec_wh_list[0][1])
    for transit_dict in transit_data[transit_type]:
        spec_id = str(transit_dict['specId'])
        if spec_id == str(spec_wh_list[0][0]) and str(transit_dict['whDeptId']) == wh_val:
            print('在途PP(type=0)数量: {}'.format(transit_dict['ztNum']),
                  '规格id: {}'.format(spec_id), '仓库id: {}'.format(transit_dict['whDeptId']))
            transit_amount = transit_dict['ztNum']
    return transit_amount


def cul_transit_amount(type_val: int, spec_wh_list: list, national_flag=0):
    # 日志关键词:【智慧订单】获取汇总在途成功、仓库汇总在途1、仓库汇总在途2
    # 数仓取值: 在途CG、在途FH、在途调拨(货物纬度), 全国取各仓库总和
    # 数仓取值: 在途PO、在途PP(规格纬度), 全国取'-1'
    transit_amount = 0
    if type_val == 0:
        # 在途PP(type=0)
        transit_amount = get_po_pp(spec_wh_list, 'type_0', national_flag)
    elif type_val == 1:
        # 在途PO(type=1)
        transit_amount = get_po_pp(spec_wh_list, 'type_1', national_flag)
    elif type_val == 2:
        # 在途CG(type=2)
        transit_amount = get_cg_fh_trs(spec_wh_list, 'type_2')
    elif type_val == 3:
        # 在途FH(type=3)
        transit_amount = get_cg_fh_trs(spec_wh_list, 'type_3')
    elif type_val == 4:
        # 在途调拨(type=4)
        transit_amount = get_cg_fh_trs(spec_wh_list, 'type_4')
    elif type_val == 5:
        # 在途配货(type=5)
        transit_amount = get_cg_fh_trs(spec_wh_list, 'type_5')
    elif type_val == 6:
        # 在途cc(type=6)
        transit_amount = get_cg_fh_trs(spec_wh_list, 'type_6')
    return transit_amount


def cul_current_stock(spec_wh_list: list):
    # 日志关键词:【智慧订单】获取实时库存
    # 数仓取值: 当前库存
    stock_total = 0
    data_list = []
    for data_dict in stock_list:
        for spec_wh in spec_wh_list:
            if str(data_dict['specId']) == str(spec_wh[0]) and str(data_dict['whDeptId']) == str(spec_wh[1]):
                # 过滤重复数据
                if spec_wh not in data_list:
                    data_list.append(spec_wh)
                    print('当前库存(获取实时库存): {}'.format(data_dict['totalNum']),
                          '规格id: {}'.format(spec_wh[0]), '仓库id: {}'.format(spec_wh[1]))
                    stock_total += data_dict['totalNum']
    return stock_total


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


def get_po_vlt(goods_id):
    po_vlt = 0
    cursor.execute(
        sql_vlt.format(goods_id)
    )
    sql_data = cursor.fetchall()
    if sql_data != () and sql_data is not None:
        po_vlt = sql_data[0][0]
    return po_vlt


def get_wh_list():
    # 仓库：全国所有“已完善”，且非“已停业”的城市仓
    wh_list = []
    cursor.execute(
        sql_wh
    )
    wh_data = cursor.fetchall()
    for val in wh_data:
        wh_list.append(val[0])
    return wh_list


def get_spec_list(goods_id, spec_id, wh_list):
    # 获取【货物的规格id和可替换规格】和【仓库】
    spec_wh_list = []
    for wh_id in wh_list:
        cursor.execute(sql_spec_version.format(spec_id, wh_id))
        version = cursor.fetchall()[0][0]
        if version == '':
            spec_wh_list.append([int(spec_id), int(wh_id)])
        else:
            cursor.execute(sql_spec_replace.format(version))
            sql_data = cursor.fetchall()
            for data_val in sql_data:
                if data_val[0] == int(goods_id) and data_val[2] == int(wh_id):
                    spec_wh_list.append([data_val[1], data_val[2]])
    new_list = []
    # 列表数据去重
    [new_list.append(i) for i in spec_wh_list if i not in new_list]
    return new_list


def get_spec_supplier(goods_id, wh_range):
    # 获取货物规格和供应商id
    spec_dict = {}
    cursor.execute(sql_spec_wh.format(goods_id, wh_range))
    spec_data = cursor.fetchall()
    for data_val in spec_data:
        spec_supplier = str(data_val[0]) + '_' + str(data_val[1])
        if spec_supplier in spec_dict:
            spec_dict[spec_supplier].append(data_val[2])
        else:
            spec_dict.update({spec_supplier: [data_val[2]]})
    return spec_dict


def get_spec_ratio(spec_id):
    # 查询用料单位换算采购单位
    cursor.execute(
        sql_purchase_ratio.format(spec_id)
    )
    purchase_data = cursor.fetchall()
    purchase_ratio = float(purchase_data[0][0]) * float(purchase_data[0][1])
    return purchase_ratio


def get_price_order(spec_id, supplier_id):
    # 查询报价单
    cursor_srm.execute(
        sql_national_price.format(spec_id, supplier_id)
    )
    price_data = cursor_srm.fetchall()
    return price_data


if __name__ == '__main__':
    get_central_wh(20617, 4001)
