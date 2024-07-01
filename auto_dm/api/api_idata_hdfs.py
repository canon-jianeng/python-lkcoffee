
import requests
from datetime import datetime
from auto_dm import tools

"""
idata平台 的 HDFS 目录文件
http://wiki.lkcoffee.com/pages/viewpage.action?pageId=97247910

idata平台，权限控制-权限申请-申请其他权限【测试环境申请后自动审批】
1、应用: 选择程序用户的登录名
2、添加数据类型: 选择 HDFS, 输入路径, 选择包含子文件

idata平台，系统运维-HDFS-查看HDFS目录
1、输入HDFS路径，查看上传的文件

"""


def download_hdfs(hdfs_path, file_path):
    conf_data = tools.conf_data.get_conf_yaml()["test"]
    token = conf_data["idata_token"]
    # 从idata平台 的 HDFS 目录下载文件
    url = conf_data['url_dataservice'] + "/dataservice-gateway/hdfs-api/download"
    # hdfs下载路径
    params = {"path": hdfs_path}
    headers = {
        'authorization': token
    }
    res = requests.get(url, headers=headers, params=params)
    if res.status_code == 200:
        print(res.status_code)
        # 写入文件
        with open(file_path, 'w+') as f:
            f.write(res.text)
    else:
        print(res.text)


def upload_hdfs(hdfs_path, file_data, append_flag='false'):
    conf_data = tools.conf_data.get_conf_yaml()["test"]
    token = conf_data["idata_token"]
    # 上传文件到 idata 平台的 HDFS 目录下
    url = conf_data['url_dataservice'] + "/dataservice-gateway/hdfs-api/upload"
    # hdfs上传路径
    params = {
        "path": hdfs_path,
        "append": append_flag
    }
    headers = {
        'authorization': token,
        'content-type': "application/octet-stream",
    }

    start_time = datetime.now()
    res = requests.post(url, headers=headers, params=params, data=file_data)
    end_time = datetime.now()
    if res.status_code == 200:
        print("本次上传时间: {}秒, 上传文件到 {} 路径下".format(
            (end_time - start_time).total_seconds(),
            hdfs_path
        ))
    else:
        print(res.text)


def batch_upload_hdfs(hdfs_path, file_path):
    """
    文件超过上传大小限制, 使用追加上传
    """
    # 数据限制大小(MB)
    chunk_size = 8
    # 读取文件
    with open(file_path, 'r') as f:
        start_line = 0
        end_line = 30000
        read_data = f.readlines()
        len_data = len(read_data)
        # 默认上传不追加
        append_flag = 'false'
        while True:
            chunk_data = get_file_data(read_data, start_line, end_line, chunk_size)
            # print(chunk_data)
            if append_flag == 'true':
                upload_hdfs(hdfs_path, chunk_data['data'], append_flag)
            else:
                upload_hdfs(hdfs_path, chunk_data['data'])
                append_flag = 'true'
            if end_line > len_data:
                break
            start_line += chunk_data['end'] - chunk_data['start']
            end_line += chunk_data['end'] - chunk_data['start']


def get_file_data(read_data, start_index, end_index, limit_size):
    mb_size = 1024 * 1024
    len_data = len(read_data)
    if end_index > len_data:
        end_index = len_data
    chunk_list = read_data[start_index:end_index]
    chunk = ''
    for item in chunk_list:
        chunk += item
    # 转换为字节
    bytes_data = chunk.encode('utf-8')
    # 数据大小
    bytes_size = bytes_data.__sizeof__() / mb_size
    if bytes_size <= limit_size:
        data_dict = {'start': start_index, 'end': end_index, 'data': bytes_data}
        print('开始行: {}, 结束行: {}'.format(start_index+1, end_index))
        return data_dict
    else:
        end_index -= 2000
        return get_file_data(read_data, start_index, end_index, limit_size)


if __name__ == '__main__':
    file_path_val = "../data/shop_unfreeze_data.csv"
    hdfs_path_val = "/user/yuan.bie/dm/test/shop-order/temp/shop_unfreeze_data.csv"
    # 上传文件
    # upload_hdfs(hdfs_path_val, file_path_val)
    batch_upload_hdfs(hdfs_path_val, file_path_val)
    # 下载文件
    # download_hdfs(hdfs_path_val, file_path_val)
