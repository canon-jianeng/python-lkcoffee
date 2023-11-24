
import random
import pymysql
import datetime
import yaml
from lkcoffee_script import lk_tools

"""
查询是否重复
SELECT record_date, wh_dept_id FROM t_bi_warehouse_shop_detail 
GROUP BY record_date, wh_dept_id HAVING count(*) > 1 ORDER BY record_date DESC;

查询数据是否存在:
SELECT * FROM t_bi_warehouse_shop_detail 
WHERE
  wh_dept_id in ('327193', '245971', '245871', '326932', '326327', '-1')
  AND record_date in ();
  
数仓-仓库门店详情表: t_bi_warehouse_shop_detail

"""

# 获取当前年1月1号到前一天日期的日期列表
date_list_last = lk_tools.datetool.get_yesterday_last_date()

# 当前年份
now_year = int(datetime.datetime.now().strftime('%Y'))
# 前一年日期
date_list_last_year = lk_tools.datetool.get_month_date(str(now_year-1)+'-12')
# 明年1月份日期
date_list_next_year = lk_tools.datetool.get_year_month_date(now_year+1, 1)
date_list = date_list_last + date_list_last_year + date_list_next_year


wh_dept_id = [
    '327193', '245971', '245871', '326932', '326327', '-1'
]


with open('./sql.yml', encoding='utf-8') as f:
    yml_data = yaml.load(f, Loader=yaml.CLoader)
    mysql_sql = yml_data['sql']
    mysql_conf = yml_data['mysql']

sql_insert = mysql_sql['insert_bi_warehouse_shop_detail']
sql_insert_value = mysql_sql['val_bi_warehouse_shop_detail']


val_data = ''
val_sql = sql_insert_value + ',\n'
for date_val in date_list:
    for wh in wh_dept_id:
        self_num = random.randint(50, 300)
        agent_num = random.randint(10, self_num)
        self_operating_num = random.randint(50, 300)
        agent_operating_num = random.randint(10, self_operating_num)
        val_str = val_sql.format(
            date_val, wh, self_num, agent_num, self_num+agent_num,
            self_operating_num, agent_operating_num, self_operating_num+agent_operating_num,
        )
        val_data += val_str
insert_data = sql_insert + '\n' + val_data


def update_data():
    # 更新全国的数据
    sql_update = "UPDATE t_bi_warehouse_shop_detail SET total_operating_num={} WHERE record_date='{}' AND wh_dept_id='-1';"
    sql_query = "SELECT SUM(total_operating_num) AS num FROM t_bi_warehouse_shop_detail WHERE record_date='{}' AND wh_dept_id!='-1'"
    sql_query_date = "SELECT distinct record_date FROM t_bi_warehouse_shop_detail"

    with open('predictive_analytics/predictive_sql.yml', encoding='utf-8') as f:
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

    key_list = ['self_num', 'agent_num', 'total_num', 'self_operating_num', 'agent_operating_num', 'total_operating_num']

    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db_cooperation.cursor()

    cursor.execute(sql_query_date)
    data = cursor.fetchall()
    for date in data:
        cursor.execute(sql_query.format(date[0]))
        num = cursor.fetchone()[0]
        cursor.execute(sql_update.format(num, date[0]))
    # db_cooperation.commit()


with open('../data/predictive_create/bi_warehouse_shop_detail.txt', 'w', encoding='utf-8') as f:
    f.write(insert_data)
