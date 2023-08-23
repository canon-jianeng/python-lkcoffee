
from lkcoffee_script import lk_tools
from order_strategy import cul_shop_consume, cul_wh_out_num, new_goods_scene


# 仓库BP
wh_bp = 0

# 门店BP+RO
shop_bp_ro = 0

COA = 0
LT = 0
PT = 0
MT = 0

goods_id = 4488

# 当前库存
current_stock = 0

# BP-PO
bp_po_adj = 0
wt_adj = 0

transit_amount = 0

scene = 1
food_type = True
central_type = 1
# 调整后首批到仓量
first_batch_adj_num = 0
# 调整后成品备货量
stocking_up_adj_num = 0

# 计划上市日期
left_plan_date, right_plan_date = new_goods_scene(scene, goods_id)
# 首批计划完成日期 = min("计划上市日期") - 15天
first_batch_plan_finish = lk_tools.datetool.cul_date(left_plan_date, -15)
# 备货计划完成日期 = min("计划上市日期") + 7天
stocking_up_plan_finish = lk_tools.datetool.cul_date(left_plan_date, 7)
# 备料计划完成日期 = min("计划上市日期") + 30天
material_pre_plan_finish = lk_tools.datetool.cul_date(left_plan_date, 30)

if central_type == 1:
    # 中心仓
    # 首批到仓周期 = 调整后BP-PO + max(COA, LT)
    first_batch_days = bp_po_adj + max(COA, LT)
    if food_type:
        # 门店消耗量 = [计划上市日期, 计划上市日期+调整后BP-PO+max(COA, LT)]周期内【门店消耗】
        start_date = left_plan_date
        end_date = lk_tools.datetool.cul_date(right_plan_date, first_batch_days)
        shop_consume = cul_shop_consume(start_date, end_date)
        # 首批到仓量 = 门店消耗量 - 当前库存 - 在途CG/FH - 在途调拨
        first_batch_num = shop_consume - current_stock - transit_amount

        # 门店消耗量 = [计划上市日期+首批到仓周期+1天, 计划上市日期+首批到仓周期+PT]周期内【门店消耗】
        start_date = lk_tools.datetool.cul_date(left_plan_date, first_batch_days + 1)
        end_date = lk_tools.datetool.cul_date(right_plan_date, first_batch_days + PT)
        shop_consume = cul_shop_consume(start_date, end_date)
        # 成品备货量 = 门店消耗量 - 当前库存 - 在途CG/FH - 在途调拨
        stocking_up_num = shop_consume - current_stock - transit_amount

        # 门店消耗量 = [计划上市日期+首批到仓周期+PT+1天, 计划上市日期+首批到仓周期+PT+MT]周期内【门店消耗】
        start_date = lk_tools.datetool.cul_date(left_plan_date, first_batch_days + PT + 1)
        end_date = lk_tools.datetool.cul_date(right_plan_date, first_batch_days + PT + MT)
        shop_consume = cul_shop_consume(start_date, end_date)
        # 原料备货量 = 门店消耗量 - 当前库存 - 在途CG/FH - 在途调拨
        material_pre_num = shop_consume - current_stock - transit_amount
    else:
        # 仓库出库量 = [计划上市日期-11天, 计划上市日期+仓库BP+max(COA, LT)]周期内【仓库出库】
        start_date = lk_tools.datetool.cul_date(left_plan_date, -11)
        end_date = lk_tools.datetool.cul_date(right_plan_date, wh_bp + max(COA, LT))
        wh_out = cul_wh_out_num(start_date, end_date)
        # 首批到仓量 = 仓库出库量 - 当前库存 - 在途CG/FH - 在途调拨
        first_batch_num = wh_out - current_stock - transit_amount

        # 仓库出库量 = [计划上市日期+仓库BP+max(COA, LT)+1天, 计划上市日期+仓库BP+max(COA, LT)+PT]周期内【仓库出库】
        start_date = lk_tools.datetool.cul_date(left_plan_date, wh_bp + max(COA, LT) + 1)
        end_date = lk_tools.datetool.cul_date(right_plan_date, wh_bp + max(COA, LT) + PT)
        wh_out = cul_wh_out_num(start_date, end_date)
        # 成品备货量 = 仓库出库量 - 当前库存 - 在途CG/FH - 在途调拨
        stocking_up_num = wh_out - current_stock - transit_amount

        # 仓库出库量 = [计划上市日期+仓库BP+max(COA, LT)+PT+1天, 计划上市日期+仓库BP+max(COA, LT)+PT+MT]周期内【仓库出库】
        start_date = lk_tools.datetool.cul_date(left_plan_date, wh_bp + max(COA, LT) + PT + 1)
        end_date = lk_tools.datetool.cul_date(right_plan_date, wh_bp + max(COA, LT) + PT + MT)
        wh_out = cul_wh_out_num(start_date, end_date)
        # 原料备货量 = 仓库出库量 - 当前库存 - 在途CG/FH - 在途调拨
        material_pre_num = wh_out - current_stock - transit_amount
