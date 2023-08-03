
# import pymysql
# import yaml

"""
应退货款计算规则：
1、按照供应商+结算币种+结算项目类型+货物退款明细(结算状态为“待结算”) ，若为按货物加载费用项目仅保留所选货物退款明细，累加后获取应退金额
2、应退货款>0时，应退货款金额需要从应付货款费用项目金额上扣除，扣减步骤：
2.1）汇总扣款、返利、预付款金额进行等比均摊到每一项应付的费用项目上
2.2）按照退款明细所属小类的财务分类所关联的费用项目与应付费用项目进行匹配，扣减至0为止
2.3）若某一项费用项目退款>应付，费用项目扣减至0，退款超出部分汇总后等比均摊至所有非零项目
2.4）均摊过程中，如有尾差问题，按照原有尾差处理逻辑处理（直接汇总至最后一项）
"""


def cul_amount_sum(**param_dict):
    """
    计算金额的总和
    """
    amount_val = 0
    for param_key in param_dict:
        param_val = param_dict[param_key]
        if not isinstance(param_val, dict):
            raise Exception('必须是字典类型')
        amount_val += sum(param_val.values())
    return amount_val


def cul_amount_abs_sum(**param_dict):
    """
    计算金额绝对值的总和
    """
    amount_abs = 0
    for param_key in param_dict:
        param_val = param_dict[param_key]
        if not isinstance(param_val, dict):
            raise Exception('必须是字典类型')
        param_list = list(param_val.values())
        for amount_val in param_list:
            amount_abs += abs(amount_val)
    return amount_abs


def proportional_allocation(total, item_number, **param_dict):
    """
    等比分摊
    """
    for param_key in param_dict:
        param_val = param_dict[param_key]
        if not isinstance(param_val, dict):
            raise Exception('必须是字典类型')
        for param_val_key in param_val:
            item_dict[param_key][param_val_key] = total / item_number
    return param_dict


def prorate_average(total, prorate_total, record=False, **param_dict):
    """
    等比均摊
    """
    zero_val = 0
    negative_val = 0
    item_number = 0
    for param_key in param_dict:
        param_val = param_dict[param_key]
        if not isinstance(param_val, dict):
            raise Exception('必须是字典类型')
        for param_val_key in param_val:
            value = param_val[param_val_key]
            average_val = value - abs(value) / total * prorate_total
            if record:
                if average_val != 0:
                    zero_val = 1
                if average_val > 0 or average_val == 0:
                    negative_val = 1
                item_number += 1
            item_dict[param_key][param_val_key] = average_val
    if record:
        return param_dict, item_number, zero_val, negative_val
    else:
        return param_dict


# 应付货款
payment_amount = {'周边产品': {'sy财务分类01': 360, 'sy财务分类02': 225}, '运营设备采购': {'sy财务分类03': 300, '咖啡豆': 200}}

# 应退货款
refund_amount = {'周边产品': {'sy财务分类01': 50, 'sy财务分类02': 890}}

# 应扣罚款
fine_amount = 13.5

# 应扣返利
rebate_amount = 25

# 预付货款
advance_amount = 28

# 服务费用
service_fees = {'装修费': {'装修费': 3.7}}

item_dict = {**payment_amount, **service_fees}
print('费用项目：\n' + str(item_dict))

# 应扣金额 = 应扣罚款+返利+预付货款
deduction_amout = fine_amount + rebate_amount + advance_amount
print('\n应扣金额(应扣罚款、返利、预付货款）：' + str(deduction_amout))

# 应付金额 = 应付货款+服务费
pay_amount = cul_amount_sum(**payment_amount)
print('应付货款：' + str(pay_amount))
total_amount = cul_amount_sum(**item_dict)
print('应付金额（应付货款+服务费）：' + str(total_amount))

# 退款总数
refund_dict = {}
for key in refund_amount:
    refund_val = sum(refund_amount[key].values())
    refund_dict[key] = refund_val
refund_total = sum(refund_dict.values())
print('应退货款：' + str(refund_dict))
print('应退货款：' + str(refund_total))
print('结算金额：' + str(total_amount-refund_total-deduction_amout))

# 1.等比均摊扣减(应扣罚款、返利预付款)
# 费用项目数: item_num
item_dict, item_num, zero_flag, negative_flag = prorate_average(
    total_amount, deduction_amout, record=True, **item_dict
)
print('\n一次分摊后（每个费用项-等比均摊应扣金额）费用项目：\n' + str(item_dict))

# 第一次等比均摊后的付款总数（应付货款+服务费）
total_amount_two = cul_amount_abs_sum(**item_dict)


if zero_flag == 0:
    # 第一次等比均摊都为0, 退款金额等比分摊
    item_dict = proportional_allocation(-refund_total, item_num, **item_dict)
elif negative_flag == 0:
    print('二次分摊付款总金额：' + str(total_amount_two))
    # 第一次等比均摊都为负数, 再次等比均摊
    prorate_average(total_amount_two, refund_total, **item_dict)
else:
    # 按照退款明细所属小类的财务分类所关联的费用项目与应付费用项目进行匹配，扣减至0为止
    refund_list = refund_dict.keys()
    two_share_equally = {}
    refund_total = 0
    for item_key in item_dict:
        val_dict = item_dict[item_key]
        val_dict_len = len(val_dict)
        if item_key in refund_list:
            refund_abs = abs(refund_dict[item_key])
            for i, item_val in enumerate(val_dict):
                # 若某一项费用项目退款>应付，费用项目扣减至0
                if refund_abs > 0:
                    val = val_dict[item_val]
                    num = abs(val) - refund_abs
                    if num > 0:
                        item_dict[item_key][item_val] = num
                        refund_abs = 0
                        two_share_equally.update({item_key: {item_val: num}})
                    else:
                        # 退款 > 应付款
                        item_dict[item_key][item_val] = 0
                        refund_abs = abs(num)
                        if i == val_dict_len - 1:
                            refund_total += refund_abs
        else:
            two_share_equally.update({item_key: item_dict[item_key]})
    print("\n付款金额不为0的费用项目：\n" + str(two_share_equally))
    # 退款超出部分汇总后等比均摊至所有非零项目
    if refund_total > 0:
        print('剩余退款金额：' + str(refund_total))
        # 一次分摊后应付货款不为0的费用项总金额
        share_equally_amount = cul_amount_abs_sum(**two_share_equally)
        print('二次分摊付款总金额：' + str(share_equally_amount))
        item_dict.update(prorate_average(share_equally_amount, refund_total, **two_share_equally))

print('\n最终费用项目：\n' + str(item_dict))
