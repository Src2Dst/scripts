#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import time, os
import subprocess

data = []
queue_name = ('salt-master',)

#取值函数
def fetch_queue_value(queue):
	cmd_lines = 'ps -ef|grep %s|grep -v grep|wc -l' %queue
	child_lines = subprocess.Popen(cmd_lines, shell=True, stdout=subprocess.PIPE)
	lines = int(child_lines.stdout.read().strip())
	
	if lines != 0:
		#找到进程，对cpu/mem占用进行累计
		cmd_proc = "ps -ef|grep %s|grep -v grep|awk '{print $2}'|tr '\n' ','|sed 's#,$##'" %queue
		child_proc = subprocess.Popen(cmd_proc, shell=True, stdout=subprocess.PIPE)
		proc = child_proc.stdout.read().strip()
		
		cmd_value = "top -b -n 1 -p %s|tail -%s|awk '{sum1 += $9; sum2 += $10} END {print sum1,sum2}'" %(proc, lines+1)
		child_value = subprocess.Popen(cmd_value, shell=True, stdout=subprocess.PIPE)
		value = child_value.stdout.read().strip().split()
		return tuple(value)

def create_record(queue, *value):
	for i in range(len(value)):
		record = {}
		if i == 0:
			record['metric'] = 'proc_%s_cpu' %queue
		elif i == 1:
			record['metric'] = 'proc_%s_mem' %queue
		record['endpoint'] = os.uname()[1]
		record['timestamp'] = int(time.time())
		record['step'] = 60
		record['value'] = float(value[i])
		record['counterType'] = 'GAUGE'
		record['tags'] = ''
		data.append(record)
	
for queue in queue_name:
	cmd_lines = 'ps -ef|grep %s|grep -v grep|wc -l' %queue
	child_lines = subprocess.Popen(cmd_lines, shell=True, stdout=subprocess.PIPE)
	lines = int(child_lines.stdout.read().strip())
	
	if lines != 0:
		create_record(queue, *fetch_queue_value(queue))
	
if data:
    print json.dumps(data)