else:
    # 非中心仓
    # 首批到仓周期 = 调整后BP-PO + max(COA, LT) + 调整后WT
    first_batch_days = bp_po_adj + max(COA, LT) + wt_adj
    if food_type:
        # 门店消耗量 = [计划上市日期, 计划上市日期+调整后BP-PO+max(COA, LT)+调整后WT]周期内【门店消耗】
        start_date = left_plan_date
        end_date = lk_tools.datetool.cul_date(right_plan_date, first_batch_days)
        shop_consume = cul_shop_consume(start_date, end_date)
        # "首批到仓量" = 门店消耗量 - 当前库存 - 在途CG/FH - 在途调拨
        first_batch_num = shop_consume - current_stock - transit_amount

        # 门店消耗量 = [计划上市日期, 计划上市日期+首批到仓周期+PT]周期内【门店消耗】
        start_date = left_plan_date
        end_date = lk_tools.datetool.cul_date(right_plan_date, first_batch_days + PT)
        shop_consume = cul_shop_consume(start_date, end_date)
        # "成品备货量" = max(门店消耗量 - 调整后首批到仓量 - 当前库存 - 在途CG/FH - 在途调拨, 0)
        stocking_up_num = max(shop_consume - first_batch_adj_num - current_stock - transit_amount, 0)

        # 门店消耗量 = [计划上市日期, 计划上市日期+首批到仓周期+PT+MT]周期内【门店消耗】
        start_date = left_plan_date
        end_date = lk_tools.datetool.cul_date(right_plan_date, first_batch_days + PT + MT)
        shop_consume = cul_shop_consume(start_date, end_date)
        # "原料备货量" = max(门店消耗量 - 调整后首批到仓量 - 调整后成品备货量 - 当前库存 - 在途CG/FH - 在途调拨, 0)
        material_pre_num = max(
            shop_consume - first_batch_adj_num - stocking_up_adj_num - current_stock - transit_amount, 0
        )
    else:
        # 仓库出库量 = [计划上市日期-11天, 计划上市日期+仓库BP+max(COA, LT)+调整后WT]周期内【仓库出库】
        start_date = lk_tools.datetool.cul_date(left_plan_date, -11)
        end_date = lk_tools.datetool.cul_date(right_plan_date, wh_bp + max(COA, LT) + wt_adj)
        wh_out = cul_wh_out_num(start_date, end_date)
        # "首批到仓量" = 仓库出库量 - 当前库存 - 在途CG/FH - 在途调拨
        first_batch_num = wh_out - current_stock - transit_amount

        # 仓库出库量 = [计划上市日期-11天, 计划上市日期+仓库BP+max(COA, LT)+PT]周期内【仓库出库】
        start_date = lk_tools.datetool.cul_date(left_plan_date, -11)
        end_date = lk_tools.datetool.cul_date(right_plan_date, wh_bp + max(COA, LT) + PT)
        wh_out = cul_wh_out_num(start_date, end_date)
        # "成品备货量" = max(仓库出库量 - 调整后首批到仓量 - 当前库存 - 在途CG/FH - 在途调拨, 0)
        stocking_up_num = max(wh_out - first_batch_adj_num - current_stock - transit_amount, 0)

        # 仓库出库量 = [计划上市日期-11天, 计划上市日期+仓库BP+max(COA, LT)+PT+MT]周期内【仓库出库】
        start_date = lk_tools.datetool.cul_date(left_plan_date, -11)
        end_date = lk_tools.datetool.cul_date(right_plan_date, wh_bp + max(COA, LT) + PT + MT)
        wh_out = cul_wh_out_num(start_date, end_date)
        # "原料备货量" = max(仓库出库量 - 调整后首批到仓量 - 调整后成品备货量 - 当前库存 - 在途CG/FH - 在途调拨, 0)
        material_pre_num = max(
            wh_out - first_batch_adj_num - stocking_up_adj_num - current_stock - transit_amount, 0
        )
