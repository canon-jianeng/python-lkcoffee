
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
            # 一个仓库下的货物规格id和可替换货物规格【满足同一个货物】
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
            transit_amount = transit_cg + transit_fh + transit_trs
            # 查询用料单位换算采购单位
            purchase_ratio = order_strategy.get_spec_ratio(spec_id)
            print('用料单位换算采购单位', purchase_ratio)
            cul_plan_finish_date(plan_date)
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
                    cul_new_purchase_amount(goods_id, current_stock, transit_list, purchase_ratio, wh_list, 1)
                else:
                    print(
                        '全国PO为"否"', '规格id:{}'.format(spec_id), '供应商id:{}'.format(supplier_id),
                        '仓库列表:{}'.format(wh_list), '\n'
                    )
                    transit_po = order_strategy.cul_transit_amount(1, [[spec_id, wh_list]], 0)
                    transit_pp = order_strategy.cul_transit_amount(0, [[spec_id, wh_list]], 0)
                    transit_list = [transit_amount, transit_po, transit_pp]
                    cul_new_purchase_amount(goods_id, current_stock, transit_list, purchase_ratio, wh_list, 1)
            else:
                print(
                    '全国PO为"否"', '规格id:{}'.format(spec_id), '供应商id:{}'.format(supplier_id),
                    '仓库列表:{}'.format(wh_list), '\n'
                )
                transit_po = order_strategy.cul_transit_amount(1, [[spec_id, wh_list]], 0)
                transit_pp = order_strategy.cul_transit_amount(0, [[spec_id, wh_list]], 0)
                transit_list = [transit_amount, transit_po, transit_pp]
                cul_new_purchase_amount(goods_id, current_stock, transit_list, purchase_ratio, wh_list, 1)


def cul_new_purchase_amount(goods_id, current_stock, transit_list, purchase_ratio, wh_list, new_flag):
    first_batch_num = 0
    stocking_up_num = 0
    material_pre_num = 0
    for wh_id in wh_list:
        new_list = cul_goods_scene(goods_id, wh_id, new_flag)
        first_batch_num += new_list[0]
        stocking_up_num += new_list[1]
        material_pre_num += new_list[2]
    # 首批到仓量 = 消耗量 - 当前库存 - 在途CG/FH - 在途调拨 - 在途PP1 - 在途PO1
    first_batch_num = max(first_batch_num - current_stock - transit_list[0], 0)
    first_batch_num = max(first_batch_num - transit_list[1] - transit_list[2], 0)
    print('新品首采-采购量:', first_batch_num / purchase_ratio)
    # 成品备货量 = 消耗量 - 当前库存 - 在途CG/FH - 在途调拨 - 在途PP1 - 在途PO1
    stocking_up_num = max(stocking_up_num - current_stock - transit_list[0], 0)
    stocking_up_num = max(stocking_up_num - transit_list[1] - transit_list[2], 0)
    print('新品备货-采购量:', stocking_up_num / purchase_ratio)
    # 原料备货量 = 消耗量 - 当前库存 - 在途CG/FH - 在途调拨 - 在途PP1 - 在途PO1
    material_pre_num = max(material_pre_num - current_stock - transit_list[0], 0)
    material_pre_num = max(material_pre_num - transit_list[1] - transit_list[2], 0)
    print('新品备料-采购量:', material_pre_num / purchase_ratio, '\n')


def get_plan_date(goods_id, wh_list):
    date_wh_dict = {}
    for wh_id in wh_list:
        scene_dict = order_strategy.get_new_scene(goods_id, wh_id, 1)
        for scene_val in scene_dict:
            plan_finish_date_list = scene_dict[scene_val]
            min_date = min(plan_finish_date_list)
            if min_date in date_wh_dict.keys():
                date_wh_dict[min_date].append(wh_id)
            else:
                date_wh_dict[min_date] = [wh_id]
    print(date_wh_dict)
    return date_wh_dict


def cul_goods_scene(goods_id, wh_id, new_flag):
    scene_dict = order_strategy.get_new_scene(goods_id, wh_id, new_flag)
    new_consume_list = [0, 0, 0]
    for scene_val in scene_dict:
        plan_finish_date_list = scene_dict[scene_val]
        if scene_val in ['1', '2', '3', '4']:
            # 新品备货参数取全国数据
            po_new_param = order_strategy.get_po_new_param(goods_id, 0)
            # 新品备货参数取仓库数据
            po_new_wh_param = order_strategy.get_po_new_wh_param(goods_id, wh_id, 0)
            consume_list = cul_po_new(
                goods_id, wh_id, scene_val,
                plan_finish_date_list,
                po_new_param + po_new_wh_param
            )
            print(consume_list)
            new_consume_list = list(map(lambda x, y: x + y, new_consume_list, consume_list))
        else:
            new_consume_list = list(map(lambda x, y: x + y, new_consume_list, [0, 0, 0]))
    return new_consume_list


