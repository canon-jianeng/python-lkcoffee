
import json
import yaml
import pymysql
from lkcoffee_script import lk_tools
from current_stock import stock_list
from transit_data import transit_data
from theory_shop_stock import theory_shop_stock_list


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
sql_spec_supplier = mysql_sql['cooperation']['query_spec_supplier']
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
sql_sale_shop_definite = mysql_sql['cooperation']['query_sale_shop_definite']
sql_sale_shop_v0 = mysql_sql['cooperation']['query_sale_shop_v0']
sql_future_sale_shop = mysql_sql['cooperation']['query_future_sale_shop']
sql_actual_sale_shop = mysql_sql['cooperation']['query_actual_sale_shop']


def get_central_wh(goods_id, wh_id):
    # DM系统 "配置表列表" 的【自动CG仓货模式配置】
    cursor_dm.execute(sql_central_data)
    config_data = cursor_dm.fetchall()[0][0]
    data_json = json.loads(config_data)
    is_cdc, is_cdc_model = 0, 0
    for data_val in data_json:
        if (str(data_val['wh_dept_id']).split('.')[0] == str(wh_id)
                and str(data_val['goods_id']).split('.')[0] == str(goods_id)):
            is_cdc = data_val['is_cdc']
            is_cdc_model = data_val['is_cdc_model']
    return int(is_cdc), int(is_cdc_model)


def is_food_type(goods_id):
    cursor.execute(
        sql_large_class_id.format(goods_id)
    )
    large_class_id = cursor.fetchall()[0][0]
    # 配置中心【新品、次新品CG货物是食品的大类ID】: luckycooperation.special.config
    # 修改这个字段: foodsRelateGoodsLargeClass
    # 判断 "商品大类" 是否为"食品"
    if large_class_id in [3, 36, 127, 171]:
        return True
    else:
        return False


def get_new_scene(goods_id, wh_id, new_flag):
    # 同一个仓库和同一个货物只有一个场景
    # 新品场景和计划完成日期
    scene_date = {}
    cursor.execute(
        sql_new_scene.format(goods_id, wh_id, new_flag)
    )
    sql_data = cursor.fetchall()
    for val in sql_data:
        # {场景值: [计划日期, 商品id]}
        scene_date[str(val[0])] = [val[1].split(','), val[2].split(',')]
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


def get_cg_fh_trs(spec_wh_list, transit_type, plan_finish_date):
    plan_date = lk_tools.datetool.str_to_date(plan_finish_date)
    transit_amount = 0
    type_data = transit_data[transit_type]
    for date_val in type_data:
        end_date = lk_tools.datetool.str_to_date(date_val)
        if end_date <= plan_date:
            data_list = []
            for transit_val in type_data[date_val]:
                for spec_wh in spec_wh_list:
                    spec_id = str(transit_val['specId'])
                    if spec_id == str(spec_wh[0]) and str(transit_val['whDeptId']) == str(spec_wh[1]):
                        # 过滤重复数据
                        if spec_wh not in data_list:
                            data_list.append(spec_wh)
                            print('在途数量: {}'.format(transit_val['ztNum']),
                                  '规格id: {}'.format(spec_wh[0]), '仓库id: {}'.format(spec_wh[1]))
                            transit_amount += transit_val['ztNum']
    return transit_amount


def get_po_pp(spec_wh_list, transit_type, plan_finish_date, national_flag):
    plan_date = lk_tools.datetool.str_to_date(plan_finish_date)
    transit_amount = 0
    if national_flag == 1:
        wh_val = '-1'
    else:
        wh_val = str(spec_wh_list[0][1][0])
    type_data = transit_data[transit_type]
    for date_val in type_data:
        end_date = lk_tools.datetool.str_to_date(date_val)
        if end_date <= plan_date:
            for transit_val in type_data[date_val]:
                spec_id = str(transit_val['specId'])
                if spec_id == str(spec_wh_list[0][0]) and str(transit_val['whDeptId']) == wh_val:
                    print('在途数量: {}'.format(transit_val['ztNum']),
                          '规格id: {}'.format(spec_id), '仓库id: {}'.format(transit_val['whDeptId']))
                    transit_amount = transit_val['ztNum']
    return transit_amount


def cul_transit_amount(type_val: int, spec_wh_list: list, plan_finish_date, national_flag=0):
    # 日志关键词:【智慧订单】获取汇总在途成功、仓库汇总在途1、仓库汇总在途2
    # 数仓取值: 在途CG、在途FH、在途调拨(货物纬度), 全国取各仓库总和
    # 数仓取值: 在途PO、在途PP(规格纬度), 全国取'-1'
    transit_amount = 0
    if type_val == 0:
        # 在途PP(type=0)
        transit_amount = get_po_pp(spec_wh_list, 'type_0', plan_finish_date, national_flag)
    elif type_val == 1:
        # 在途PO(type=1)
        transit_amount = get_po_pp(spec_wh_list, 'type_1', plan_finish_date, national_flag)
    elif type_val == 2:
        # 在途CG(type=2)
        transit_amount = get_cg_fh_trs(spec_wh_list, 'type_2', plan_finish_date)
    elif type_val == 3:
        # 在途FH(type=3)
        transit_amount = get_cg_fh_trs(spec_wh_list, 'type_3', plan_finish_date)
    elif type_val == 4:
        # 在途调拨(type=4)
        transit_amount = get_cg_fh_trs(spec_wh_list, 'type_4', plan_finish_date)
    elif type_val == 5:
        # 在途配货(type=5)
        transit_amount = get_cg_fh_trs(spec_wh_list, 'type_5', plan_finish_date)
    elif type_val == 6:
        # 在途cc(type=6)
        transit_amount = get_cg_fh_trs(spec_wh_list, 'type_6', plan_finish_date)
    return transit_amount


