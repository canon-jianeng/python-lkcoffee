
import random
import datetime
import yaml
from lkcoffee_script import lk_tools

"""
查询是否重复
SELECT predict_dt, commodity_id, wh_dept_id FROM t_alg_purchase_wh_com_pred_future 
GROUP BY predict_dt, commodity_id, wh_dept_id HAVING count(*) > 1;

查询数据是否存在:
SELECT * FROM t_alg_purchase_wh_com_pred_future 
WHERE
  commodity_id in (5990, 801) 
  AND wh_dept_id in ('327193', '245971', '245871', '326932', '326327', '-1') 
  AND predict_dt in ();

"""

# 当前年份
now_year = int(datetime.datetime.now().strftime('%Y'))

# 过去实际数据
# 前一年日期
date_list_last_year = lk_tools.datetool.get_month_date(str(now_year-1)+'-12')
# 获取当前年1月1号到前一天日期的日期列表
date_list_now = lk_tools.datetool.get_yesterday_last_date()

# 预测当前月及未来的3个月
now_month = datetime.datetime.now().strftime('%Y-%m')
date_list_pre = lk_tools.datetool.get_future_date(now_month, 3)

# 明年1月份日期
date_list_next_year = lk_tools.datetool.get_year_month_date(now_year+1, 1)
date_list = date_list_last_year + date_list_now + date_list_pre + date_list_next_year


wh_dept_id = [
    '327193', '245971', '245871', '326932', '326327', '-1'
]

# 新品
commodity_list = [5990, 6192, 801]


with open('./sql.yml', encoding='utf-8') as f:
    yml_data = yaml.load(f, Loader=yaml.CLoader)
    mysql_sql = yml_data['sql']
    mysql_conf = yml_data['mysql']

sql_insert = mysql_sql['insert_alg_purchase_wh_com_pred_future']
sql_insert_value = mysql_sql['val_alg_purchase_wh_com_pred_future']

val_data = ''
val_sql = sql_insert_value + ',\n'
amount = 0
for commodity in commodity_list:
    for date_val in date_list:
        for wh in wh_dept_id:
            if wh == '-1':
                val_str = val_sql.format(
                    date_val, commodity, wh, amount
                )
                val_data += val_str
                amount = 0
            else:
                amount_num = random.uniform(0, 20)
                amount += amount_num
                val_str = val_sql.format(
                    date_val, commodity, wh, amount_num
                )
                val_data += val_str
insert_data = sql_insert + '\n' + val_data


with open('../data/predictive_create/alg_purchase_wh_com_pred_future.txt', 'w', encoding='utf-8') as f:
    f.write(insert_data)
