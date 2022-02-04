#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 31 21:57:47 2022

@author: willmaethner
"""

import os
import typing
import pandas as pd
import numpy as np
from Data.DataScraper import (get_teams, get_all_teams_stats, get_teams_stats)

def explore(obj):
    if type(obj) is dict:
        explore_dict(obj)
    elif type(obj) is list:
        for x in obj:
            print(x)
    else:
        print(obj)

def explore_dict(dictionary):
    mapped = {}
    
    selection = '.'
    
    while (selection != '') and (selection != 'q'):
        # print options
        for index, k in enumerate(dictionary.keys()):
            mapped[f'{index+1}'] = k
            print(f'[{index+1}] {k}')
            
        selection = input('Selection: ')
        if selection in mapped.keys():
            selection = explore(dictionary[mapped[selection]])
              
    return selection 
        


def main():
    # data = get_teams_stats('clt',2021)
    # print(data.corr())
    
    data = get_all_teams_stats(2021)
    all_offenses = {key:value for key,value in data[2021].items()}
    vertical_stack = pd.concat([x.head(1) for key, x in all_offenses.items()], axis=0)
    correlation = vertical_stack.corr()
    print(correlation[0:3])
    
    # explore(data)

if __name__ == "__main__":
    main()