def cul_plan_finish_date(min_date):
    # 首批计划完成日期 = min("计划上市日期") - 15天
    first_batch_plan_finish = lk_tools.datetool.cul_date(min_date, -15)
    print('新品首采-计划完成日期:', first_batch_plan_finish)
    # 备货计划完成日期 = min("计划上市日期") + 7天
    stocking_up_plan_finish = lk_tools.datetool.cul_date(min_date, 7)
    print('新品备货-计划完成日期:', stocking_up_plan_finish)
    # 备料计划完成日期 = min("计划上市日期") + 30天
    material_pre_plan_finish = lk_tools.datetool.cul_date(min_date, 30)
    print('新品备料-计划完成日期:', material_pre_plan_finish)


def cul_po_new(goods_id, wh_id, scene, date_list, po_new_param):
    # 判断货物大类是否食品
    large_class_flag = order_strategy.is_food_type(goods_id)
    print('货物大类是否食品:', large_class_flag)
    # 判断是否是中心仓
    is_cdc, is_cdc_model = order_strategy.get_central_wh(goods_id, wh_id)
    if is_cdc == 1 and is_cdc_model == 0:
        # 非中心仓
        central_type = 0
        print('非中心仓', is_cdc, is_cdc_model)
    else:
        # 中心仓
        central_type = 1
        print('中心仓', is_cdc, is_cdc_model)

    # 门店BP+RO
    shop_bp_ro = po_new_param[5]
    # 调整后BP-PO
    bp_po_adj = po_new_param[6]
    # 调整后WT
    wt_adj = po_new_param[7]
    # 仓库BP
    wh_bp = po_new_param[0]
    coa = po_new_param[1]
    lt = po_new_param[2]
    pt = po_new_param[3]
    mt = po_new_param[4]

    print('场景{}:'.format(scene), date_list)
    print('wh_bp: {}, shop_bp_ro: {}, 调整后BP-PO: {}, coa: {}, lt: {}, pt: {}, mt: {}'.format(
        wh_bp, shop_bp_ro, bp_po_adj, coa, lt, pt, mt)
    )

    # 计划上市日期
    left_plan_date, right_plan_date = order_strategy.new_scene_date(scene, date_list, large_class_flag, central_type)

    if central_type == 1:
        # 中心仓
        # 首批到仓周期 = 调整后BP-PO + max(coa, lt)
        first_batch_days = bp_po_adj + max(coa, lt)
        if large_class_flag:
            # 门店消耗量 = [计划上市日期, 计划上市日期+调整后BP-PO+max(coa, lt)]周期内【门店消耗】
            start_date = left_plan_date
            end_date = lk_tools.datetool.cul_date(right_plan_date, first_batch_days)
            shop_consume = order_strategy.cul_shop_consume(goods_id, wh_id, start_date, end_date)
            # 首批到仓量 = 门店消耗量
            first_batch_num = max(shop_consume, 0)

            # 门店消耗量 = [计划上市日期+首批到仓周期+1天, 计划上市日期+首批到仓周期+pt]周期内【门店消耗】
            start_date = lk_tools.datetool.cul_date(left_plan_date, first_batch_days + 1)
            end_date = lk_tools.datetool.cul_date(right_plan_date, first_batch_days + pt)
            shop_consume = order_strategy.cul_shop_consume(goods_id, wh_id, start_date, end_date)
            # 成品备货量 = 门店消耗量
            stocking_up_num = max(shop_consume, 0)

            # 门店消耗量 = [计划上市日期+首批到仓周期+pt+1天, 计划上市日期+首批到仓周期+pt+mt]周期内【门店消耗】
            start_date = lk_tools.datetool.cul_date(left_plan_date, first_batch_days + pt + 1)
            end_date = lk_tools.datetool.cul_date(right_plan_date, first_batch_days + pt + mt)
            shop_consume = order_strategy.cul_shop_consume(goods_id, wh_id, start_date, end_date)
            # 原料备货量 = 门店消耗量
            material_pre_num = max(shop_consume, 0)
        else:
            # 仓库出库量 = [计划上市日期-11天, 计划上市日期+仓库BP+max(coa, lt)]周期内【仓库出库】
            start_date = lk_tools.datetool.cul_date(left_plan_date, -11)
            end_date = lk_tools.datetool.cul_date(right_plan_date, wh_bp + max(coa, lt))
            wh_out = order_strategy.cul_wh_out_num(goods_id, wh_id, start_date, end_date)
            # 首批到仓量 = 仓库出库量
            first_batch_num = max(wh_out, 0)

            # 仓库出库量 = [计划上市日期+仓库BP+max(coa, lt)+1天, 计划上市日期+仓库BP+max(coa, lt)+pt]周期内【仓库出库】
            start_date = lk_tools.datetool.cul_date(left_plan_date, wh_bp + max(coa, lt) + 1)
            end_date = lk_tools.datetool.cul_date(right_plan_date, wh_bp + max(coa, lt) + pt)
            wh_out = order_strategy.cul_wh_out_num(goods_id, wh_id, start_date, end_date)
            # 成品备货量 = 仓库出库量
            stocking_up_num = max(wh_out, 0)

            # 仓库出库量 = [计划上市日期+仓库BP+max(coa, lt)+pt+1天, 计划上市日期+仓库BP+max(coa, lt)+pt+mt]周期内【仓库出库】
            start_date = lk_tools.datetool.cul_date(left_plan_date, wh_bp + max(coa, lt) + pt + 1)
            end_date = lk_tools.datetool.cul_date(right_plan_date, wh_bp + max(coa, lt) + pt + mt)
            wh_out = order_strategy.cul_wh_out_num(goods_id, wh_id, start_date, end_date)
            # 原料备货量 = 仓库出库量
            material_pre_num = max(wh_out, 0)
    else:
        # 非中心仓(是否中心仓:0, 是否中心仓模式:1)
        # 首批到仓周期 = 调整后BP-PO + max(coa, lt) + 调整后WT
        first_batch_days = bp_po_adj + max(coa, lt) + wt_adj
        if large_class_flag:
            # 门店消耗量 = [计划上市日期, 计划上市日期+调整后BP-PO+max(coa, lt)+调整后WT]周期内【门店消耗】
            start_date = left_plan_date
            end_date = lk_tools.datetool.cul_date(right_plan_date, first_batch_days)
            shop_consume = order_strategy.cul_shop_consume(goods_id, wh_id, start_date, end_date)
            # "首批到仓量" = 门店消耗量
            first_batch_num = max(shop_consume, 0)

            # 门店消耗量 = [计划上市日期, 计划上市日期+首批到仓周期+pt]周期内【门店消耗】
            start_date = left_plan_date
            end_date = lk_tools.datetool.cul_date(right_plan_date, first_batch_days + pt)
            shop_consume = order_strategy.cul_shop_consume(goods_id, wh_id, start_date, end_date)
            # "成品备货量" = max(门店消耗量 - 调整后首批到仓量, 0)
            stocking_up_num = max(shop_consume - first_batch_num, 0)

            # 门店消耗量 = [计划上市日期, 计划上市日期+首批到仓周期+pt+mt]周期内【门店消耗】
            start_date = left_plan_date
            end_date = lk_tools.datetool.cul_date(right_plan_date, first_batch_days + pt + mt)
            shop_consume = order_strategy.cul_shop_consume(goods_id, wh_id, start_date, end_date)
            # "原料备货量" = max(门店消耗量 - 调整后首批到仓量 - 调整后成品备货量, 0)
            material_pre_num = max(shop_consume - first_batch_num - stocking_up_num, 0)
        else:
            # 仓库出库量 = [计划上市日期-11天, 计划上市日期+仓库BP+max(coa, lt)+调整后WT]周期内【仓库出库】
            start_date = lk_tools.datetool.cul_date(left_plan_date, -11)
            end_date = lk_tools.datetool.cul_date(right_plan_date, wh_bp + max(coa, lt) + wt_adj)
            wh_out = order_strategy.cul_wh_out_num(goods_id, wh_id, start_date, end_date)
            # "首批到仓量" = 仓库出库量
            first_batch_num = max(wh_out, 0)

            # 仓库出库量 = [计划上市日期-11天, 计划上市日期+仓库BP+max(coa, lt)+pt]周期内【仓库出库】
            start_date = lk_tools.datetool.cul_date(left_plan_date, -11)
            end_date = lk_tools.datetool.cul_date(right_plan_date, wh_bp + max(coa, lt) + pt)
            wh_out = order_strategy.cul_wh_out_num(goods_id, wh_id, start_date, end_date)
            # "成品备货量" = max(仓库出库量 - 调整后首批到仓量, 0)
            stocking_up_num = max(wh_out - first_batch_num, 0)

            # 仓库出库量 = [计划上市日期-11天, 计划上市日期+仓库BP+max(coa, lt)+pt+mt]周期内【仓库出库】
            start_date = lk_tools.datetool.cul_date(left_plan_date, -11)
            end_date = lk_tools.datetool.cul_date(right_plan_date, wh_bp + max(coa, lt) + pt + mt)
            wh_out = order_strategy.cul_wh_out_num(goods_id, wh_id, start_date, end_date)
            # "原料备货量" = max(仓库出库量 - 调整后首批到仓量 - 调整后成品备货量, 0)
            material_pre_num = max(wh_out - first_batch_num - stocking_up_num, 0)
    return float(first_batch_num), float(stocking_up_num), float(material_pre_num)


if __name__ == '__main__':
    # JK纯牛奶(仓配\盘点) 货物id: 83625
    # 货物大类: 轻食 货物大类id: 70, 127
    # 供应商: 小奶狗  SC004990  1964
    # 供应商: 北京赢识  SC202917  629992
    '''
    货物规格id  供应商id  仓库id
    364752     1964:    [327193]
    364753     1964:    [245971, 245871]
    365908     629992:  [326932, 245770]
    '''
    get_national_flag(83625)