def cul_theory_shop_stock(goods_id, wh_list: list):
    # 日志关键词:【智慧订单】获取实时门店货物的理论可用库存成功
    # 数仓取值: 门店货物的理论可用库存
    stock_total = 0
    data_list = []
    for data_dict in theory_shop_stock_list:
        for wh_id in wh_list:
            if str(data_dict['goodsId']) == str(goods_id) and str(data_dict['whDeptId']) == str(wh_id):
                goods_wh = [str(goods_id), str(wh_id)]
                # 过滤重复数据
                if goods_wh not in data_list:
                    data_list.append(goods_wh)
                    print('门店货物的理论可用库存: {}'.format(data_dict['theoryStockNum']),
                          '货物id: {}'.format(goods_id), '仓库id: {}'.format(wh_id))
                    stock_total += data_dict['theoryStockNum']
    return stock_total


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


def get_goods_spec_list(goods_id):
    # 货物规格：货物下所有"已完善"，且未删除的货物规格
    spec_list = []
    cursor.execute(sql_spec.format(goods_id))
    spec_data = cursor.fetchall()
    for val in spec_data:
        spec_list.append(val[0])
    return spec_list


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
    cursor.execute(sql_spec_supplier.format(goods_id, wh_range))
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


def get_sale_shop_version(year_val):
    # 判断售卖门店数是否存在确定版
    cursor.execute(sql_sale_shop_definite.format(year_val))
    sql_data = cursor.fetchall()
    if sql_data == ():
        # 不存在确定版, 获取 v0 版本
        cursor.execute(sql_sale_shop_v0.format(year_val))
        sql_data = cursor.fetchall()
        if sql_data == ():
            version_id = 0
        else:
            version_id = int(sql_data[0][0])
    else:
        version_id = int(sql_data[0][0])
    return version_id


def get_sale_shop_num(wh_dept_id, commodity_id, date_list):
    # 获取过去和未来的售卖门店数
    year_val = date_list[0].split('-')[0]
    version_id = get_sale_shop_version(year_val)
    now_val = lk_tools.datetool.get_now_date()
    now_date = lk_tools.datetool.str_to_date(now_val)
    left_date = lk_tools.datetool.str_to_date(date_list[0])
    right_date = lk_tools.datetool.str_to_date(date_list[1])
    sale_shop_num, sale_shop_day = 0, 0
    if left_date < now_date:
        for day_num in range((now_date - left_date).days):
            date_val = lk_tools.datetool.cul_date(date_list[0], day_num)
            # 过去售卖门店数
            cursor.execute(sql_actual_sale_shop.format(
                wh_dept_id, commodity_id, year_val, date_val
            ))
            sql_data = cursor.fetchall()
            # 过滤查询不到数据的日期
            if sql_data != ():
                sale_shop_num += sql_data[0][0]
                sale_shop_day += 1
        for day_num in range((right_date - now_date).days + 1):
            date_val = lk_tools.datetool.cul_date(now_val, day_num)
            # 未来售卖门店数
            cursor.execute(sql_future_sale_shop.format(
                version_id, wh_dept_id, commodity_id, year_val, date_val
            ))
            sql_data = cursor.fetchall()
            if sql_data != ():
                sale_shop_num += sql_data[0][0]
                sale_shop_day += 1
    else:
        for day_num in range((right_date - left_date).days + 1):
            date_val = lk_tools.datetool.cul_date(date_list[0], day_num)
            # 未来售卖门店数
            cursor.execute(sql_future_sale_shop.format(
                version_id, wh_dept_id, commodity_id, year_val, date_val
            ))
            sql_data = cursor.fetchall()
            if sql_data != ():
                sale_shop_num += sql_data[0][0]
                sale_shop_day += 1
    return sale_shop_num, sale_shop_day


def get_sale_shop_total(wh_dept_id, commodity_id, date_list):
    left_year = int(date_list[0].split('-')[0])
    right_year = int(date_list[1].split('-')[0])
    # 日期范围包含不同年份
    if left_year == right_year:
        sale_shop_num, sale_shop_day = get_sale_shop_num(wh_dept_id, commodity_id, date_list)
    else:
        left_num, left_day = get_sale_shop_num(
            wh_dept_id, commodity_id, [date_list[0], str(left_year) + '-' + '12' + '-' + '31']
        )
        right_num, right_day = get_sale_shop_num(
            wh_dept_id, commodity_id, [str(right_year) + '-' + '01' + '-' + '01', date_list[1]]
        )
        sale_shop_num = left_num + right_num
        sale_shop_day = left_day + right_day
    return sale_shop_num, sale_shop_day


if __name__ == '__main__':
    get_central_wh(83625, 327193)
    is_food_type(83625)
    print(get_sale_shop_version('2024'))
    get_sale_shop_total(245971, 5990, ['2023-09-01', '2024-01-03'])
