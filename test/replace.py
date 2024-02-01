
import re

val_str = ''
with open('/Users/canon/Documents/PythonProject/Github/python-lkcoffee/test/test', 'r') as f:
    read_data = f.readlines()
    for val in read_data:
        val_init = val.strip()
        if val_init:
            val_list = val_init.split(',')
            year_val = val_list[0][8:12]
            month_val = val_list[1][2:4]
            type_id = re.match("(.*?)as", val_list[2]).group(1).strip()
            goods_id = re.match("(.*?)as", val_list[3]).group(1).strip()
            type_val = re.match("(.*?)as", val_list[4]).group(1).strip()
            need_num = re.match("(.*?)as", val_list[5]).group(1).strip()
            sql_val = "select cast('2023-12-13' as date) as dt, {} as type_id, {} as goods_id, '{}-{}' as month, {} as type, {} as single_need_num union all\n"
            val_str += sql_val.format(type_id, goods_id, year_val, month_val, type_val, need_num)

with open('/Users/canon/Documents/PythonProject/Github/python-lkcoffee/test/test1', 'w') as f:
    f.write(val_str)
