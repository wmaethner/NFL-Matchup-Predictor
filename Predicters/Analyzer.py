#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  6 20:32:15 2022

@author: willmaethner
"""

from Data.DataScraper import (get_teams, get_all_teams_stats, get_teams_stats, get_schedule)


def analyze_predicter(predicter, years: list, print_results = True):
    total = 0
    total_right = 0
    
    for year  in years:
        year_total = 0
        year_right = 0
        schedule = get_schedule(year)
        
        for index, row in schedule.iterrows():
            home = row['Home']
            away = row['Away']
            predicted_winner, _ = predicter.predict_winner(home, away) 
            if predicted_winner == row['Winner/tie']:
                year_right += 1
            year_total += 1
        total += year_total
        total_right += year_right
        if print_results:
            print(f'     {year}: {year_right} / {year_total} = {year_right/year_total}')
      
    if print_results:
        print(f'Overall: {total_right} / {total} = {total_right/total}')
    return total_right, total, total_right/total