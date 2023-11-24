import random
import datetime
import datedays

list_val = ['a1', 'a2', 'a3']
print(str(list_val))

print(datetime.datetime.now().strftime('%Y'))

for val in list_val:
    print(list_val.index(val), val)

dict_val = {'a': 1, 'b': 2}
for val in dict_val:
    print(val)

cup_num_dict = [{"commodityId": 5352, "goodsId": 42, "month": 4, "needNum": 27.21, "year": 2023},
                {"commodityId": 5352, "goodsId": 42, "month": 3, "needNum": 27.21, "year": 2023},
                {"commodityId": 5352, "goodsId": 42, "month": 9, "needNum": 27.21, "year": 2023},
                {"commodityId": 5352, "goodsId": 42, "month": 11, "needNum": 27.21, "year": 2023},
                {"commodityId": 5618, "goodsId": 42, "month": 2, "needNum": 33.78, "year": 2023},
                {"commodityId": 5618, "goodsId": 42, "month": 9, "needNum": 33.78, "year": 2023},
                {"commodityId": 5352, "goodsId": 42, "month": 12, "needNum": 27.21, "year": 2023},
                {"commodityId": 5352, "goodsId": 83070, "month": 11, "needNum": 17.36, "year": 2023},
                {"commodityId": 5352, "goodsId": 83070, "month": 12, "needNum": 17.36, "year": 2023},
                {"commodityId": 5352, "goodsId": 42, "month": 8, "needNum": 27.21, "year": 2023},
                {"commodityId": 5352, "goodsId": 83070, "month": 9, "needNum": 17.36, "year": 2023},
                {"commodityId": 5352, "goodsId": 42, "month": 10, "needNum": 27.21, "year": 2023},
                {"commodityId": 5618, "goodsId": 42, "month": 12, "needNum": 33.78, "year": 2023},
                {"commodityId": 5352, "goodsId": 83070, "month": 3, "needNum": 17.36, "year": 2023},
                {"commodityId": 5352, "goodsId": 83070, "month": 1, "needNum": 17.36, "year": 2023},
                {"commodityId": 5352, "goodsId": 42, "month": 7, "needNum": 27.21, "year": 2023},
                {"commodityId": 5618, "goodsId": 42, "month": 1, "needNum": 33.78, "year": 2023},
                {"commodityId": 5618, "goodsId": 42, "month": 5, "needNum": 33.78, "year": 2023},
                {"commodityId": 5352, "goodsId": 83070, "month": 2, "needNum": 17.36, "year": 2023},
                {"commodityId": 5352, "goodsId": 83070, "month": 10, "needNum": 17.36, "year": 2023},
                {"commodityId": 5618, "goodsId": 42, "month": 7, "needNum": 33.78, "year": 2023},
                {"commodityId": 5352, "goodsId": 42, "month": 6, "needNum": 27.21, "year": 2023},
                {"commodityId": 5352, "goodsId": 83070, "month": 8, "needNum": 17.36, "year": 2023},
                {"commodityId": 5352, "goodsId": 83070, "month": 4, "needNum": 17.36, "year": 2023},
                {"commodityId": 5618, "goodsId": 42, "month": 3, "needNum": 33.78, "year": 2023},
                {"commodityId": 5352, "goodsId": 42, "month": 1, "needNum": 27.21, "year": 2023},
                {"commodityId": 5352, "goodsId": 42, "month": 5, "needNum": 27.21, "year": 2023},
                {"commodityId": 5352, "goodsId": 83070, "month": 7, "needNum": 17.36, "year": 2023},
                {"commodityId": 5618, "goodsId": 42, "month": 6, "needNum": 33.78, "year": 2023},
                {"commodityId": 5352, "goodsId": 42, "month": 2, "needNum": 27.21, "year": 2023},
                {"commodityId": 5618, "goodsId": 42, "month": 8, "needNum": 33.78, "year": 2023},
                {"commodityId": 5352, "goodsId": 83070, "month": 6, "needNum": 17.36, "year": 2023},
                {"commodityId": 5618, "goodsId": 42, "month": 10, "needNum": 33.78, "year": 2023},
                {"commodityId": 5618, "goodsId": 42, "month": 11, "needNum": 33.78, "year": 2023},
                {"commodityId": 5618, "goodsId": 42, "month": 4, "needNum": 33.78, "year": 2023},
                {"commodityId": 5352, "goodsId": 83070, "month": 5, "needNum": 17.36, "year": 2023},
                {"commodityId": 5990, "goodsId": 42, "month": 8, "needNum": 35.26, "year": 2023},
                {"commodityId": 5990, "goodsId": 42, "month": 9, "needNum": 35.26, "year": 2023},
                {"commodityId": 5352, "goodsId": 44, "month": 8, "needNum": 71.44, "year": 2023},
                {"commodityId": 5352, "goodsId": 44, "month": 9, "needNum": 71.44, "year": 2023},
                {"commodityId": 5990, "goodsId": 48214, "month": 8, "needNum": 7.63, "year": 2023},
                {"commodityId": 5990, "goodsId": 48214, "month": 9, "needNum": 7.63, "year": 2023},
                {"commodityId": 5990, "goodsId": 42, "month": 6, "needNum": 35.26, "year": 2023},
                {"commodityId": 5990, "goodsId": 42, "month": 12, "needNum": 35.26, "year": 2023},
                {"commodityId": 5352, "goodsId": 44, "month": 6, "needNum": 71.44, "year": 2023},
                {"commodityId": 5352, "goodsId": 44, "month": 12, "needNum": 71.44, "year": 2023},
                {"commodityId": 5990, "goodsId": 48214, "month": 6, "needNum": 7.63, "year": 2023},
                {"commodityId": 5990, "goodsId": 48214, "month": 12, "needNum": 7.63, "year": 2023},
                {"commodityId": 5990, "goodsId": 42, "month": 7, "needNum": 35.26, "year": 2023},
                {"commodityId": 5990, "goodsId": 42, "month": 10, "needNum": 35.26, "year": 2023},
                {"commodityId": 5990, "goodsId": 42, "month": 11, "needNum": 35.26, "year": 2023},
                {"commodityId": 5352, "goodsId": 44, "month": 7, "needNum": 71.44, "year": 2023},
                {"commodityId": 5352, "goodsId": 44, "month": 10, "needNum": 71.44, "year": 2023},
                {"commodityId": 5352, "goodsId": 44, "month": 11, "needNum": 71.44, "year": 2023},
                {"commodityId": 5990, "goodsId": 48214, "month": 7, "needNum": 7.63, "year": 2023},
                {"commodityId": 5990, "goodsId": 48214, "month": 10, "needNum": 7.63, "year": 2023},
                {"commodityId": 5990, "goodsId": 48214, "month": 11, "needNum": 7.63, "year": 2023}]

