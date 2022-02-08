#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  6 20:32:15 2022

@author: willmaethner
"""

from Data.DataScraper import (get_teams, get_all_teams_stats, get_teams_stats, get_schedule)


def analyze_predicter(predicter):
    total = 0
    total_right = 0
    year = predicter.year 
    schedule = get_schedule(year)
    
    for index, row in schedule.iterrows():
        home = row['Home']
        away = row['Away']
        predicted_winner, _ = predicter.predict_winner(home, away) 
        if predicted_winner == row['Winner/tie']:
            total_right += 1
        total += 1
        
    print(f'{year}: {total_right} / {total} = {total_right/total}')