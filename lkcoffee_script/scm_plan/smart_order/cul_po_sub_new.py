
from lkcoffee_script import lk_tools
import order_strategy


def get_national_flag(goods_id):
    # 仓库：全国所有"已完善"，且非"已停业"的城市仓
    wh_list = order_strategy.get_wh_list()
    wh_range = str(wh_list).replace('[', '(').replace(']', ')')
    # 获取货物规格和供应商id
    spec_dict = order_strategy.get_spec_supplier(goods_id, wh_range)
    print(spec_dict, '\n')
    # 判断是否全国PO
    for spec_supplier in spec_dict.keys():
        spec_val = spec_supplier.split('_')
        spec_id = spec_val[0]
        supplier_id = spec_val[1]
        # 多个不同货物规格和不同的供应商 对应 多个全国PO
        # 相同货物规格和供应商id的仓库
        wh_data = spec_dict[spec_supplier]
        # 相同计划完成日期的仓库
        date_wh_dict = get_plan_date(goods_id, wh_data)
        for plan_date in date_wh_dict:
            wh_list = date_wh_dict[plan_date]
            # 获取一个仓库下的货物规格id和可替换货物规格【满足同一个货物】
            spec_wh_list = order_strategy.get_spec_list(goods_id, spec_id, wh_list)
            print('货物规格:', spec_wh_list)
            # 当前库存(货物纬度)
            current_stock = order_strategy.cul_current_stock(spec_wh_list)
            # 在途数量(货物纬度)
            transit_cg = order_strategy.cul_transit_amount(2, spec_wh_list)
            print('在途CG总数量:', transit_cg)
            transit_fh = order_strategy.cul_transit_amount(3, spec_wh_list)
            print('在途FH总数量:', transit_fh)
            transit_trs = order_strategy.cul_transit_amount(4, spec_wh_list)
            print('在途调拨总数量:', transit_trs)
            transit_delivery = order_strategy.cul_transit_amount(5, spec_wh_list)
            print('在途配货总数量:', transit_delivery)
            transit_amount = transit_cg + transit_fh + transit_trs + transit_delivery
            # 查询用料单位换算采购单位
            purchase_ratio = order_strategy.get_spec_ratio(spec_id)
            print('用料单位换算采购单位', purchase_ratio)
            print('计划完成日期:', plan_date)
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
                    cul_sub_new_purchase_amount(goods_id, current_stock, transit_list, purchase_ratio, wh_list)
                else:
                    print(
                        '全国PO为"否"', '规格id:{}'.format(spec_id), '供应商id:{}'.format(supplier_id),
                        '仓库列表:{}'.format(wh_list), '\n'
                    )
                    transit_po = order_strategy.cul_transit_amount(1, [[spec_id, wh_list]], 0)
                    transit_pp = order_strategy.cul_transit_amount(0, [[spec_id, wh_list]], 0)
                    transit_list = [transit_amount, transit_po, transit_pp]
                    cul_sub_new_purchase_amount(goods_id, current_stock, transit_list, purchase_ratio, wh_list)
            else:
                print(
                    '全国PO为"否"', '规格id:{}'.format(spec_id), '供应商id:{}'.format(supplier_id),
                    '仓库列表:{}'.format(wh_list), '\n'
                )
                transit_po = order_strategy.cul_transit_amount(1, [[spec_id, wh_list]], 0)
                transit_pp = order_strategy.cul_transit_amount(0, [[spec_id, wh_list]], 0)
                transit_list = [transit_amount, transit_po, transit_pp]
                cul_sub_new_purchase_amount(goods_id, current_stock, transit_list, purchase_ratio, wh_list)


def cul_sub_new_purchase_amount(goods_id, current_stock, transit_list, purchase_ratio, wh_list):
    sub_new_num_total = 0
    for wh_id in wh_list:
        sub_new_num = cul_po_sub_new(goods_id, wh_id)
        sub_new_num_total += sub_new_num
    # 次新品补单量 = 消耗量 - 当前库存 - 在途配货 - 在途CG/FH - 在途调拨 - 在途PP1 - 在途PO1
    sub_new_num_total = max(sub_new_num_total - current_stock - transit_list[0], 0)
    sub_new_num_total = max(sub_new_num_total - transit_list[1] - transit_list[2], 0)
    print('次新品补采-次新品补单量:', sub_new_num_total / purchase_ratio, '\n')


