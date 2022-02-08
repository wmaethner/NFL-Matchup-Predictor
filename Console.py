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

from Data.DataScraper import (get_teams, get_all_teams_stats, get_teams_stats, get_schedule)
from Predictors.Predictors import Offense_Correlation
from Predictors.Analyzer import analyze_predicter

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
    pd.set_option('display.max_columns', None)
    
    # explore(get_schedule(2021))
    
    # return
    predicters = []
    for year in [2020,2021]:
        predicters.append(Offense_Correlation(year))

    for predicter in predicters:
        analyze_predicter(predicter)

    # print(predictor.predict_winner("Arizona Cardinals", "Atlanta Falcons"))
    return
    
    
    
    
    data = get_all_teams_stats(2021)
    all_offenses = {key:value for key,value in data[2021].items()}
    vertical_stack = pd.concat({key: x.head(1) for key, x in all_offenses.items()}, axis=0)
    vertical_stack = vertical_stack.reset_index(level=1, drop=True)
    cols = ['PF', 'Yds']
    offense_normal = (vertical_stack-vertical_stack.min())/(vertical_stack.max()-vertical_stack.min())
    correlation = vertical_stack.corr()
    win_corr = correlation.iloc[0,3:]
    
    for key in win_corr.index:
        print(key)
        
    for team in offense_normal.index:
        total = 0
        for key in win_corr.index:
            total += win_corr[key] * offense_normal.loc[team, key]
        print(f'{team} - {total}')


if __name__ == "__main__":
    main()