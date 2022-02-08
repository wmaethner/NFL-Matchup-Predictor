#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  6 20:30:48 2022

@author: willmaethner
"""

import pandas as pd
from Data.DataScraper import (get_teams, get_all_teams_stats, get_teams_stats)



class Offense_Correlation:
    def __init__(self, year):
        self.year = year
        self.team_offense_scores = {}
        
        data = get_all_teams_stats(year)
        all_offenses = {key:value for key,value in data[year].items()}
        vertical_stack = pd.concat({key: x.head(1) for key, x in all_offenses.items()}, axis=0)
        vertical_stack = vertical_stack.reset_index(level=1, drop=True)
        offense_normal = (vertical_stack-vertical_stack.min())/(vertical_stack.max()-vertical_stack.min())
        correlation = vertical_stack.corr()
        win_corr = correlation.iloc[0,3:]
        
        for team in offense_normal.index:
            total = 0
            for key in win_corr.index:
                total += win_corr[key] * offense_normal.loc[team, key]
            self.team_offense_scores[team] = total
    
    def predict_winner(self, home, away):
        home_score = self.team_offense_scores[home]
        away_score = self.team_offense_scores[away]
            
        total = home_score + away_score
        return home if (home_score > away_score) else away, (home_score/total, away_score/total)
    