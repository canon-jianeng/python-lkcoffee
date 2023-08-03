
import yaml
import pymysql


with open('./predictive_sql.yml', encoding='utf-8') as f:
    yml_data = yaml.load(f, Loader=yaml.CLoader)
    mysql_sql = yml_data['get_sale_shop']
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

sql_actual_shop = mysql_sql['query_actual_shop_num']
sql_pred_shop = mysql_sql['query_pred_shop_num']
sql_open_shop_definite = mysql_sql['query_sale_shop_definite']
sql_open_shop_v0 = mysql_sql['query_sale_shop_v0']


def get_version(year_val):
    # 判断是否存在确定版
    cursor.execute(sql_open_shop_definite.format(year_val))
    definite_data = cursor.fetchall()
    if len(definite_data) > 0:
        version_id = definite_data[0][0]
    else:
        # 不存在确定版, 获取 v0 版本
        cursor.execute(sql_open_shop_v0.format(year_val))
        version_data = cursor.fetchall()
        version_id = version_data[0][0]
    return version_id


def get_actual_sale_shop(wh_id, commodity_id, date_val):
    # 先获取新品的售卖门店数
    cursor.execute(sql_actual_shop.format(wh_id, commodity_id, 1, date_val))
    data = cursor.fetchall()
    if len(data) == 0:
        # 新品为空时, 查询常规品的售卖门店数
        cursor.execute(sql_actual_shop.format(wh_id, commodity_id, 2, date_val))
        data = cursor.fetchall()
        if len(data) == 0:
            sale_shop_num = 0
        else:
            sale_shop_num = data[0][0]
    else:
        sale_shop_num = data[0][0]
    return sale_shop_num


def get_pred_sale_shop(wh_id, commodity_id, date_val):
    # 获取版本id
    version_id = get_version(date_val.split('-')[0])
    # 先获取新品的售卖门店数
    cursor.execute(sql_pred_shop.format(version_id, wh_id, commodity_id, 1, date_val))
    data = cursor.fetchall()
    if len(data) == 0:
        # 新品为空时, 查询常规品的售卖门店数
        cursor.execute(sql_pred_shop.format(version_id, wh_id, commodity_id, 2, date_val))
        data = cursor.fetchall()
        if len(data) == 0:
            pred_shop_num = 0
        else:
            pred_shop_num = data[0][0]
    else:
        pred_shop_num = data[0][0]
    return pred_shop_num


if __name__ == '__main__':
    pass
