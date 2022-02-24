#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 23 15:47:55 2022

@author: willmaethner
"""
from time import perf_counter

class Metric:
    def __init__(self, key, depth = 0, start = True, root = False):
        self.key = key
        self.active = True if start else False
        self.start = perf_counter() if start else None
        self.sub_metrics = []
        self.root = root
        self.depth = depth
        
    def start(self):
        self.start = perf_counter()
    def stop(self):
        self.stop = perf_counter()
        self.elapsed = self.stop - self.start
        self.active = False
    
    def add_sub_metric(self, metric):
        self.sub_metrics.append(metric)

    def metric_details(self):
        details = {} if self.root else {self.key : {'depth':self.depth, 'times':[self.elapsed]}}


        for m in self.sub_metrics:
            # if not 'subs' in details.keys():
            #     details['subs'] = {}
            sub_details = m.metric_details()
            # print(sub_details)
            for key, item in sub_details.items():
                if not key in details.keys():
                    details[key] = {'depth':item['depth'], 'times':[]}
                    # details['subs'][key] = {'depth':item['depth'], 'times':[]}
                    
                details[key]['times'].extend(item['times'])
                # details['subs'][key]['times'].extend(item['times'])
                
        return details

    # def display_info(self, indent_level = 0):
    #     indent = '  ' * indent_level
    #     sub_indent = '  ' * (indent_level+1)
    #     print(f'{indent}{self.key}: {self.elapsed} s')
        
    #     if self.sub_metrics:
    #         data = {}
    #         for m in self.sub_metrics:
    #             if not m.key in data.keys():
    #                 data[m.key] = []
    #             data[m.key].append(m.elapsed)
                    
    #         for key in data:
    #             print(f'{sub_indent}{key}:')
    #             print(f'{sub_indent}  Count: {len(data[key])}')
    #             print(f'{sub_indent}  Total: {sum(data[key])}')
    #             print(f'{sub_indent}  Average: {sum(data[key])/len(data[key])}')
                
            
    #         print(f'{sub_indent}-------------------------')
    #         for metric in self.sub_metrics:
    #             metric.display_info(indent_level+1)

    # def __repr__(self):
    #     s = f'{self.key}: {self.elapsed} s \n'
    #     s += str(self.sub_metrics)
    #     return s

    # def __str__(self):
    #     return self.__repr__()