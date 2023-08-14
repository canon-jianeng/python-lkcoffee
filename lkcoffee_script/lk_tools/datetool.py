
import datedays
import datetime
import calendar


def get_month_date(month: str, num=0):
    # month ='2024-01'
    date_list = []
    month_num = int(month.split('-')[1].lstrip('0'))
    if num > month_num:
        raise Exception("不能大于当前月份数")
    year_val = month.split('-')[0]
    if num > 0:
        # 获取当前年 month_num-num 月到当前月的日期列表
        init_num = month_num - num
    else:
        # 获取当前年1月到当前月的日期列表
        init_num = num
    for num in range(init_num, month_num):
        month = num + 1
        if month < 10:
            month_val = year_val + '-0' + str(month)
        else:
            month_val = year_val + '-' + str(month)
        date_list += datedays.gettodaydays(str(month_val) + '-01')
    return date_list


def get_last_month_date(month: str):
    # 获取当前年1月到前一个月的日期列表
    date_list = []
    month_num = int(month.split('-')[1].lstrip('0'))
    if month_num < 2:
        raise Exception("必须大于1月")
    year_val = month.split('-')[0]
    for num in range(month_num-1):
        month = num + 1
        if month < 10:
            month_val = year_val + '-0' + str(month)
        else:
            month_val = year_val + '-' + str(month)
        date_list += datedays.gettodaydays(str(month_val) + '-01')
    return date_list


def get_last_date(day_num: int):
    date_list = []
    # 当天日期往前 n 天 的日期列表(day_num=n)
    for num in range(day_num):
        date_val = datetime.datetime.now().replace(microsecond=0) - datetime.timedelta(days=num+1)
        date_list.append(datetime.datetime.strftime(date_val, "%Y-%m-%d"))
    date_list.reverse()
    return date_list


def get_future_day_date(day_num: int):
    date_list = []
    # 当天日期
    now_val = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
    date_list.append(now_val)
    # 当天日期往后 n 天 的日期列表(day_num=n)
    for num in range(day_num):
        date_val = datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(days=num+1)
        date_list.append(datetime.datetime.strftime(date_val, "%Y-%m-%d"))
    return date_list


def get_yesterday_last_date():
    now = datetime.datetime.now()
    day_num = (now - datetime.datetime(now.year, now.month, 1)).days
    # 本月当天之前的日期列表
    yesterday_last = get_last_date(day_num)
    # 获取当前年1月到前一个月的日期列表
    date_list = now.strftime('%Y-%m-%d').split('-')
    last_date = get_last_month_date(date_list[0] + '-' + date_list[1])
    # 获取当前年1月1号到前一天日期的日期列表
    return last_date + yesterday_last


def get_year_date(year_val: int):
    # 任意一年的全部日期
    date_list = []
    for num in range(12):
        month = num + 1
        if month < 10:
            month_val = str(year_val) + '-0' + str(month)
        else:
            month_val = str(year_val) + '-' + str(month)
        date_list += datedays.gettodaydays(str(month_val) + '-01')
    return date_list


def get_year_month_date(year_val: int, month: int):
    # 任意一年的某个月的全部日期
    date_list = []
    if month < 10:
        month_val = str(year_val) + '-0' + str(month)
    else:
        month_val = str(year_val) + '-' + str(month)
    return datedays.gettodaydays(str(month_val) + '-01')


def get_future_date(year_month: str, future_num: int):
    date_list = []
    date_split = year_month.split('-')
    month_num = int(date_split[1].lstrip('0'))
    year_val = date_split[0]
    # 当月未来日期
    now_num = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d').split('-')[2]
    future_date = get_future_day_date(calendar.monthrange(int(year_val), month_num)[1]-int(now_num))
    # 当月为T, T+n个月的日期(future_num=n)
    for num in range(month_num, month_num+future_num):
        month = num + 1
        if month < 10:
            month_val = year_val + '-0' + str(month)
        else:
            month_val = year_val + '-' + str(month)
        date_list += datedays.gettodaydays(str(month_val) + '-01')
    return future_date + date_list


def get_month_end_date(year: int, month: int):
    # 第一天是星期几（0-6对应星期一到星期天）和这个月的天数
    date, month_num = calendar.monthrange(year, month)
    return month_num


def get_last_reduce_date(date_val: str, num: int):
    # date_val 日期减去 num 天的日期
    date_time = datetime.datetime.strptime(date_val, '%Y-%m-%d').replace(microsecond=0) - datetime.timedelta(days=num)
    return datetime.datetime.strftime(date_time, '%Y-%m-%d')


def get_date_val(date_val: str):
    date_list = date_val.split("-")
    # 去掉月份中的 0
    if date_list[1].startswith("0"):
        date_list[1] = date_list[1][1:]
    # 去掉日期中的 0
    if date_list[2].startswith("0"):
        date_list[2] = date_list[2][1:]
    new_date = "-".join(date_list)
    return new_date


def date_compare(left_day, right_day, day_val):
    # 判断日期在 [left_day, right_day] 范围内
    left_date = datetime.datetime.strptime(left_day, '%Y-%m-%d')
    right_date = datetime.datetime.strptime(right_day, '%Y-%m-%d')
    date_val = datetime.datetime.strptime(day_val, '%Y-%m-%d')
    if left_date <= date_val <= right_date:
        return True
    else:
        return False


if __name__ == '__main__':
    # print(get_month_date('2022-12', 4))
    print(get_future_date('2023-07', 3))
    print(calendar.monthrange(2023, 7)[1])
    print(get_year_date(2022))
    print(get_yesterday_last_date())
    print(datetime.datetime.strptime('2023-07-17', '%Y-%m-%d'))
    # 上个月
    print(datetime.datetime.now().replace(day=1) - datetime.timedelta(days=1))
    print(get_date_val("2022-07-05"))
    print(date_compare('2023-07-24', '2023-08-13', '2023-08-01'))
