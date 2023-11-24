
import lk_tools
import order_strategy


def cul_cg_amount(goods_id):
    # 仓库：全国所有"已完善"，且非"已停业"的城市仓
    wh_list = order_strategy.get_wh_list()
    spec_list = order_strategy.get_goods_spec_list(goods_id)
    spec_wh_list = []
    for spec_id in spec_list:
        # 获取一个仓库下的货物规格id和可替换货物规格【满足同一个货物】
        spec_wh_list += order_strategy.get_spec_list(goods_id, spec_id, wh_list)
        print('货物规格:', spec_wh_list)
        purchase_ratio = 0
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
        transit_cc = order_strategy.cul_transit_amount(6, spec_wh_list)
        print('在途cc总数量:', transit_cc)
        transit_amount = transit_cg + transit_fh + transit_trs
        # 门店货物理论可用库存
        shop_use_stock = 0
        cg_amount = cul_goods_scene(goods_id, wh_id, 1)
        # 新品CG需求量 = 消耗量 - 当前库存 - 门店货物理论可用库存 - 在途配货 - 在途CG/FH - 在途CC - 在途调拨
        cg_amount = max(cg_amount - current_stock - shop_use_stock - transit_amount, 0)
        print('新品CG需求量:', cg_amount)
        print('新品CG需求量(采购单位):', cg_amount / purchase_ratio)


def cul_goods_scene(goods_id, wh_id, new_flag):
    scene_dict = order_strategy.get_new_scene(goods_id, wh_id, new_flag)
    new_consume = 0
    for scene_val in scene_dict:
        plan_finish_date_list = scene_dict[scene_val]
        # 新品备货参数取全国数据
        po_new_param = order_strategy.get_po_new_param(goods_id, 0)
        # 新品备货参数取仓库数据
        po_new_wh_param = order_strategy.get_po_new_wh_param(goods_id, wh_id, 0)
        consume = cul_cg_new(
            goods_id, wh_id, scene_val,
            plan_finish_date_list,
            po_new_param + po_new_wh_param
        )
        new_consume += consume
    return new_consume


def cul_plan_finish_date(min_date):
    # 计划完成日期 = min("计划上市日期") - 15天
    cg_new_plan_finish = lk_tools.datetool.cul_date(min_date, -15)


