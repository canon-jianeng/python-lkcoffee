#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json
import socket
import telnetlib
import sys
import hashlib
import time


class DubboTelnet(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.__connect_timeout = 10
        self.__read_timeout = 10
        self.__encoding = 'UTF-8'
        self.__finish = 'dubbo>'

    def invoke(self, command):
        try:
            telnet = telnetlib.Telnet(host=self.host, port=self.port, timeout=self.__connect_timeout)
        except socket.error as err:
            print("[host:{} port:{}] {}".format(self.host, self.port, err))
            return

        # 触发Dubbo提示符
        telnet.write(b'\n')
        # 执行命令
        telnet.read_until(self.__finish.encode(), timeout=self.__read_timeout)
        telnet.write(command.encode() + b"\n")
        # 获取结果
        data = ''
        while str(data).find(self.__finish) == -1:
            data = telnet.read_very_eager()
        data = data.decode().split("\n")
        telnet.close()
        return data


def main(cmd, host='127.0.0.1', port=20880):
    conn = DubboTelnet(host, port)
    ret = conn.invoke(cmd)
    print(ret)


if __name__ == "__main__":
    user_name = 'p_supplysystem'
    token_val = '0C9B66DA551A88FCA0E5B9E5D216FD0F'
    service_code = "SmartOrderWhGoodsTotalZtQuery"
    ts = str(int(time.time()))
    sign_val = user_name + service_code + ts + token_val
    sign = hashlib.md5(sign_val.encode('UTF-8')).hexdigest()
    param_val = {
        'type': '0',
        'whDeptIds': '-1',
        'specIds': '364753',
        'startDt': '2023-10-10',
        'endDt': '2023-12-10'
    }
    parameters = {
        "class": "com.luckincoffee.dataservice.base.service.dto.SqlQueryDTO",
        "timeout": 60,
        "params": param_val,
        "userName": user_name,
        "serviceCode": service_code,
        "ts": ts,
        "sign": sign
    }
    data_param = {
        'dubbo_service': 'com.luckincoffee.dataservice.base.service.api.DataQueryRemoteService',
        'dubbo_method': 'queryData',
        'parameters': json.dumps(parameters)
    }
    try:
        cmd = "invoke " + data_param["dubbo_service"] + "." + data_param["dubbo_method"] + "({})".format(
            data_param["parameters"])
        print(cmd + '\n')
        main(cmd, '10.218.41.109', 20880)
    finally:
        sys.exit()
