#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  6 20:32:15 2022

@author: willmaethner
"""

from nfl.Data.TeamManager import Team_Manager
from nfl.Data.DataScraper import Data_Scraper

def analyze_predicter(predicter, years: list, print_results = True):
    ds = Data_Scraper()
    total = 0
    total_right = 0
    results = {}
    
    tm = Team_Manager()
    
    print("")
    print(f'Analyzing {type(predicter).__name__}')
    print('------------------------')
    
    for year in years:
        year_total = 0
        year_right = 0
        schedule = ds.get_schedule(year)
        
        for index, row in schedule.iterrows():
            home = tm.get_team_id(row['Home'])
            away = tm.get_team_id(row['Away'])
            predicted_winner, _ = predicter.predict_winner(home, away, year) 
            if predicted_winner == tm.get_team_id(row['Winner/tie']):
                year_right += 1
            year_total += 1
        total += year_total
        total_right += year_right
        results[year] = (year_right, year_total)
        # if print_results:
        #     print(f'     {year}: {year_right} / {year_total} = {year_right/year_total}')
      
    if print_results:
        print(f'Overall: {total_right} / {total} = {total_right/total:.1%}')
        for year in years:
            print(f'   {year}: {results[year][0]} / {results[year][1]} = {(results[year][0]/results[year][1]):.1%}')
    return total_right, total, total_right/total