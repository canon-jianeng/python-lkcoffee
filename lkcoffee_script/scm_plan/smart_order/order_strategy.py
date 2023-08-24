
import yaml
import pymysql
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

# 使用 cursor() 方法创建一个游标对象 cursor
cursor = db_cooperation.cursor()

sql_shop_consume = mysql_sql['cooperation']['query_shop_consume']
sql_wh_consume = mysql_sql['cooperation']['query_wh_consume']


def is_central_wh(wh_id, goods_id):
    # 判断是否中心仓
    wh_flag = 0
    if wh_flag == 1:
        return True
    else:
        return False


def is_food_type(goods_id):
    # 判断 "商品大类" 是否为"食品"
    return True


def plan_finish_date_list():
    plan_date_list = []
    return plan_date_list


def new_goods_scene(scene, goods_id):
    # 新品场景
    date_list = []
    plan_date_list = sorted(plan_finish_date_list(), reverse=False)
    min_date = min(plan_date_list)
    max_date = max(plan_date_list)
    # 场景1: 同个货物只有一个上市计划
    if scene == 1:
        left_date, right_date = min_date
        date_list = [left_date, right_date]
    # 场景2: 同个货物有多个上市计划，且"计划上市日期"相同
    elif scene == 2:
        pass
    # 场景3: 同个货物有多个上市计划，且"计划上市日期"不同，且min("计划上市日期")和max("计划上市日期")的间隔 ≤ 11天（冷启动周期重合）
    elif scene == 3:
        left_date = min_date
        right_date = max_date
        date_list = [left_date, right_date]
    # 场景4: 同个货物有多个上市计划，且"计划上市日期"不同，且min("计划上市日期")和max("计划上市日期")的间隔 ＞ 11天（冷启动周期不重合）
    elif scene == 4:
        left_date, right_date = min_date
        date_list = [left_date, right_date]
    return date_list


def nearly_new_goods_cense(scene, goods_id):
    # 次新品的场景
    plan_date_list = sorted(plan_finish_date_list(), reverse=False)
    min_date = min(plan_date_list)
    # 场景1: 同个货物只有一个上市计划
    if scene == 1:
        plan_date = min_date
    # 场景2: 同个货物有多个上市计划，且"计划上市日期"相同
    elif scene == 2:
        plan_date = min_date
    # 场景3: 同个货物有多个上市计划，且"计划上市日期"不同，且min("计划上市日期")和max("计划上市日期")的间隔 ≤ 11天（冷启动周期重合）
    elif scene == 3:
        plan_date = min_date
    # 场景4: 同个货物有多个上市计划，且"计划上市日期"不同，且min("计划上市日期")和max("计划上市日期")的间隔 ＞ 11天（冷启动周期不重合）
    elif scene == 4:
        plan_date = min_date
    # 场景5: 同个货物有多个上市计划，且"计划上市日期"不同，且包含新品和次新品
    elif scene == 5:
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
