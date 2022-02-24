#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 23 15:06:56 2022

@author: willmaethner

"""

from nfl.Performance.Metric import Metric

metric_stack = [Metric('root', root=True)]

def start_metric(key):
    metric_stack.append(Metric(key, depth=len(metric_stack)))

def stop_metric():
    metric = metric_stack.pop()
    metric.stop()
    parent = metric_stack[-1]
    parent.add_sub_metric(metric)
    return metric

def display_metrics():
    metric = metric_stack[0]
    details = metric.metric_details()
    
    for key, item in details.items():
        # print(f'{key} - {item["depth"]}:')
        print(f'{key}:')
        print(f'  Count: {len(item["times"])}')
        print(f'  Total: {sum(item["times"])}')
        print(f'  Average: {sum(item["times"])/len(item["times"])}')

