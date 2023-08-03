
import yaml
import random
import datetime

"""
查询是否重复
select commodity_id, type, wh_dept_id from t_actuality_cup_commodity 
GROUP BY `year`, type, commodity_id, wh_dept_id HAVING count(*) > 1;

查询数据是否存在:
SELECT * FROM t_actuality_cup_commodity 
WHERE 
  `year`=2022 
  AND type=10 
  AND commodity_id in (5352, 5990, 6192, 801, 800) 
  AND wh_dept_id in ('327193', '245971', '245871', '326932', '326327', '-1');

"""

# 当前年份
now_year = int(datetime.datetime.now().strftime('%Y'))
now_month = int(datetime.datetime.now().strftime('%m'))
# 年份列表
year_list = [now_year-1, now_year]

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
sql_insert = mysql_sql['insert_actuality_cup_commodity']
sql_insert_value = mysql_sql['val_actuality_cup_commodity']

val_data = ''
for year_val in year_list:
    if year_val == now_year:
        month_num = now_month - 1
    else:
        month_num = 12
    for commodity in commodity_list:
        for wh in wh_dept_id:
            amount_1, amount_2, amount_3, amount_4, amount_5, amount_6 = 0, 0, 0, 0, 0, 0
            amount_7, amount_8, amount_9, amount_10, amount_11, amount_12 = 0, 0, 0, 0, 0, 0
            if month_num >= 1:
                amount_1 = random.uniform(0, 50)
            if month_num >= 2:
                amount_2 = random.uniform(0, 50)
            if month_num >= 3:
                amount_3 = random.uniform(0, 50)
            if month_num >= 4:
                amount_4 = random.uniform(0, 50)
            if month_num >= 5:
                amount_5 = random.uniform(0, 50)
            if month_num >= 6:
                amount_6 = random.uniform(0, 50)
            if month_num >= 7:
                amount_7 = random.uniform(0, 50)
            if month_num >= 8:
                amount_8 = random.uniform(0, 50)
            if month_num >= 9:
                amount_9 = random.uniform(0, 50)
            if month_num >= 10:
                amount_10 = random.uniform(0, 50)
            if month_num >= 11:
                amount_11 = random.uniform(0, 50)
            if month_num == 12:
                amount_12 = random.uniform(0, 50)
            amount_total = (amount_1 + amount_2 + amount_3 + amount_4 + amount_5 + amount_6
                            + amount_7 + amount_8 + amount_9 + amount_10 + amount_11 + amount_12) / 12
            val_str = sql_insert_value.format(
                year_val, commodity, '10', amount_1, amount_2, amount_3, amount_4,
                amount_5, amount_6, amount_7, amount_8, amount_9, amount_10,
                amount_11, amount_12, amount_total, wh
            )
            val_data += val_str

insert_data = sql_insert + '\n' + val_data


with open('../data/predictive_create/actuality_cup_commodity.txt', 'w', encoding='utf-8') as f:
    f.write(insert_data)
