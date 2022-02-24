#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  6 20:32:15 2022

@author: willmaethner
"""

from nfl.Data.TeamManager import Team_Manager
from nfl.Data.DataScraper import Data_Scraper
from nfl.Core.utilities import (printProgressBar)
from nfl.Performance.Performance import (start_metric, stop_metric)

def analyze_predicter(predicter, years: list, print_results = True):
    ds = Data_Scraper()
    total = 0
    total_right = 0
    results = {}
    results_by_week = {}
    
    tm = Team_Manager()
    
    print("")
    print(f'Analyzing {type(predicter).__name__}')
    print('------------------------')
    
    for index, year in enumerate(years):
        start_metric('Analyze year')
        results_by_week[year] = {}
        
        year_total = 0
        year_right = 0
        schedule = ds.get_schedule(year)
        
        printProgressBar(0, len(schedule), prefix = 'Schedule Progress:', suffix = 'Complete', length = 50)
        for index in range(len(schedule)):
            row = schedule.iloc[index,:]
            week = row['Week']
            
            if not week in results_by_week[year].keys():
                results_by_week[year][week] = {'right':0,'total':0}

            printProgressBar(index+1, len(schedule), prefix = 'Schedule Progress:', suffix = 'Complete', length = 50)                    
            home = tm.get_team_id(row['Home'])
            away = tm.get_team_id(row['Away'])
            start_metric('Predict winner')
            predicted_winner, _ = predicter.predict_winner(home, away, year, week) 
            stop_metric()
            if predicted_winner == tm.get_team_id(row['Winner/tie']):
                year_right += 1
                results_by_week[year][week]['right'] += 1
            
            year_total += 1
            results_by_week[year][week]['total'] += 1
            
        total += year_total
        total_right += year_right
        results[year] = (year_right, year_total)
        stop_metric()
      
    if print_results:
        print(f'Overall: {total_right} / {total} = {total_right/total:.1%}')
        for year in years:
            print(f'   {year}: {results[year][0]} / {results[year][1]} = {(results[year][0]/results[year][1]):.1%}')
            for week in results_by_week[year]:
                print(f'     {week}: {results_by_week[year][week]["right"]} / {results_by_week[year][week]["total"]} = {(results_by_week[year][week]["right"]/results_by_week[year][week]["total"]):.1%}')
    
    overall_results = {'by_year':results,'by_year_and_week':results_by_week,'overall':{'right':total_right,'total':total}}
    return overall_results
    # return total_right, total, total_right/total