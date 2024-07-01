
import time
import requests
from auto_dm import tools

"""
查询 idata平台 数据
http://wiki.lkcoffee.com/pages/viewpage.action?pageId=4946779
http://wiki.lkcoffee.com/pages/viewpage.action?pageId=6593953

"""


def get_query_id(sql_val, env="test"):
    """
    查询提交接口
    """
    conf_data = tools.conf_data.get_conf_yaml()[env]
    user_name = conf_data['idata_name']
    json_data = {
        # 程序端唯一id, 非必须
        "origCode": '',
        # 用户名
        "application": user_name,
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
        'Authorization': conf_data['idata_token'],
        # 数据开发平台, 权限控制-程序用户, 登录名
        'Principal': user_name
    }
    url = conf_data['url_dataq'] + '/dataq-api/app-rpc-api/query'
    res = requests.post(url, headers=headers, json=json_data).json()
    print('查询任务id: {}'.format(res['data']))
    return res['data']


def get_query_status(id_val, env="test"):
    """
    获取查询结果
    """
    conf_data = tools.conf_data.get_conf_yaml()[env]
    user_name = conf_data['idata_name']
    status_dict = {
        '1': '初始化',
        '2': '运行中',
        '3': '完成',
        '4': '错误',
        '5': '取消'
    }
    # 查询状态码
    res_status = 1
    while res_status < 3:
        headers = {
            # 数据开发平台, 权限控制-程序用户, token
            'Authorization': conf_data['idata_token'],
            # 数据开发平台, 权限控制-程序用户, 登录名
            'Principal': user_name
        }
        url = conf_data['url_dataq'] + '/dataq-api/app-rpc-api/get-query-result'
        params = {'id': id_val}
        res = requests.get(url, headers=headers, params=params).json()
        res_status = res['data']['status']
        if res_status >= 3:
            print('查询任务执行状态: {}'.format(status_dict[str(res_status)]))
            break
        print('查询任务执行状态: {}'.format(status_dict[str(res_status)]))
        time.sleep(10)
    return res_status


def query_to_csv(sql_val, file_path, env="test"):
    """
    下载文件
    """
    conf_data = tools.conf_data.get_conf_yaml()[env]
    user_name = conf_data['idata_name']
    id_val = get_query_id(sql_val, env)
    res_status = get_query_status(id_val, env)
    if res_status == 3:
        headers = {
            # 数据开发平台, 权限控制-程序用户, token
            'Authorization': conf_data['idata_token'],
            # 数据开发平台, 权限控制-程序用户, 登录名
            'Principal': user_name
        }
        params = {'id': id_val}
        url = conf_data['url_dataq'] + '/dataq-api/app-rpc-api/download'
        res = requests.get(url, headers=headers, params=params)
        # 写入文件
        with open(file_path, 'w+') as f:
            f.write(res.text)
        print('下载 {} 文件完成'.format(file_path.split('/')[-1]))
    else:
        print('查询失败')


def query_sql():
    pass


if __name__ == '__main__':
    val = "select * from dw_lucky_dataplatform.dm_shop_unfreeze_goods_predict where wh_dept_id in (4001, 19101) and dt='2023-11-30';"
    path_val = '../data/shop_unfreeze_data.csv'
    query_to_csv(val, path_val)
