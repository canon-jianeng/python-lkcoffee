
import pymysql
import yaml

# 厦门小奶狗贸易有限公司
supplier_id = 1964
time_start = '2022-10-01'
time_end = '2022-12-31'

with open('sql.yml', encoding='utf-8') as f:
    yml_data = yaml.load(f, Loader=yaml.CLoader)
    mysql_sql = yml_data['sql']
    mysql_conf = yml_data['mysql']

# 打开数据库连接
db_purchase = pymysql.connect(
    host=mysql_conf['stock_purchase']['host'],
    user=mysql_conf['stock_purchase']['user'],
    password=mysql_conf['stock_purchase']['pwd'],
    database=mysql_conf['stock_purchase']['db'],
    port=mysql_conf['stock_purchase']['port']
)
db_stock = pymysql.connect(
    host=mysql_conf['stock']['host'],
    user=mysql_conf['stock']['user'],
    password=mysql_conf['stock']['pwd'],
    database=mysql_conf['stock']['db'],
    port=mysql_conf['stock']['port']
)

# 使用 cursor() 方法创建一个游标对象 cursor
cursor = db_purchase.cursor()
cursor2 = db_stock.cursor()

sql_consign = mysql_sql['query_consign']
cursor.execute(sql_consign.format(supplier_id, time_start, time_end))
data = cursor.fetchall()
list_consign = []
# 获取发货单号
for value in data:
    list_consign.append(value[0])
print(list_consign)

sql_reserve = mysql_sql['query_reserve']
# 未预约发货单数
unbooked_count = 0
# 未签到发货单数
unreceipted_count = 0
# 预约发货单数
reservation_count = 0
# 迟到发货单数
late_count = 0
# 获取预约单状态、到仓状态
for list_val in list_consign:
    cursor2.execute(sql_reserve.format(list_val))
    data2 = cursor2.fetchone()
    # print(data2)
    # 不存在预约单, 发货单: 未预约
    if data2 is not None:
        reservation_count += 1
        # 到仓状态:已到仓（迟到）, 发货单: 迟到
        if data2[9] == 3:
            late_count += 1
        # 到仓状态:未到仓
        if data2[9] == 1:
            # 发货单: 未签到
            if data2[8] != 4:
                unreceipted_count += 1
            # 发货单: 未预约
            if data2[8] == 4:
                unbooked_count += 1

consign_count = len(list_consign)
unbooked_count += consign_count - reservation_count
print("发货单：" + str(consign_count))
print("未预约发货单：" + str(unbooked_count))
print("未签到发货单：" + str(unreceipted_count))
print("迟到发货单：" + str(late_count))
if unbooked_count > 100:
    unbooked_count = 100
if late_count > 100:
    late_count = 100
score = (100-unbooked_count)*0.4 + (100-unreceipted_count)*0.3 + (100-late_count)*0.3
print("预约到货得分：" + str(score))

# 关闭数据库连接
db_purchase.close()
db_stock.close()
