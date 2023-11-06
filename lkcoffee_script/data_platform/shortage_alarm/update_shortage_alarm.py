
import yaml
import pymysql

"""
需要修改供应商数据:
UPDATE t_dm_wh_stock_shortage_alarm SET supplier_no='SC004990', supplier_name='厦门小奶狗贸易有限公司';
"""

old_good_id = '11685'
old_spec_id = '26357'
old_wh_name = '南昌仓库'
old_wh_dept_id = '326921'

new_wh_dict = {'wh_dept_id': '326123', 'wh_code': 'WH00380', 'wh_name': '上海仓库'}
new_goods_dict = {'goods_id': '86948', 'goods_code': 'GS02336', 'goods_name': '巧克力味曲奇'}
new_spec_dict = {'spec_id': '3286995', 'spec_code': 'GS02336-01', 'spec_name': '瑞幸巧克力味曲奇25g*40包*9盒/箱'}

with open('./shortage_alarm_sql.yml', encoding='utf-8') as f:
    yml_data = yaml.load(f, Loader=yaml.CLoader)
    mysql_sql = yml_data['sql']
    mysql_conf = yml_data['mysql']

sql_update_shortage_alarm = mysql_sql['update_dm_wh_stock_shortage_alarm']
sql_update_goods_stock_detail = mysql_sql['update_dataplatform_control_tower_goods_stock_detail']
sql_update_spec_stock_detail = mysql_sql['update_dataplatform_control_tower_spec_stock_detail']

# 打开数据库连接
db_dataplatform = pymysql.connect(
    host=mysql_conf['dataplatform']['host'],
    user=mysql_conf['dataplatform']['user'],
    password=mysql_conf['dataplatform']['pwd'],
    database=mysql_conf['dataplatform']['db'],
    port=mysql_conf['dataplatform']['port']
)

# 使用 cursor() 方法创建一个游标对象 cursor
cursor = db_dataplatform.cursor()
# 更新断仓预警数据为测试数据
# 仓库断仓预警
cursor.execute(
    sql_update_shortage_alarm.format(
        new_wh_dict['wh_dept_id'], new_wh_dict['wh_code'], new_wh_dict['wh_name'],
        new_goods_dict['goods_id'], new_goods_dict['goods_code'], new_goods_dict['goods_name'],
        new_spec_dict['spec_id'], new_spec_dict['spec_code'], new_spec_dict['spec_name'],
        old_good_id, old_wh_dept_id
    )
)

# 控制塔-货物
cursor.execute(
    sql_update_goods_stock_detail.format(
        new_wh_dict['wh_dept_id'], new_wh_dict['wh_name'],
        new_goods_dict['goods_id'], new_goods_dict['goods_name'],
        old_good_id, old_wh_dept_id
    )
)

# 控制塔-货物规格
cursor.execute(
    sql_update_spec_stock_detail.format(
        new_wh_dict['wh_dept_id'], new_goods_dict['goods_id'],
        new_spec_dict['spec_id'], new_spec_dict['spec_name'],
        old_spec_id, old_wh_dept_id
    )
)

# db_dataplatform.commit()
