
import requests
from auto_dm import tools

"""
定时任务

"""


def login_chronus():
    conf_data = tools.conf_data.get_conf_yaml()["test"]
    login_url = conf_data['url_chronus'] + '/console/auth/login'
    json_data = {
        "loginAccountType": "lucky",
        "username": conf_data['chronus_user'],
        "password": conf_data['chronus_pwd']
    }
    json_header = {
        'Content-Type': 'application/json'
    }
    # 通过 Session 会话管理 Cookies，同一个会话的多个请求可共享 Cookies
    session = requests.session()
    # 登录 chronus 定时任务
    session.post(login_url, headers=json_header, json=json_data).json()
    return dict(session.cookies)


def execute_task(service_name, task_name):
    conf_data = tools.conf_data.get_conf_yaml()["test"]
    # 执行定时任务
    exec_url = conf_data['url_chronus'] + "/console/task/chronus-lucky3/{}/{}/run"
    task_url = exec_url.format(service_name, task_name)
    cookies = login_chronus()
    res = requests.post(task_url, cookies=cookies).json()
    print(res)


if __name__ == '__main__':
    app_name = "luckydataplatform"
    task = "WhStockShortageAlarmTask"
    execute_task(app_name, task)
