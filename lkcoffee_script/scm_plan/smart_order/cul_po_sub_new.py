

scene = 1
central_type = 1

if central_type == 1:
    # 需求量 = [当前日, 调整后BP-PO+调整后VLT+调整后SS]周期内【需求量】
    # 次新品补单量 = 需求量 - 当前库存 - 在途配货 - 在途CG/FH - 在途调拨
    nearly_new_num = 0
else:
    # 需求量 = [当前日, 调整后BP-PO+调整后VLT+调整后SS+调整后WT]周期内【需求量】
    # 次新品补单量 = 需求量 - 当前库存 - 在途配货 - 在途CG/FH - 在途调拨
    nearly_new_num = 0

if scene == 1 or scene == 2 or scene == 3 or scene == 4:
    # 计划完成日期 = 当前日 + 调整后BP-PO + 调整后VLT
    plan_finish_date = ''
elif scene == 5:
    # 计划完成日期 = min(当前日+调整后BP-PO+调整后VLT, min("计划上市日期")-15天)
    plan_finish_date = ''
