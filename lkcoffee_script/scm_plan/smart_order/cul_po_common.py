
import datetime
from lkcoffee_script import lk_tools
import order_strategy

"""
先删除数据 DELETE FROM t_po_order_strategy, 再执行定时任务 PoStrategyTask

1.计算采购数量时，所有的计算因子 都用“用料单位”计算，算出采购量后
2.再换算为“采购单位”，换算时，若有小数，向上取整

"""


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


def cul_pred_data_total(adjust_flag, goods_id, wh_list, mark_type, type_val, start_date, end_date):
    pred_total = 0
    for wh in wh_list:
        pred_total += order_strategy.cul_pred_data(adjust_flag, goods_id, wh, mark_type, type_val, start_date, end_date)
    return pred_total


def cul_end_order_day(goods_id, increment_num):
    date_list = get_date_range(increment_num, 1)
    # 当天日期
    now_date = datetime.datetime.strptime(date_list[0], '%Y-%m-%d')
    # 计划完成日期
    finish_plan_date = datetime.datetime.strptime(date_list[1], '%Y-%m-%d')
    print('+{}计划完成日期'.format(increment_num), date_list[1])
    po_vlt = order_strategy.get_po_vlt(goods_id)
    # 计划完成日期 - 当前日期 < vlt, "是否紧急PO"为是
    days = (finish_plan_date - now_date).days
    if days < po_vlt:
        print('计划完成日期-当前日期={} < vlt={}'.format(days, po_vlt))
        print("是否紧急PO{}: 是".format(increment_num))
    else:
        print('计划完成日期-当前日期={} > vlt={}'.format(days, po_vlt))
        print("是否紧急PO{}: 否".format(increment_num))
    # PO最晚下单日 = 计划完成日期 - po_vlt
    end_order_date = finish_plan_date - datetime.timedelta(days=po_vlt)
    print("PO{}最晚下单日".format(increment_num), end_order_date, '\n')


def get_national_flag(goods_id):
    # 仓库：全国所有"已完善"，且非"已停业"的城市仓
    wh_list = order_strategy.get_wh_list()
    wh_range = str(wh_list).replace('[', '(').replace(']', ')')
    # 获取货物规格和供应商id
    spec_dict = order_strategy.get_spec_supplier(goods_id, wh_range)
    print(spec_dict, '\n')
    '''
    场景1: 多个不同货物规格和不同的供应商 对应 多个全国PO
    例: 
      1.规格: xcy咖啡豆1箱2000克(id: 301814), 对应供应商: SC004990
      2.规格: xcy咖啡豆1000g(id: 306240), 对应供应商: SC202917
    '''
    # 判断是否全国PO
    for spec_supplier in spec_dict.keys():
        spec_val = spec_supplier.split('_')
        spec_id = spec_val[0]
        supplier_id = spec_val[1]
        wh_list = spec_dict[spec_supplier]
        '''
        场景2: 一个仓库下的货物规格id和可替换货物规格【满足同一个货物】
        '''
        spec_wh_list = order_strategy.get_spec_list(goods_id, spec_id, wh_list)
        print('货物规格和仓库:', spec_wh_list)
        # 当前库存(货物纬度)
        current_stock = order_strategy.cul_current_stock(spec_wh_list)
        # 在途数量(货物纬度)
        transit_cg = order_strategy.cul_transit_amount(2, spec_wh_list)
        print('在途CG总数量:', transit_cg)
        transit_fh = order_strategy.cul_transit_amount(3, spec_wh_list)
        print('在途FH总数量:', transit_fh)
        transit_trs = order_strategy.cul_transit_amount(4, spec_wh_list)
        print('在途调拨总数量:', transit_trs)
        transit_amount = transit_cg + transit_fh + transit_trs
        # 查询用料单位换算采购单位
        purchase_ratio = order_strategy.get_spec_ratio(spec_id)
        print('用料单位换算采购单位', purchase_ratio)
        # 查询报价单
        price_data = order_strategy.get_price_order(spec_id, supplier_id)
        if price_data != () and price_data is not None:
            price_new = price_data[0]
            # 报价城市为全国(-1), 且"是否全国同一价"为"是"
            if str(price_new[0]) == '-1' and str(price_new[1]) == '1':
                print(
                    '全国PO为"是"', '规格id:{}'.format(spec_id), '供应商id:{}'.format(supplier_id),
                    '仓库列表:{}'.format(wh_list), '\n'
                )
                transit_po = order_strategy.cul_transit_amount(1, [[spec_id, wh_list]], 1)
                transit_pp = order_strategy.cul_transit_amount(0, [[spec_id, wh_list]], 1)
                transit_list = [transit_amount, transit_po, transit_pp]
                cul_purchase_amount(goods_id, current_stock, transit_list, purchase_ratio, wh_list)
            else:
                print(
                    '全国PO为"否"', '规格id:{}'.format(spec_id), '供应商id:{}'.format(supplier_id),
                    '仓库列表:{}'.format(wh_list), '\n'
                )
                transit_po = order_strategy.cul_transit_amount(1, [[spec_id, wh_list]], 0)
                transit_pp = order_strategy.cul_transit_amount(0, [[spec_id, wh_list]], 0)
                transit_list = [transit_amount, transit_po, transit_pp]
                cul_purchase_amount(goods_id, current_stock, transit_list, purchase_ratio, wh_list)
        else:
            print(
                '全国PO为"否"', '规格id:{}'.format(spec_id), '供应商id:{}'.format(supplier_id),
                '仓库列表:{}'.format(wh_list), '\n'
            )
            transit_po = order_strategy.cul_transit_amount(1, [[spec_id, wh_list]], 0)
            transit_pp = order_strategy.cul_transit_amount(0, [[spec_id, wh_list]], 0)
            transit_list = [transit_amount, transit_po, transit_pp]
            cul_purchase_amount(goods_id, current_stock, transit_list, purchase_ratio, wh_list)


