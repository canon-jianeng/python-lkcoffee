
import datedays
import datetime
import calendar
from dateutil.relativedelta import relativedelta


def make_date(year: int, month: int, day: int):
    # 构造日期
    return date_to_str(datetime.date(year, month, day))


def str_to_date(date_str):
    # %Y-%m-%d字符串转日期
    return datetime.datetime.strptime(date_str, '%Y-%m-%d')


def date_to_str(date):
    # 日期转%Y-%m-%d字符串
    return datetime.datetime.strftime(date, '%Y-%m-%d')


def get_now_time():
    # 当前时间
    return datetime.datetime.now()


def get_now_date():
    # 当天日期
    return datetime.datetime.strftime(get_now_time(), '%Y-%m-%d')


def get_yesterday_date():
    # 昨天日期
    return cul_date(get_now_date(), -1)


def cul_days(left_date, right_date):
    # 两个日期相差天数
    day_num = (str_to_date(right_date) - str_to_date(left_date)).days
    return day_num


def get_month_end(date_str):
    # 当月的最后一天
    date_val = str_to_date(date_str)
    days_num = get_month_days(date_val.year, date_val.month)
    return date_val.replace(day=days_num)


def get_month_start(date_str):
    # 当月的第一天
    date_val = str_to_date(date_str)
    return date_val.replace(day=1)


def get_diff_month_num(init_str, cur_str):
    # 获取两个日期相差的全部月份和月份天数
    init_date = str_to_date(init_str)
    cur_date = str_to_date(cur_str)
    interval = (cur_date.year - init_date.year) * 12 + (cur_date.month - init_date.month)
    month_list = []
    for month_val in range(1, interval):
        date_res = init_date + relativedelta(months=month_val)
        month_num = date_res.month
        year_num = date_res.year
        month_days = get_month_days(year_num, month_num)
        month_list.append({'year': year_num, 'month': month_num, 'days': month_days})
    return month_list


def cul_month(date_val, month_num):
    # 某个日期+/-月数后的日期
    month_date = str_to_date(date_val) + relativedelta(months=month_num)
    return month_date


def get_last_month():
    # 上个月
    month_date = cul_month(date_to_str(get_now_time()), -1)
    return month_date.strftime("%Y-%m")


def get_next_month():
    # 下个月
    month_date = cul_month(date_to_str(get_now_time()), 1)
    return month_date.strftime("%Y-%m")


def cul_date(date_val, day_num):
    # 计算+/-天数后的日期
    time_val = str_to_date(date_val) + datetime.timedelta(days=day_num)
    return date_to_str(time_val)


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
    now_time = get_now_time().replace(microsecond=0)
    # 当天日期往前 n 天 的日期列表(day_num=n)
    for num in range(day_num):
        date_val = now_time - datetime.timedelta(days=num+1)
        date_list.append(datetime.datetime.strftime(date_val, "%Y-%m-%d"))
    date_list.reverse()
    return date_list


def get_future_day_date(day_num: int):
    date_list = []
    now_time = get_now_time().replace(microsecond=0)
    # 当天日期
    now_val = get_now_date()
    date_list.append(now_val)
    # 当天日期往后 n 天 的日期列表(day_num=n)
    for num in range(day_num):
        date_val = now_time + datetime.timedelta(days=num+1)
        date_list.append(datetime.datetime.strftime(date_val, "%Y-%m-%d"))
    return date_list


def get_yesterday_last_date():
    now = get_now_time()
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
    now_num = get_now_date().split('-')[2]
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


def get_month_days(year: int, month: int):
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


def get_date_difference_set(left_list, right_list):
    # ['2023-09-20', '2024-02-01'] 和 ['2023-09-20', '2024-02-07'] 结果返回: ['2024-02-02', '2024-02-07']
    left_date = left_list[-1]
    right_date1 = right_list[0]
    right_date2 = right_list[1]
    if left_date > right_date2:
        right_list = []
    else:
        if left_date > right_date1:
            right_list[0] = cul_date(left_date, 1)
    return right_list


def get_future_date_list(date_list):
    # 获取大于今天的日期列表
    future_list = []
    now_date = str_to_date(get_now_date())
    for date_day in date_list:
        if str_to_date(date_day) >= now_date:
            future_list.append(date_day)
    return future_list


if __name__ == '__main__':
    # print(get_month_date('2022-12', 4))
    print(get_month_start('2023-11-15'))
    print(get_month_end('2023-11-01'))
    print(get_future_date('2023-07', 3))
    print(calendar.monthrange(2023, 7)[1])
    print(get_year_date(2022))
    print(get_yesterday_last_date())
    print(make_date(2023, 1, 1))
    print(cul_days('2023-08-18', '2023-08-20'))
    print(cul_month('2023-08-18', -1))
    print(cul_date('2023-08-18', -1))
    print(get_date_val("2022-07-05"))
    print(date_compare('2023-07-24', '2023-08-13', '2023-08-01'))
    print(get_now_time())
    print(get_diff_month_num('2022-08-31', '2023-11-06'))
    print(get_yesterday_date())
