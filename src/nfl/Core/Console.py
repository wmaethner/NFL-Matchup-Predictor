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
import matplotlib.pyplot as plt


from nfl.Data.DataScraper import Data_Scraper
from nfl.Data.TeamManager import Team_Manager

from nfl.Predicters.Predicters import (Offense_Correlation,  
                                       TensorFlowBasic)
from nfl.Predicters.Analyzer import analyze_predicter


from utilities import (PFR_BASE_URL, start_timer, stop_timer, parse_page, 
                       get_table_by_id, parse_table, parse_page)


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
        

def make_prediction(year, home, away):
    off = Offense_Correlation(year)
    # stats = Team_Stats_Only_Correlation(year)
    # off_def = Offense_Minus_Defense_Correlation(year)
    print(f'Matchup: {home} - {away}')
    print(off.predict_winner(home, away))
    # print(stats.predict_winner(home, away))
    # print(off_def.predict_winner(home, away))

def analyze_predicters(train_years, test_years):
    off = Offense_Correlation(train_years, False)
    both = Offense_Correlation(train_years, True)
    tfb = TensorFlowBasic(train_years, False)
    tfb_both = TensorFlowBasic(train_years, True)
   
    analyze_predicter(off, test_years)
    analyze_predicter(both, test_years)
    analyze_predicter(tfb, test_years)
    analyze_predicter(tfb_both, test_years)

       
def save_stats_to_csvs(years):
    tm = Team_Manager()

    for year in years:   
        data = {}
        for index, t in enumerate(tm.teams):
            data[t.id_num] = tm.get_teams_stats(t.id_num, year, 1)
        
        offense = pd.concat({key: x.iloc[[0]] for key, x in data.items()}, axis=0).reset_index(level=1, drop=True)
        defense = pd.concat({key: x.iloc[[1]] for key, x in data.items()}, axis=0).reset_index(level=1, drop=True)
        
        offense.rename(index={team: tm.get_team(team).name for team in range(32)}, inplace=True)
        defense.rename(index={team: tm.get_team(team).name for team in range(32)}, inplace=True)
        
        offense.to_csv(f'CSVs/{year}_offense.csv')
        defense.to_csv(f'CSVs/{year}_defense.csv')  


def main():
    pd.set_option('display.max_columns', None)
    
    ds = Data_Scraper()
    tm = Team_Manager()
    
   
    # train_years = [2017]
    # test_years = [2017]
    # for i in range(5):
    #     tfb = TensorFlowBasic(train_years)
    #     tfbs = TensorFlowBothStats(train_years)
    #     analyze_predicter(tfb, test_years)
    #     analyze_predicter(tfbs, test_years)
    #     print('========================')
    # return
    
    analyze_predicters([2017,2018,2019,2020,2021], [2020,2021])
    
    return
    
    # print(tfb.train_data)
    # print(len(tfb.train_results))
    tfb = TensorFlowBasic([2017])
    total = 0
    total_right = 0
    schedule = ds.get_schedule(2021)
    for index, row in schedule.iterrows():
        home = tm.get_team_id(row['Home'])
        away = tm.get_team_id(row['Away'])
        results = tfb.predict_winner(home, away, 2021)
        predicted = np.argmax(results)
        actual = 1 if tm.get_team_id(row["Winner/tie"]) == home else 0
        
        total += 1
        total_right += 1 if predicted == actual else 0
        
        # print(f'{row["Home"]} vs {row["Away"]}: Predicted: {predicted} Actual: {actual}')   
    print(f'{total_right}/{total}={total_right/total}')
    
    return
    
    results = tfb.predict_winner(3,4)
    print(results)
    print(results[0][0])
    print('{}: {:2.0f}% vs {}: {:2.0f}%'.format(tm.get_team(3).name,
                                                100*results[0][0],
                                                tm.get_team(4).name,
                                                100*results[0][1]))
    # print(results)
    # predictions = model(x_train[:1]).numpy()
    return
    
    ds = Data_Scraper()
    print(ds.get_schedule(2021))
    return
   
    
   
    



if __name__ == "__main__":
    main()