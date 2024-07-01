
import time
from datetime import datetime
import requests
from auto_dm import tools

"""
执行 idata 平台上的任务
http://wiki.lkcoffee.com/pages/viewpage.action?pageId=102219825

"""


def execute_task(task_id):
    status_dict = {
        '1': "执行中",
        '2': "执行成功",
        '3': '失败',
        '4': '杀掉任务'
    }
    conf_data = tools.conf_data.get_conf_yaml()["test"]
    # 执行 idata 平台上的任务
    url = conf_data["url_sky_engine"] + "/skyengine-console/taskapi/triggerTask/{}/{}/{}"
    trigger_value = "false"
    operator = conf_data["idata_operator"]
    url = url.format(task_id, trigger_value, operator)
    headers = {
        'Content-Type': 'application/json'
    }
    res = requests.post(url, headers=headers).json()
    start_time = datetime.now()
    print('任务id: {}'.format(task_id))
    if res['statusInfo'] == "SUCCESS":
        res = get_data_version(task_id)
        final_status = res['data']['data'][0]['finalStatus']
        if final_status < 2:
            # 第一次获取任务id
            job_id = res['data']['data'][0]['id']
            while final_status < 2:
                res = get_data_version(task_id)
                res_data = res['data']['data']
                for res_val in res_data:
                    # 获取本次任务id的状态
                    if res_val['id'] == job_id:
                        final_status = res_val['finalStatus']
                        break
                if final_status >= 2:
                    end_time = datetime.now()
                    print('任务运行记录id: {}, 执行状态: {}, 执行时间: {}秒'.format(
                        job_id,
                        status_dict[str(final_status)],
                        # 执行时间
                        (end_time - start_time).total_seconds()
                    ))
                    break
                print('任务运行记录id: {}, 执行状态: {}'.format(job_id, status_dict[str(final_status)]))
                time.sleep(10)
        else:
            job_id = res['data']['data'][0]['id']
            print('任务运行记录id: {}, 执行状态: {}'.format(job_id, status_dict[str(final_status)]))
    else:
        print(res)


def get_data_version(task_id):
    conf_data = tools.conf_data.get_conf_yaml()["test"]
    # 查询 idata 平台上的任务运行记录
    url = conf_data["url_sky_engine"] + "/skyengine-console/taskapi/listDataVersion"
    param = {
        "page": 1,
        "rows": 10,
        "taskId": task_id
    }
    res = requests.get(url, params=param).json()
    return res


if __name__ == '__main__':
    execute_task(4130)
