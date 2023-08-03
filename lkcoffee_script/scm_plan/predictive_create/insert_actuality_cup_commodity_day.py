
import yaml
import random
import datetime
from lkcoffee_script import lk_tools

"""
查询是否重复
SELECT wh_dept_id, record_date, commodity_id FROM t_actuality_cup_commodity_day 
GROUP BY wh_dept_id, record_date, commodity_id HAVING count(*) > 1;

查询数据是否存在:
SELECT * FROM t_actuality_cup_commodity_day 
WHERE 
  wh_dept_id in ('327193', '245971', '245871', '326932', '326327', '-1') 
  AND record_date in () 
  AND commodity_id in (5352, 5990, 6192, 801, 800);

"""

# 当前年份
now_year = int(datetime.datetime.now().strftime('%Y'))
# 前一年日期
date_list_last_year = lk_tools.datetool.get_month_date(str(now_year-1)+'-12')
# 获取当前年1月1号到前一天日期的日期列表
date_list_now = lk_tools.datetool.get_yesterday_last_date()

# 当天日期往前30天的日期列表
# date_list = lk_tools.datetool.get_last_date(30)
date_list = date_list_last_year + date_list_now


commodity_list = [
    # 饮品
    5352, 5990, 6192,
    # 食品
    801, 800
]
wh_dept_id = [
    '327193', '245971', '245871', '326932', '326327', '-1'
]

with open('./sql.yml', encoding='utf-8') as f:
    yml_data = yaml.load(f, Loader=yaml.CLoader)
    mysql_sql = yml_data['sql']
sql_insert = mysql_sql['insert_actuality_cup_commodity_day']
sql_insert_value = mysql_sql['val_actuality_cup_commodity_day']

val_data = ''
for commodity in commodity_list:
    for wh in wh_dept_id:
        for date_val in date_list:
            amount = random.uniform(0, 20)
            val_str = (sql_insert_value + ',\n').format(
                date_val.split('-')[0], date_val, wh, commodity, '10', amount
            )
            val_data += val_str

insert_data = sql_insert + '\n' + val_data


with open('../data/predictive_create/actuality_cup_commodity_day.txt', 'w', encoding='utf-8') as f:
    f.write(insert_data)
