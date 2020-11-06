# -*- coding: utf-8 -*-

import os
import requests
import json
from datetime import datetime
import sqlite3
import subprocess

def alert_custom_dinging(str_info):
#    url = 'https://oapi.dingtalk.com/robot/send?access_token=ba0b0ecab254e812575644cb6358bdf415daf09f3b60fa141d8c886dd1963ef6'
    url = 'https://oapi.dingtalk.com/robot/send?access_token=6be3c72b4202f60b96b83d4b2e74dfa9f9d5942261b135a1ac37c3619ae9abe9'

    headers = {
        'Content-Type': 'application/json;charset=utf-8'
    }
    formdata = {
        "msgtype": "text",
        "text": {
            "content": str_info
        }
    }
    json_data = json.dumps(formdata).encode("utf-8")
    hhh = requests.post(url=url, data=json_data, headers=headers)
    print(hhh.text)

def datetime_to_timestamp(init_time):
    current_timestamp = float(datetime.strptime(init_time, '%Y-%m-%d %H:%M:%S').timestamp())
    return current_timestamp


def timestamp_to_datetime(init_timestamp):
    current_time = datetime.fromtimestamp(init_timestamp)
    return current_time

def monitor_node_status():
    creat_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    node_list = os.popen('/usr/local/bin/kubectl get nodes | grep -v NAME').readlines()
    for i in node_list:
        j = i.replace('\n', '').split()
        if j[1] != 'Ready':
            node_info = r'''【生产k8s集群节点异常告警】
节点名称：%s
节点状态：%s
节点运行时间：%s
告警时间：%s
            ''' % (j[0], j[1], j[3], creat_time)
            alert_custom_dinging(node_info)
            print(node_info)

def pod_ip_repeat():
    creat_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ip_list = os.popen("/usr/local/bin/kubectl get pod --all-namespaces -o wide | grep -Ev '(arms-prom|kruise-system|kube-system|kube-system-inner|kube-system-office|IP)'| awk '{print $7}' | sort | uniq -c | sort -rn | awk '$1>1 {print $0}' | head -n3 | grep -Ev 'none'").readlines()
    for i in ip_list:
        repeat_app_list = []
        repeat_pod_list = []
        j = i.replace('\n', '').split()
        repeat_ip = j[1]
        repeat_pod = os.popen("kubectl get pod --all-namespaces -o wide | grep %s" % repeat_ip).readlines()
        for m in repeat_pod:
            n = m.replace('\n', '').split()
            repeat_app_list.append(n[0])
            repeat_pod_list.append(n[1])
        repeat_info = r'''【生产k8s集群重复IP告警】
重复IP：%s
受影响应用：%s
受影响pod：%s
告警时间：%s
        ''' % (j[1], repeat_app_list, repeat_pod_list, creat_time)
        alert_custom_dinging(repeat_info)
        print(repeat_info)

def monitor_pod_resource():
    creat_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pending_list = subprocess.getoutput('kubectl get pod --all-namespaces | grep 0/2')
    if pending_list:
        for i in pending_list.split('\n'):
            j = i.split()
            pod_status_info = r'''【生产k8s集群pod异常告警】
应用名称：%s
pod名称：%s
ready：%s
status：%s
运行时间：%s
告警时间：%s
                            ''' % (j[0], j[1], j[2], j[3], j[5], creat_time)
            alert_custom_dinging(pod_status_info)
            print(pod_status_info)
    else:
        print('resource is enough')

def monitor_pod_status():
    creat_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    con = sqlite3.connect("POD.db")
    cur = con.cursor()
    create_table = "create table if not exists ABNORMAL_POD(appName varchar(20) ,podName varchar(20) primary key ,ready varchar(20) ,status varchar(20) ,restarts varchar(20) ,age varchar(20),count integer ,ct timestamp)"
    cur.execute(create_table)
    insert_sql = 'insert into ABNORMAL_POD values(?,?,?,?,?,?,?,?)'
    # l1 = [
    #     'automation-distribute              cpaas-automation-distribute-stage-pod-0                           1/2     Running            3          142d\n',
    #     'founder-sto                        cpaas-founder-sto-stage-pod-0                                     1/2     CrashLoopBackOff   41373      157d\n']

    l1 = os.popen('/usr/local/bin/kubectl get pod --all-namespaces | grep 1/2 | grep -v NAME').readlines()
    num = 1
    for i in l1:
        j = i.replace("\n", "").split()
        try:
            cur.execute(insert_sql, (j[0], j[1], j[2], j[3], j[4], j[5], num, creat_time))
        except Exception as e:

            init_count = int(cur.execute('select count from ABNORMAL_POD where podName="%s"' % (j[1],)).fetchone()[0])
            count = init_count + num
            cur.execute('update ABNORMAL_POD set count=%s where podName="%s"' % (count, j[1]))
            cur.execute('update ABNORMAL_POD set ct="%s" where podName="%s"' % (creat_time, j[1]))
            if count >= 5:
                pod_status_info = r'''【生产k8s集群pod异常告警】
应用名称：%s
pod名称：%s
ready：%s
status：%s
运行时间：%s
告警时间：%s
                ''' % (j[0], j[1], j[2], j[3], j[5], creat_time)
                print(pod_status_info)
                alert_custom_dinging(pod_status_info)
            # print('ERROR:', e)
    cur.execute('delete from ABNORMAL_POD where ct!="%s"' % creat_time)
    con.commit()
    cur.close()
    con.close()


if __name__ == '__main__':
    monitor_node_status()
    pod_ip_repeat()
    monitor_pod_status()
    monitor_pod_resource()
