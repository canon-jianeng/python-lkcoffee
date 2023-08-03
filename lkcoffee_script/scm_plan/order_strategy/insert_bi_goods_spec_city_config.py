
import yaml
import pymysql
import random

wh_dept_list = [
    {'wh_name': '南安仓库', 'wh_dept_id': '327193', 'wh_code': 'WH00407', 'wh_id': '1274', 'city_id': '1675'},
    {'wh_name': 'ZJL压测仓库', 'wh_dept_id': '245971', 'wh_code': 'WH00305', 'wh_id': '758', 'city_id': '1689'},
    {'wh_name': '乌鲁木齐A仓库', 'wh_dept_id': '245871', 'wh_code': 'WH00302', 'wh_id': '755', 'city_id': '1374'},
    {'wh_name': 'xx仓库', 'wh_dept_id': '326932', 'wh_code': 'WH00393', 'wh_id': '1245', 'city_id': '1730'},
    {'wh_name': '武汉仓库', 'wh_dept_id': '326327', 'wh_code': 'WH00011', 'wh_id': '1441', 'city_id': '1303'},
    {'wh_name': '饮料城市仓-啦啦', 'wh_dept_id': '245770', 'wh_code': 'WH00297', 'wh_id': '750', 'city_id': '1519'},
]

goods_spec_list = [
    {'spec_name': '法布芮玫瑰味糖浆 1升*6瓶/箱', 'spec_id': '328428', 'spec_code': 'GS00042-02'},
    {'spec_name': 'xx奶糖-大白兔', 'spec_id': '365569', 'spec_code': 'GS01706-01'},
    {'spec_name': 'tong货物规格1', 'spec_id': '364936', 'spec_code': 'GS01311-01'},
    {'spec_name': 'xx小熊饼干1箱5提3个', 'spec_id': '365940', 'spec_code': ' GS01806-01'},
    {'spec_name': 'LM牛奶D_1箱3盒200毫升', 'spec_id': '365036', 'spec_code': 'GS01396-01'},
    {'spec_name': 'xx化学品-一箱3瓶（冷藏）', 'spec_id': '3284938', 'spec_code': 'GS02010-01'},
    {'spec_name': 'JK的POLO衫', 'spec_id': '301898', 'spec_code': 'GS01174-01 '},
    {'spec_name': 'QXwxn健康轻食', 'spec_id': '3284729', 'spec_code': 'GS01854-01'},
    {'spec_name': 'qq558888', 'spec_id': '3286716', 'spec_code': 'GS02104-02'}
]


with open('./strategy_sql.yml', encoding='utf-8') as f:
    yml_data = yaml.load(f, Loader=yaml.CLoader)
    mysql_sql = yml_data['sql']
    mysql_conf = yml_data['mysql']

sql_insert = mysql_sql['insert_bi_goods_spec_city_config']
sql_insert_value = mysql_sql['val_bi_goods_spec_city_config']
sql_query = mysql_sql['query_supplier_info']

# 打开数据库连接
db_purchase = pymysql.connect(
    host=mysql_conf['purchase']['host'],
    user=mysql_conf['purchase']['user'],
    password=mysql_conf['purchase']['pwd'],
    database=mysql_conf['purchase']['db'],
    port=mysql_conf['purchase']['port']
)

# 使用 cursor() 方法创建一个游标对象 cursor
cursor = db_purchase.cursor()


val_data = ''
for wh in wh_dept_list:
    for spec in goods_spec_list:
        # 查询供应商信息
        cursor.execute(sql_query.format(spec['spec_name'], wh['wh_name']))
        data = cursor.fetchall()
        if data == () or data == ((None, None, None),):
            supplier_id = ''
            supplier_code = ''
        else:
            supplier_id = data[0][0]
            supplier_code = data[0][1]
        # print(supplier_id, supplier_code, spec['spec_name'], wh['wh_name'])
        val_str = (sql_insert_value + ',\n').format(
            spec['spec_id'], wh['wh_id'], wh['wh_dept_id'], wh['city_id'],
            supplier_id, supplier_code, random.randint(0, 1)
        )
        val_data += val_str

insert_data = sql_insert + '\n' + val_data

with open('../data/order_strategy/bi_goods_spec_city_config.txt', 'w', encoding='utf-8') as f:
    f.write(insert_data)
