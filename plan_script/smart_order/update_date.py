
import pymysql
import yaml


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

sql_pre_day = mysql_sql['other']['query_pre_day']
update_pre_day = mysql_sql['other']['update_pre_day']

cursor.execute(sql_pre_day)
sql_data = cursor.fetchall()
for data_val in sql_data:
    date_list = data_val[1].split('-')
    month_num = int(date_list[1])
    day_num = int(date_list[2])
    if month_num < 10:
        month_val = '0' + str(month_num)
    else:
        month_val = str(month_num)
    if day_num < 10:
        day_val = '0' + str(day_num)
    else:
        day_val = str(day_num)
    date_val = date_list[0] + '-' + month_val + '-' + day_val
    update_val = update_pre_day.format(date_val, data_val[0])
    print(update_val)
    cursor.execute(update_val)

db_cooperation.commit()
