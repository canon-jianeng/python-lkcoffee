
import time
from datetime import date, datetime, timedelta
import pymysql
import yaml

"""



"""


def cul_day_detail(flag=1):
    if flag == 1:
        # 获取日纬度的商品明细
        pass
    else:
        # 周/月纬度 -> 日纬度
        pass
        # 商品汇总 -> 商品明细
    return


def cul_day_total(flag=1):
    if flag == 1:
        # 商品明细 -> 商品汇总
        pass
    else:
        # 商品汇总 -> 商品明细
        pass


def cul_week_detail(flag=1):
    if flag == 1:
        # 日维度 -> 周纬度
        day_detial = cul_day_detail()
        pass
    else:
        # 周纬度 -> 日纬度
        pass
    return


def cul_week_total(flag=1):
    if flag == 1:
        # 商品明细 -> 商品汇总
        week_detail = cul_week_detail()
        pass
    else:
        # 商品汇总 -> 商品明细
        pass


def cul_month_detail(flag=1):
    if flag == 1:
        # 日维度 -> 月纬度
        pass
    else:
        # 月纬度 -> 日纬度
        pass
    return


def cul_month_total(flag=1):
    if flag == 1:
        # 商品明细 -> 商品汇总
        pass
    else:
        # 商品汇总 -> 商品明细
        pass