def cul_purchase_amount(goods_id, current_stock, transit_list,
                        purchase_ratio, wh_list, increment_num=2):
    """
    :param goods_id: 货物id
    :param current_stock: 货物当前库存
    :param transit_list: 在途库存
    :param purchase_ratio: 用料采购单位换算
    :param wh_list: 仓库列表
    :param increment_num: T+n月, n为1或者2
    :return
    """
    wh_range = str(wh_list).replace('[', '(').replace(']', ')')

    if increment_num == 1:
        # 获取T日, T+0月最后一天
        date_list = get_date_range(0)
        print('+0采购量日期:', date_list)
        pred_consume = order_strategy.cul_pred_consume(goods_id, wh_range, date_list[0], date_list[1])
        print('T日至T+0月底的算法预估需求量', pred_consume)
        print('+0周期需求量(采购单位)', pred_consume/purchase_ratio, '\n')
        # T-1, T-2, T-3, T-4周日均消耗
        day_consume = order_strategy.cul_day_consume(goods_id, wh_range)
        print('T-1周日均消耗(采购单位)', round(day_consume[0] / purchase_ratio, 5))
        print('T-2周日均消耗(采购单位)', round(day_consume[1] / purchase_ratio, 5))
        print('T-3周日均消耗(采购单位)', round(day_consume[2] / purchase_ratio, 5))
        print('T-4周日均消耗(采购单位)', round(day_consume[3] / purchase_ratio, 5), '\n')

    # 获取T日, T+1月最后一天或者T+2月最后一天
    date_list = get_date_range(increment_num)
    start_date = date_list[0]
    end_date = date_list[1]
    pred_consume = order_strategy.cul_pred_consume(goods_id, wh_range, start_date, end_date)
    ss_cnt = order_strategy.cul_ss_cnt(increment_num, goods_id, wh_range)
    loss_amount = order_strategy.cul_loss_amount(goods_id, wh_range, start_date, end_date)
    transit_amount = transit_list[0]
    transit_po = transit_list[1]
    transit_pp = transit_list[2]
    transit_po_pp = transit_pp + transit_po

    purchase_num, purchase_ratio_num = 0, 0
    if increment_num == 1:
        # +1采购量 = T日至T+1月底的算法预估需求量 + SS1 + 预计损耗1 - 当前库存 - (在途CG1 + 在途FH1 + 在途调拨1) - (在途PO1 + 在途PP1)
        purchase_num = pred_consume + ss_cnt[0] + loss_amount[0] - current_stock - transit_amount - transit_po_pp
        purchase_ratio_num = purchase_num / purchase_ratio
        print('+1采购量日期:', date_list)
        print('+1采购量 = T日至T+1月底的算法预估需求量 + SS1 + 预计损耗1 - 当前库存 - (在途CG1 + 在途FH1 + 在途调拨1) - (在途PO1 + 在途PP1)')
        print('+{}采购量(用料单位)'.format(increment_num), purchase_num)
        print('+{}采购量(采购单位)'.format(increment_num), purchase_ratio_num)
        print('---------------------------------------------------')
    elif increment_num == 2:
        # 计算+1采购量
        purchase_amount1 = cul_purchase_amount(
            goods_id, current_stock, transit_list,
            purchase_ratio, wh_list,
            increment_num=1
        )
        # +1采购量为负数, 则取0
        purchase_amount1 = max(purchase_amount1, 0)
        print('+1采购量:', purchase_amount1)
        # +2采购量 = T日至T+2月底的算法预估需求量 + SS2 + 预计损耗2 - 当前库存 - (在途CG2 + 在途FH2 + 在途调拨2) - (在途PO2 + 在途PP2) - (+1采购量)
        purchase_num = (pred_consume + ss_cnt[0] + loss_amount[0] - current_stock
                        - transit_amount - transit_po_pp - purchase_amount1)
        # +2采购量为负数, 则取0
        purchase_num = max(purchase_num, 0)
        # 用料单位换算采购单位
        purchase_ratio_num = purchase_num / purchase_ratio
        print('+2采购量日期:', date_list)
        print('+2采购量 = T日至T+2月底的算法预估需求量 + SS2 + 预计损耗2 - 当前库存 - (在途CG2 + 在途FH2 + 在途调拨2) - (在途PO2 + 在途PP2) - (+1采购量)')
        print('+{}采购量(用料单位)'.format(increment_num), purchase_num)
        print('+2采购量(采购单位)'.format(increment_num), purchase_ratio_num)
        print('---------------------------------------------------')

    print('T日至T+{}月底的算法预估需求量'.format(increment_num), pred_consume)
    print(ss_cnt[1])
    print('SS{}'.format(increment_num), ss_cnt[0])
    print(loss_amount[1])
    print('预计损耗{}'.format(increment_num), loss_amount[0])
    print('截止+{}损耗量(采购单位)'.format(increment_num), loss_amount[0] / purchase_ratio)
    print('截止+{}在途量'.format(increment_num), transit_amount)
    print('截止+{}在途量(采购单位)'.format(increment_num), transit_amount / purchase_ratio)
    print('截止+{}PO在途(采购单位)'.format(increment_num), transit_po / purchase_ratio)
    print('当前库存【期末可用库存】', current_stock)
    print('当前库存【期末可用库存】(采购单位)', current_stock / purchase_ratio, '\n')

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
    cul_end_order_day(48214, increment_num=1)
    cul_end_order_day(48214, increment_num=2)
    # xcy咖啡豆
    get_national_flag(48214)
