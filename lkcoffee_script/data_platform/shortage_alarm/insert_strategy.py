
import yaml
import datetime

wh_dict = {'wh_dept_id': '326123', 'wh_code': 'WH00380', 'wh_name': '上海仓库'}
out_wh_dict = {'wh_dept_id': '226059', 'wh_code': 'WH00006', 'wh_name': '厦门仓库'}
goods_dict = {'goods_id': '86948', 'goods_code': 'GS02336', 'goods_name': '巧克力味曲奇'}
spec_dict = {'spec_id': '3286995', 'spec_code': 'GS02336-01', 'spec_name': '瑞幸巧克力味曲奇25g*40包*9盒/箱'}

# dt = 当天日期，策略推荐会显示对应数据
strategy_list = [
    # 1-新增调拨
    {'type': '1', 'business_type': '1', 'wh_address_id': 'NULL', 'wh_unit_id': 'NULL', 'git_quantity': '0'},
    # 2-新增CG
    {'type': '2', 'business_type': 'NULL', 'wh_address_id': '4613', 'wh_unit_id': '7699', 'git_quantity': '0'},
    # 3-新增PO
    {'type': '3', 'business_type': 'NULL', 'wh_address_id': 'NULL', 'wh_unit_id': 'NULL', 'git_quantity': '100'}
]


with open('./shortage_alarm_sql.yml', encoding='utf-8') as f:
    yml_data = yaml.load(f, Loader=yaml.CLoader)
    mysql_sql = yml_data['sql']
    mysql_conf = yml_data['mysql']

tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
now_time = datetime.datetime.now()
now_dt = now_time.strftime("%Y-%m-%d")
now_str = now_time.strftime("%Y-%m-%d %H:%M:%S")
batch_no = str(now_str).replace('-', '').replace(':', '').replace(' ', '')

sql_insert = mysql_sql['insert_ads_strategy_record']
sql_insert_value = mysql_sql['val_ads_strategy_record']

val_data = ''
finish_date = str((datetime.date.today() + datetime.timedelta(days=6)).strftime("%Y-%m-%d"))
for strategy in strategy_list:
    strategy_type = strategy['type']
    if strategy_type == '1':
        out_wh_name = out_wh_dict['wh_name']
        out_wh_id = out_wh_dict['wh_dept_id']
    elif strategy_type == '2':
        out_wh_name = 'NULL'
        out_wh_id = 'NULL'
    else:
        out_wh_name = 'NULL'
        out_wh_id = 'NULL'
    val_str = (sql_insert_value + ',\n').format(
        strategy_type, wh_dict['wh_dept_id'], goods_dict['goods_id'], spec_dict['spec_id'],
        strategy['wh_address_id'], goods_dict['goods_name'], wh_dict['wh_name'],
        out_wh_name, finish_date, out_wh_id, strategy['business_type'], strategy['git_quantity'],
        finish_date, now_str, now_dt, now_str, batch_no, strategy['wh_unit_id']
    )
    val_data += val_str

insert_data = sql_insert + '\n' + val_data


with open('../data/shortage_alarm/ads_strategy_record.txt', 'w', encoding='utf-8') as f:
    f.write(insert_data.replace("'NULL'", "NULL"))
