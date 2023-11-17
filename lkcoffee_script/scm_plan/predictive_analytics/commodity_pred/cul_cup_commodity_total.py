
from datetime import date
import pymysql
import yaml

predict_dt = '2023-06-06'
version_val = 36
wh_id = '-1'
# 修改仓库的总杯量
total_cup = 76770

with open('../conf/predictive_sql.yml', encoding='utf-8') as f:
    yml_data = yaml.load(f, Loader=yaml.CLoader)
    mysql_sql = yml_data['sql2']
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

sql_wh_pred = mysql_sql['query_pred_cup_commodity']

cursor.execute(sql_wh_pred.format(wh_id, version_val, predict_dt))
data = cursor.fetchall()
total_pred = 0
new_cup_list = []
for commodity_pred in data:
    total_pred += commodity_pred[1]
for commodity_pred in data:
    cup_pred = commodity_pred[1]/total_pred * total_cup
    new_cup_list.append([commodity_pred[0], cup_pred])
print('现制饮品商品杯量预测（全国）：')
print(new_cup_list)



