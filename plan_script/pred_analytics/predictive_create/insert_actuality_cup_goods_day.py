
import random
import yaml
import datetime
from lkcoffee_script import lk_tools

"""
查询是否重复
SELECT `year`, record_date, wh_dept_id, goods_id, type FROM t_actuality_cup_goods_day
GROUP BY record_date, wh_dept_id, goods_id, type HAVING count(*) > 1;

查询数据是否存在:
SELECT * FROM t_actuality_cup_goods_day 
WHERE 
  wh_dept_id in ('327193', '245971', '245871', '326932', '326327', '-1')
  AND record_date in ()
  AND goods_id in ('42', '48214', '82796', '44', '83070', '83622', '83623')
  AND type in ('20', '40');

# 当天日期往前30天的日期列表
# date_list = lk_tools.datetool.get_last_date(30)
"""

# 当前年份
now_year = int(datetime.datetime.now().strftime('%Y'))

# 过去实际数据（当前年1月1号到前一天日期的日期列表）
# 前一年日期
date_list_last_year = lk_tools.datetool.get_month_date(str(now_year-1)+'-12')

# 当前年日期
date_list_now = lk_tools.datetool.get_month_date(str(now_year)+'-12')

# 明年日期
date_list_next_year = lk_tools.datetool.get_month_date(str(now_year+1)+'-12')

date_list = date_list_last_year + date_list_now + date_list_next_year

wh_dept_id = [
    '327193', '245971', '245871', '326932', '326327', '-1'
]

goods_dict = {
    # 新品有冷比例系数
    '42': ['20', '40'],
    '48214': ['20', '40'],
    '82796': ['20', '40'],
    '44': ['20'],
    '83070': ['20'],
    '86969': ['20'],
    '83207': ['20'],
    # 食品
    '83622': ['20'],
    '83623': ['20']
}

with open('./sql.yml', encoding='utf-8') as f:
    yml_data = yaml.load(f, Loader=yaml.CLoader)
    mysql_sql = yml_data['sql']

sql_insert = mysql_sql['insert_actuality_cup_goods_day']
sql_insert_value = mysql_sql['val_actuality_cup_goods_day']

val_data = ''
val_sql = sql_insert_value + ',\n'
amount = 0
for item in goods_dict.items():
    for val in item[1]:
        for date_val in date_list:
            for wh in wh_dept_id:
                if val == '20':
                    if wh == '-1':
                        val_str = val_sql.format(
                            date_val.split('-')[0], date_val, item[0], val, wh, amount
                        )
                        val_data += val_str
                        amount = 0
                    else:
                        amount_num = random.uniform(100000, 500000)
                        amount += amount_num
                        val_str = val_sql.format(
                            date_val.split('-')[0], date_val, item[0], val, wh, amount_num
                        )
                        val_data += val_str
                if val == '40':
                    amount_num = random.uniform(0, 1)
                    val_str = val_sql.format(
                        date_val.split('-')[0], date_val, item[0], val, wh, amount_num
                    )
                    val_data += val_str
insert_data = sql_insert + '\n' + val_data


with open('../data/predictive_create/actuality_cup_goods_day.txt', 'w', encoding='utf-8') as f:
    f.write(insert_data)
