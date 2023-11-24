
import yaml
import datetime

wh_dict = {'wh_dept_id': '325140', 'wh_code': 'WH00345', 'wh_name': 'sy仓库01'}
out_wh_dict = {'wh_dept_id': '326123', 'wh_code': 'WH00380', 'wh_name': '上海仓库'}
goods_dict = {'goods_id': '87074', 'goods_code': 'GS02476', 'goods_name': '青青的货物项目专属'}
spec_dict = {'spec_id': '3287190', 'spec_code': 'GS02476-01', 'spec_name': '青青的规格项目专属'}

# dt = 当天日期，策略推荐会显示对应数据
strategy_list = [
    # 1-新增调拨
    {
        'type': '1', 'business_type': '1',
        'wh_address_id': 'NULL', 'wh_unit_id': 'NULL',
        'git_quantity': '0',
        'dly_amount': 12, 'dly_amount_quantity': 12, 'dly_use_ratio': 1, 'dly_unit_name': '米'
    },
    # 2-新增CG
    {
        'type': '2', 'business_type': 'NULL',
        # 库存单位id【wh_unit_id】和库存单位地址id【wh_address_id】需求匹配
        'wh_address_id': '26198', 'wh_unit_id': '6886',
        'git_quantity': '0',
        'dly_amount': 12, 'dly_amount_quantity': 12, 'dly_use_ratio': 1, 'dly_unit_name': '米'
    },
    # 3-新增PO
    {
        'type': '3', 'business_type': 'NULL',
        'wh_address_id': 'NULL', 'wh_unit_id': 'NULL',
        'git_quantity': '100',
        'dly_amount': 12, 'dly_amount_quantity': 12, 'dly_use_ratio': 1, 'dly_unit_name': '米'
    }
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
        out_wh_name, finish_date, strategy['dly_amount'], out_wh_id, strategy['business_type'],
        strategy['git_quantity'], finish_date, now_str, now_dt, now_str, batch_no,
        strategy['dly_amount_quantity'], strategy['dly_use_ratio'], strategy['dly_unit_name'], strategy['wh_unit_id']
    )
    val_data += val_str

insert_data = sql_insert + '\n' + val_data


with open('../data/shortage_alarm/ads_strategy_record.txt', 'w', encoding='utf-8') as f:
    f.write(insert_data.replace("'NULL'", "NULL"))
