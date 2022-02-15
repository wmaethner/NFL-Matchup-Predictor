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



from Data.DataScraper import (get_teams, get_all_teams_stats, get_teams_stats, get_schedule,
                              get_team_id, Data_Scraper)
from Predicters.Predicters import (Offense_Correlation, Team_Stats_Only_Correlation, 
                                   Offense_Minus_Defense_Correlation)
from Predicters.Analyzer import analyze_predicter
from Data.TeamManager import Team_Manager

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
    stats = Team_Stats_Only_Correlation(year)
    off_def = Offense_Minus_Defense_Correlation(year)
    print(f'Matchup: {home} - {away}')
    print(off.predict_winner(home, away))
    print(stats.predict_winner(home, away))
    print(off_def.predict_winner(home, away))

def analyze_predicters(data_year):
    print(f'Data from year {data_year}')
    off = Offense_Correlation([data_year])
    stats = Team_Stats_Only_Correlation(data_year)
    off_def = Offense_Minus_Defense_Correlation(data_year)
    
    for year in range(2019, 2022):
        print(f'{year}')
        analyze_predicter(off, year)
        analyze_predicter(stats, year)
        analyze_predicter(off_def, year)
        


def main():
    pd.set_option('display.max_columns', None)
    
    # ds = Data_Scraper()
    # stats = ds.get_teams_stats('crd',2021,1)
    # print(stats)
    # df = pd.DataFrame(stats).T
    # df.columns = ds.data_columns()
    # print(df)
    
    # tm = Team_Manager()
    # print(tm.get_teams_stats(1,2021,1))
    
    # url = PFR_BASE_URL + f"/teams/crd/2021.htm"
    # soup = parse_page(url)
    # table = get_table_by_id(soup, 'team_stats')
    # stats = parse_table(table)
    # print(stats)
    
    # stats = get_teams_stats('crd', 2021, True)
    # print(stats)
    
    
    return
    
    # for year in range(2019, 2022):
    #     analyze_predicters(year)
    # analyze_predicters(2021)
    
    # x = [1,2,3,4]
    # y = [3, 8, 1, 10]
      
    # df = pd.DataFrame(y, index=x, columns=['One'])
    # print(df)
    # y = [5, 1, 2, 5]
    # # df = df.append(pd.DataFrame(y, index=x, columns=['Two']))
    # df.insert(len(df.columns), 'Two', y)
    # print(df)
    # df.plot(y=['One','Two'], kind="bar")

    # return
    # df.plot()
    # # plot lines
    # plt.bar(x,y, label = "line 1")
    # y = np.array([5, 1, 2, 5])
    # plt.bar(x,y, label = "line 2")
    
    # # plt.plot(x, np.sin(x), label = "curve 1")
    # # plt.plot(x, np.cos(x), label = "curve 2")
    # plt.legend()
    # plt.show()
    # return
    
    
    five_years = list(range(2017,2022))
    result_df = pd.DataFrame()
    off_corr_stats = []
    all_stats_corr_stats = []
    for rng in range(0, 10):
        print(rng)
        years = list(range(2021-rng, 2022))
        off_corr = Offense_Correlation(years)
        both_corr = Team_Stats_Only_Correlation(years)
        # difference_corr = Offense_Minus_Defense_Correlation(years)
        
        _,_,percentage = analyze_predicter(off_corr, five_years, False)
        off_corr_stats.append(percentage)
        
        _,_,percentage = analyze_predicter(both_corr, five_years, False)
        all_stats_corr_stats.append(percentage)

        # _,_,percentage = analyze_predicter(difference_corr, five_years, False)
        # diff_corr_stats.append(percentage)
    
    results = {'Offense Correlation': off_corr_stats, 
               'All Stats Correlation': all_stats_corr_stats}
    result_df = pd.DataFrame(results)
    result_df.plot(y=['Offense Correlation',
                      'All Stats Correlation'], ylim=[0.5,0.7])
    return 
    
    

    off = Offense_Correlation([2019,2020,2021])
    off1 = Offense_Correlation([2021])
    print('2020')
    analyze_predicter(off, 2020)
    analyze_predicter(off1, 2020)
    print('2021')
    analyze_predicter(off, 2021)
    analyze_predicter(off1, 2021)
    return
    
    # for years in [[2021], [2020,2021], [2019,2020,2021]]:
    #     off = Offense_Correlation(years)
    #     for year in [2019,2020,2021]:
    #         analyze_predicter(off, year)
            
    # return
    
    # teams = get_teams()
    # for x in teams:
    #     print(f'{x.id_num} - {x.name} - {x.aliases}')
    # # print(teams)
    
    # # make_prediction(2021, 'Los Angeles Rams', 'Cincinnati Bengals')
    # return
    
    
    
    
    predicters = []
    years = [2019, 2020, 2021]
    for year in years:
        predicters.append(Offense_Correlation(year))
        
    print("Offense Correlation")
    for predicter in predicters:
        analyze_predicter(predicter)

    predicters = []
    for year in years:
        predicters.append(Team_Stats_Only_Correlation(year))
        
    print("Team Stats Correlation")
    for predicter in predicters:
        analyze_predicter(predicter)

    predicters = []
    for year in years:
        predicters.append(Offense_Minus_Defense_Correlation(year))
        
    print("Offense Minus Defense Correlation")
    for predicter in predicters:
        analyze_predicter(predicter)

    # print(predictor.predict_winner("Arizona Cardinals", "Atlanta Falcons"))
    return


if __name__ == "__main__":
    main()