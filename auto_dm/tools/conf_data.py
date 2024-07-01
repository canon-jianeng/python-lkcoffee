
import yaml


def get_conf_yaml():
    # 读取配置文件
    path_val = '../conf/conf.yml'
    with open(path_val, encoding='utf-8') as f:
        yml_data = yaml.load(f, Loader=yaml.CLoader)
    return yml_data