def get_plan_date(goods_id, wh_list):
    now_date = lk_tools.datetool.get_now_date()
    # 次新品备货参数取全国数据
    po_new_param = order_strategy.get_po_sub_new_param(goods_id, 0)
    bp_po_adj = po_new_param[2]
    vlt = po_new_param[0]
    date_wh_dict = {}
    for wh_id in wh_list:
        scene_dict = order_strategy.get_new_scene(goods_id, wh_id, 2)
        for scene_val in scene_dict:
            plan_finish_date_list = scene_dict[scene_val]
            if scene_val == '5':
                # 计划完成日期 = min(当前日+调整后BP-PO+调整后VLT, min("计划上市日期")-15天)
                left_date = lk_tools.datetool.cul_date(now_date, bp_po_adj + vlt)
                right_date = lk_tools.datetool.cul_date(min(plan_finish_date_list), -15)
                plan_finish_date = min(left_date, right_date)
            else:
                # 计划完成日期 = 当前日 + 调整后BP-PO + 调整后VLT
                plan_finish_date = lk_tools.datetool.cul_date(now_date, bp_po_adj + vlt)
            if plan_finish_date in date_wh_dict.keys():
                date_wh_dict[plan_finish_date].append(wh_id)
            else:
                date_wh_dict[plan_finish_date] = [wh_id]
    print(date_wh_dict)
    return date_wh_dict


def cul_po_sub_new(goods_id, wh_id):
    now_date = lk_tools.datetool.get_now_date()
    # 次新品备货参数取全国数据
    po_new_param = order_strategy.get_po_sub_new_param(goods_id, 0)
    # 次新品备货参数取仓库数据
    po_new_wh_param = order_strategy.get_po_sub_new_wh_param(goods_id, wh_id, 0)
    po_sub_new_param = po_new_param + po_new_wh_param
    # 判断货物大类是否食品
    large_class_flag = order_strategy.is_food_type(goods_id)
    # 判断是否是中心仓
    is_cdc, is_cdc_model = order_strategy.get_central_wh(goods_id, wh_id)
    if is_cdc == 1 and is_cdc_model == 0:
        # 非中心仓
        central_type = 0
    else:
        # 中心仓
        central_type = 1

    # 调整后BP-PO
    bp_po_adj = po_sub_new_param[2]
    vlt = po_sub_new_param[0]
    ss = po_sub_new_param[1]
    # 调整后WT
    wt_adj = po_sub_new_param[3]
    print('调整后BP-PO: {}, vlt: {}, ss: {}, 调整后WT: {}'.format(
        bp_po_adj, vlt, ss, wt_adj)
    )

    if central_type == 1:
        # [当前日, 当前日+(调整后BP-PO+调整后VLT+调整后SS)]周期
        start_date = now_date
        end_date = lk_tools.datetool.cul_date(now_date, bp_po_adj + vlt + ss)
        if large_class_flag:
            # 次新品补单量 = [当前日, 调整后BP-PO+调整后VLT+调整后SS+调整后WT]周期内【门店消耗】需求量
            sub_new_num = order_strategy.cul_shop_consume(goods_id, wh_id, start_date, end_date)
        else:
            # 次新品补单量 = [当前日, 调整后BP-PO+调整后VLT+调整后SS+调整后WT]周期内【仓库出库】需求量
            sub_new_num = order_strategy.cul_wh_out_num(goods_id, wh_id, start_date, end_date)
    else:
        # [当前日, 当前日+(调整后BP-PO+调整后VLT+调整后SS+调整后WT)]周期
        start_date = now_date
        end_date = lk_tools.datetool.cul_date(now_date, bp_po_adj + vlt + ss + wt_adj)
        if large_class_flag:
            # 次新品补单量 = [当前日, 调整后BP-PO+调整后VLT+调整后SS+调整后WT]周期内【门店消耗】需求量
            sub_new_num = order_strategy.cul_shop_consume(goods_id, wh_id, start_date, end_date)
        else:
            # 次新品补单量 = [当前日, 调整后BP-PO+调整后VLT+调整后SS+调整后WT]周期内【仓库出库】需求量
            sub_new_num = order_strategy.cul_wh_out_num(goods_id, wh_id, start_date, end_date)
    print(sub_new_num)
    return float(sub_new_num)


if __name__ == '__main__':
    # JK咖啡豆（仓配\计算） 货物id: 83626
    # 货物大类: JK原料 货物大类id: 202
    # 供应商: 小奶狗  SC004990  1964
    # 供应商: 北京赢识  SC202917  629992
    '''
    货物规格id  供应商id  仓库id
    364754     1964:    [327193]
    364755     1964:    [245971, 245871]
    3284866     629992:  [326932, 245770]
    '''
    get_national_flag(83626)
