
import hashlib
import calendar
import time
import requests

"""
查询 idata平台 数据
http://wiki.lkcoffee.com/pages/viewpage.action?pageId=4946779
http://wiki.lkcoffee.com/pages/viewpage.action?pageId=6593953

"""


def get_query_id(sql_val):
    """
    查询提交接口
    """
    json_data = {
        # 程序端唯一id, 非必须
        "origCode": '',
        # 用户名
        "application": 'p_smarketsever',
        # 1：Spark查Hive, 2: Spark查Kudu, 3: Kylin JDBC, 4: Kudu JDBC, 6: Presto查hive, 7:Doris 查询doris
        "actuatorType": 1,
        # 默认为0-不返回，查询结果是否通过HTTP返回，默认最多5000条和查询结果小于1M
        # 'queryResultBack': 1,
        # 默认为0-不写，查询结果保存为CSV时，是否写表头
        'writeHeader': 1,
        # 默认文件类型为CSV
        # 'fileType': 'CSV',
        "querySql": sql_val,
    }
    headers = {
        'Content-Type': 'application/json',
        # 数据开发平台, 权限控制-程序用户, token
        'Authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoicF9zbWFya2V0c2V2ZXIiLCJhdHkiOiJ1c3IiLCJlbnYiOiJ0ZXN0IiwiaXNzIjoibHVja2luY29mZmVlIiwic3ViIjoib25lZGF0YSIsImV4cCI6MjE0NTg4ODAwMH0.F3HhC5MmEK8nbAyo7uLNCh9Rly7rih_8dgIk5uxCNWg',
        # 数据开发平台, 权限控制-程序用户, 登录名
        'Principal': 'p_smarketsever'
    }
    url = 'http://dataqtest03.lkcoffee.com/dataq-api/app-rpc-api/query'
    res = requests.post(url, headers=headers, json=json_data).json()
    # print(res['data'])
    return res['data']


def get_query_status(id_val):
    """
    获取查询结果
    """
    # 查询状态码：1-初始化，2-运行中，3-完成，4-错误，5-取消
    res_status = 1
    while res_status < 3:
        headers = {
            # 数据开发平台, 权限控制-程序用户, token
            'Authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoicF9zbWFya2V0c2V2ZXIiLCJhdHkiOiJ1c3IiLCJlbnYiOiJ0ZXN0IiwiaXNzIjoibHVja2luY29mZmVlIiwic3ViIjoib25lZGF0YSIsImV4cCI6MjE0NTg4ODAwMH0.F3HhC5MmEK8nbAyo7uLNCh9Rly7rih_8dgIk5uxCNWg',
            # 数据开发平台, 权限控制-程序用户, 登录名
            'Principal': 'p_smarketsever'
        }
        url = 'http://dataqtest03.lkcoffee.com/dataq-api/app-rpc-api/get-query-result'
        params = {'id': id_val}
        res = requests.get(url, headers=headers, params=params).json()
        # print(res)
        res_status = res['data']['status']
        if res_status >= 3:
            break
        time.sleep(1)
    return res_status


def query_to_csv(sql_val):
    """
    下载文件
    """
    id_val = get_query_id(sql_val)
    res_status = get_query_status(id_val)
    if res_status == 3:
        headers = {
            # 数据开发平台, 权限控制-程序用户, token
            'Authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoicF9zbWFya2V0c2V2ZXIiLCJhdHkiOiJ1c3IiLCJlbnYiOiJ0ZXN0IiwiaXNzIjoibHVja2luY29mZmVlIiwic3ViIjoib25lZGF0YSIsImV4cCI6MjE0NTg4ODAwMH0.F3HhC5MmEK8nbAyo7uLNCh9Rly7rih_8dgIk5uxCNWg',
            # 数据开发平台, 权限控制-程序用户, 登录名
            'Principal': 'p_smarketsever'
        }
        params = {'id': id_val}
        url = 'http://dataqtest03.lkcoffee.com/dataq-api/app-rpc-api/download'
        res = requests.get(url, headers=headers, params=params)

        file = open('./test.csv', 'a+')
        file.write(res.text)
        file.close()
    else:
        print('查询失败')


def query_sql():
    pass


if __name__ == '__main__':
    val = "select * from dw_ads_scm_alg.alg_control_tower_wh_goods_stock_simulation_without_cg_trs where 1=1 and dt='2023-08-16' limit 10"
    query_to_csv(val)
