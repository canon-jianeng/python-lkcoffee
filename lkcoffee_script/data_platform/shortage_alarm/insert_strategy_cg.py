
import yaml
import datetime

wh_dict = {'wh_dept_id': '326123', 'wh_code': 'WH00380', 'wh_name': '上海仓库'}
goods_dict = {'goods_id': '86948', 'goods_code': 'GS02336', 'goods_name': '巧克力味曲奇'}
spec_dict = {'spec_id': '3286995', 'spec_code': 'GS02336-01', 'spec_name': '瑞幸巧克力味曲奇25g*40包*9盒/箱'}
other_spec_dict = {'spec_id': '20816', 'spec_code': '', 'spec_name': '燕麦提子曲奇'}
supplier_list = {'supplier_no': 'SC004990', 'supplier_name': '厦门小奶狗贸易有限公司'}
cg_order_no = 'CG202305290004'


with open('./shortage_alarm_sql.yml', encoding='utf-8') as f:
    yml_data = yaml.load(f, Loader=yaml.CLoader)
    mysql_sql = yml_data['sql']
    mysql_conf = yml_data['mysql']

cg_finish_date = (datetime.date.today() + datetime.timedelta(days=3)).strftime("%Y-%m-%d")
arrival_warehouse_date = (datetime.date.today() + datetime.timedelta(days=2)).strftime("%Y-%m-%d")
wh_shortage_date = (datetime.date.today() + datetime.timedelta(days=8)).strftime("%Y-%m-%d %H:%M:%S")
now_time = datetime.datetime.now()
now_dt = now_time.strftime("%Y-%m-%d")
now_str = now_time.strftime("%Y-%m-%d %H:%M:%S")
batch_no = str(now_str).replace('-', '').replace(':', '').replace(' ', '')

sql_insert_cg = mysql_sql['insert_stock_shortage_cg_arrival_strategy']
sql_insert_cg_value = mysql_sql['val_stock_shortage_cg_arrival_strategy']

val_data = ''
val_str = sql_insert_cg_value.format(
    wh_dict['wh_dept_id'], wh_dict['wh_name'], goods_dict['goods_id'], goods_dict['goods_name'],
    spec_dict['spec_id'],  spec_dict['spec_code'], spec_dict['spec_name'], supplier_list['supplier_no'],
    supplier_list['supplier_name'], cg_order_no, cg_finish_date, arrival_warehouse_date,
    wh_shortage_date, other_spec_dict['spec_id'], other_spec_dict['spec_name'], now_dt, now_dt
)
val_data += val_str

insert_data = sql_insert_cg + '\n' + val_data

with open('../data/shortage_alarm/shortage_cg_arrival_strategy.txt', 'w', encoding='utf-8') as f:
    f.write(insert_data)