def cul_cg_new(goods_id, wh_id, scene, plan_finish_date_list: list, po_new_param):
    # 判断货物大类是否食品
    food_flag = order_strategy.is_food_type(goods_id)
    print('货物大类是否食品:', food_flag)
    # 判断是否是中心仓
    is_cdc, is_cdc_model = order_strategy.get_central_wh(goods_id, wh_id)
    if is_cdc == 0 and is_cdc_model == 1:
        # 非中心仓(是否中心仓:0, 是否中心仓模式:1)
        central_flag = False
        print('非中心仓', '是否中心仓:{}'.format(is_cdc), '是否中心仓模式:{}'.format(is_cdc_model))
    else:
        # 中心仓
        central_flag = True
        print('中心仓', '是否中心仓:{}'.format(is_cdc), '是否中心仓模式:{}'.format(is_cdc_model))

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

    print('场景{}:'.format(scene), plan_finish_date_list)
    print('wh_bp: {}, shop_bp_ro: {}, 调整后BP-PO: {}, coa: {}, lt: {}, pt: {}, mt: {}'.format(
        wh_bp, shop_bp_ro, bp_po_adj, coa, lt, pt, mt)
    )

    if central_flag:
        # 中心仓
        if food_flag:
            if scene == '1' or scene == '2':
                # 首批到仓周期 = 调整后BP-PO + max(coa, lt)
                # 首批到仓量 = [计划上市日期, 计划上市日期+BP-PO+max(coa, lt)]周期内【门店消耗】
                start_date = plan_finish_date_list[0]
                end_date = lk_tools.datetool.cul_date(plan_finish_date_list[0], bp_po_adj + max(coa, lt))
                shop_consume = order_strategy.cul_shop_consume(goods_id, wh_id, start_date, end_date)
                cg_new_num = max(shop_consume, 0)
                print(start_date, end_date)
            elif scene == '3':
                # 首批到仓量 = [ max(计划上市日期), max(计划上市日期)+BP-PO+max(COA, LT)] 周期内【门店消耗】
                start_date = max(plan_finish_date_list)
                end_date = lk_tools.datetool.cul_date(max(plan_finish_date_list), bp_po_adj + max(coa, lt))
                shop_consume = order_strategy.cul_shop_consume(goods_id, wh_id, start_date, end_date)
                cg_new_num = max(shop_consume, 0)
                print(start_date, end_date)
            elif scene == '4':
                # 首批到仓量 = [ min(计划上市日期), min(计划上市日期)+BP-PO+max(COA, LT)] 周期内【门店消耗】
                start_date = min(plan_finish_date_list)
                end_date = lk_tools.datetool.cul_date(min(plan_finish_date_list), bp_po_adj + max(coa, lt))
                shop_consume = order_strategy.cul_shop_consume(goods_id, wh_id, start_date, end_date)
                cg_new_num = max(shop_consume, 0)
                print(start_date, end_date)
            else:
                cg_new_num = 0
        else:
            if scene == '1' or scene == '2':
                # 首批到仓量 = [计划上市日期-11天, 计划上市日期+仓库BP+max(coa, lt)]周期内【仓库出库】
                start_date = lk_tools.datetool.cul_date(plan_finish_date_list[0], -11)
                end_date = lk_tools.datetool.cul_date(plan_finish_date_list[0], wh_bp + max(coa, lt))
                wh_out = order_strategy.cul_wh_out_num(goods_id, wh_id, start_date, end_date)
                cg_new_num = max(wh_out, 0)
                print(start_date, end_date)
            elif scene == '3':
                # 首批到仓量 = [ max(计划上市日期)-11天, max(计划上市日期)+仓库BP+max(COA, LT)] 周期内【仓库出库】
                start_date = lk_tools.datetool.cul_date(max(plan_finish_date_list), -11)
                end_date = lk_tools.datetool.cul_date(max(plan_finish_date_list), wh_bp + max(coa, lt))
                wh_out = order_strategy.cul_wh_out_num(goods_id, wh_id, start_date, end_date)
                cg_new_num = max(wh_out, 0)
                print(start_date, end_date)
            elif scene == '4':
                # 首批到仓量 = [ min(计划上市日期)-11天, min(计划上市日期)+仓库BP+max(COA, LT)] 周期内【仓库出库】
                start_date = lk_tools.datetool.cul_date(min(plan_finish_date_list), -11)
                end_date = lk_tools.datetool.cul_date(min(plan_finish_date_list), wh_bp + max(coa, lt))
                wh_out = order_strategy.cul_wh_out_num(goods_id, wh_id, start_date, end_date)
                cg_new_num = max(wh_out, 0)
                print(start_date, end_date)
            else:
                cg_new_num = 0
    else:
        # 非中心仓
        if food_flag:
            if scene == '1' or scene == '2':
                # 首批到仓周期 = 调整后BP-PO + max(coa, lt) + 调整后WT
                # 首批到仓量 = [计划上市日期, 计划上市日期+调整后BP-PO+max(coa, lt)+调整后WT]周期内【门店消耗】
                start_date = plan_finish_date_list[0]
                end_date = lk_tools.datetool.cul_date(plan_finish_date_list[0], bp_po_adj + max(coa, lt) + wt_adj)
                shop_consume = order_strategy.cul_shop_consume(goods_id, wh_id, start_date, end_date)
                cg_new_num = max(shop_consume, 0)
                print(start_date, end_date)
            elif scene == '3':
                # 首批到仓量 = [ min(计划上市日期), max(计划上市日期)+BP-PO+max(COA, LT)+调整后WT] 周期内【门店消耗】
                start_date = min(plan_finish_date_list)
                end_date = lk_tools.datetool.cul_date(max(plan_finish_date_list), bp_po_adj + max(coa, lt) + wt_adj)
                shop_consume = order_strategy.cul_shop_consume(goods_id, wh_id, start_date, end_date)
                cg_new_num = max(shop_consume, 0)
                print(start_date, end_date)
            elif scene == '4':
                # 首批到仓量 = [ min(计划上市日期), min(计划上市日期)+BP-PO+max(COA, LT)+调整后WT] 周期内【门店消耗】
                start_date = min(plan_finish_date_list)
                end_date = lk_tools.datetool.cul_date(min(plan_finish_date_list), bp_po_adj + max(coa, lt) + wt_adj)
                shop_consume = order_strategy.cul_shop_consume(goods_id, wh_id, start_date, end_date)
                cg_new_num = max(shop_consume, 0)
                print(start_date, end_date)
            else:
                cg_new_num = 0
        else:
            if scene == '1' or scene == '2':
                # 首批到仓量 = [计划上市日期-11天, 计划上市日期+仓库BP+max(coa, lt)+调整后WT]周期内【仓库出库】
                start_date = lk_tools.datetool.cul_date(plan_finish_date_list[0], -11)
                end_date = lk_tools.datetool.cul_date(plan_finish_date_list[0], wh_bp + max(coa, lt) + wt_adj)
                wh_out = order_strategy.cul_wh_out_num(goods_id, wh_id, start_date, end_date)
                cg_new_num = max(wh_out, 0)
                print(start_date, end_date)
            elif scene == '3':
                # 首批到仓量 = [ min(计划上市日期)-11天, max(计划上市日期)+仓库BP+max(COA, LT)+调整后WT] 周期内【仓库出库】
                start_date = lk_tools.datetool.cul_date(min(plan_finish_date_list), -11)
                end_date = lk_tools.datetool.cul_date(max(plan_finish_date_list), wh_bp + max(coa, lt) + wt_adj)
                wh_out = order_strategy.cul_wh_out_num(goods_id, wh_id, start_date, end_date)
                cg_new_num = max(wh_out, 0)
                print(start_date, end_date)
            elif scene == '4':
                # 新品CG需求量 = [ min(计划上市日期)-11天, min(计划上市日期)+仓库BP+max(COA, LT)+调整后WT] 周期内【仓库出库】
                start_date = lk_tools.datetool.cul_date(min(plan_finish_date_list), -11)
                end_date = lk_tools.datetool.cul_date(min(plan_finish_date_list), wh_bp + max(coa, lt) + wt_adj)
                wh_out = order_strategy.cul_wh_out_num(goods_id, wh_id, start_date, end_date)
                cg_new_num = max(wh_out, 0)
                print(start_date, end_date)
            else:
                cg_new_num = 0
    return float(cg_new_num)


if __name__ == '__main__':
    # JK纯牛奶(仓配\盘点) 货物id: 83625
    # 货物大类: 轻食 货物大类id: 70, 127
    # 供应商: 小奶狗  SC004990  1964
    # 供应商: 北京赢识  SC202917  629992
    '''
    货物规格名称                         货物规格id  供应商id  仓库id
    JK伊利纯牛奶500mL*12盒/箱（仓配/盘点） 364752     1964     [327193]
    JK蒙牛纯牛奶1L*12盒/箱（仓配/盘点）    364753     1964     [245971, 245871]
    JK光明纯牛奶1L*12盒/箱（仓配/盘点）    365908     629992   [326932, 245770]
    '''
    cul_cg_amount(83625)