cup_dict = {}
for cup_val in cup_num_dict:
    cup_val_month = str(cup_val['month'])
    if cup_val_month in cup_dict.keys():
        cup_val_goods = str(cup_val['goodsId'])
        commodity_dict = cup_dict[cup_val_month]
        if cup_val_goods in commodity_dict.keys():
            commodity_dict[cup_val_goods].update({str(cup_val['commodityId']): str(cup_val['needNum'])})
        else:
            commodity_dict[cup_val_goods] = {str(cup_val['commodityId']): str(cup_val['needNum'])}
    else:
        cup_dict[cup_val_month] = {str(cup_val['goodsId']): {str(cup_val['commodityId']): str(cup_val['needNum'])}}
print(cup_dict)

print(random.randrange(0, 50))
print(random.uniform(0, 50))
print(random.randint(0, 1))

date_list = []
# 当天日期往前30天的日期列表
for num in range(30):
    date_val = datetime.datetime.now().replace(microsecond=0) - datetime.timedelta(days=num + 1)
    date_list.append(datetime.datetime.strftime(date_val, "%Y-%m-%d"))
print(date_list[0], date_list[len(date_list) - 1])


def get_date_list(begin_date, end_date):
    # 获取起止日期时间段的所有时间列表
    dates = []
    # Get the time tuple : dt
    dt = datetime.datetime.strptime(begin_date, "%Y-%m-%d")
    date = begin_date[:]
    while date <= end_date:
        dates.append(date)
        dt += datetime.timedelta(days=1)
        date = dt.strftime("%Y-%m-%d")
    return dates


print(get_date_list('2023-05-15', '2023-05-21'))

print('2024-01-01'.split("-"))

print(datedays.gettodaydays('2024-01-01'))

now_time = datetime.datetime.now()
now_dt = now_time.strftime("%Y-%m-%d")
now_str = now_time.strftime("%Y-%m-%d %H:%M:%S")
batch_no = str(now_str).replace('-', '').replace(':', '').replace(' ', '')
print(batch_no)

print((datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d"))
