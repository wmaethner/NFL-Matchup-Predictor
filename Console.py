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
from Predicters.Predicters import (Offense_Correlation, Team_Stats_Only_Correlation, 
                                   Offense_Minus_Defense_Correlation)
from Predicters.Analyzer import analyze_predicter

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
    # year = 2021
    # data = get_all_teams_stats(year)
    # explore(data)
    # return
    
    predicters = []
    for year in [2020,2021]:
        predicters.append(Offense_Correlation(year))
        
    print("Offense Correlation")
    for predicter in predicters:
        analyze_predicter(predicter)

    predicters = []
    for year in [2020,2021]:
        predicters.append(Team_Stats_Only_Correlation(year))
        
    print("Team Stats Correlation")
    for predicter in predicters:
        analyze_predicter(predicter)

    predicters = []
    for year in [2020,2021]:
        predicters.append(Offense_Minus_Defense_Correlation(year))
        
    print("Offense Minus Defense Correlation")
    for predicter in predicters:
        analyze_predicter(predicter)

    return


if __name__ == "__main__":
    main()