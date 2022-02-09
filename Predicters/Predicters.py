#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  6 20:30:48 2022

@author: willmaethner
"""

import pandas as pd
from Data.DataScraper import (get_teams, get_all_teams_stats, get_teams_stats)


def get_all_stats(year):
    data = get_all_teams_stats(year)
    return {key:value for key,value in data[year].items()}

def get_correlation_normalized_stats(all_stats, row_index):
    stacked_stats = pd.concat({key: x.iloc[[row_index]] for key, x in all_stats.items()}, axis=0)
    stacked_stats = stacked_stats.reset_index(level=1, drop=True)
    stats_normal = (stacked_stats-stacked_stats.min())/(stacked_stats.max()-stacked_stats.min())
    corr = stacked_stats.corr() 
    win_corr = corr.iloc[0,3:]
    return (win_corr, stats_normal)

def get_winner_percentages(home, home_score, away, away_score):
    total = home_score + away_score
    return home if (home_score > away_score) else away, (home_score/total, away_score/total)

class Offense_Correlation:
    def __init__(self, year):
        self.year = year
        self.team_offense_scores = {}

        all_stats = get_all_stats(year)
        win_corr, offense_normal = get_correlation_normalized_stats(all_stats, 0)
        
        for team in offense_normal.index:
            total = 0
            for key in win_corr.index:
                total += win_corr[key] * offense_normal.loc[team, key]
            self.team_offense_scores[team] = total
    
    def predict_winner(self, home, away):
        home_score = self.team_offense_scores[home]
        away_score = self.team_offense_scores[away]
            
        return get_winner_percentages(home, home_score, away, away_score)
    
class Team_Stats_Only_Correlation:
    def __init__(self, year):
        self.year = year
        self.team_scores = {}
        
        all_stats = get_all_stats(year)
        offense_win_corr, offense_normal = get_correlation_normalized_stats(all_stats, 0)
        defense_win_corr, defense_normal = get_correlation_normalized_stats(all_stats, 1)
        
        for team in offense_normal.index:
            total = 0
            for key in offense_win_corr.index:
                total += offense_win_corr[key] * offense_normal.loc[team, key]
                total += defense_win_corr[key] * defense_normal.loc[team, key]
            self.team_scores[team] = total
    
    def predict_winner(self, home, away):
        home_score = self.team_scores[home]
        away_score = self.team_scores[away]
            
        return get_winner_percentages(home, home_score, away, away_score)
    
class Offense_Minus_Defense_Correlation:
    def __init__(self, year):
        self.year = year
        self.team_offense_scores = {}
        self.team_defense_scores = {}
        
        all_stats = get_all_stats(year)
        offense_win_corr, offense_normal = get_correlation_normalized_stats(all_stats, 0)
        defense_win_corr, defense_normal = get_correlation_normalized_stats(all_stats, 1)
        
        for team in offense_normal.index:
            total_off = 0
            total_def = 0
            for key in offense_win_corr.index:
                total_off += offense_win_corr[key] * offense_normal.loc[team, key]
                total_def += defense_win_corr[key] * defense_normal.loc[team, key]
            self.team_offense_scores[team] = total_off
            self.team_defense_scores[team] = total_def
    
    def predict_winner(self, home, away):
        home_score = self.team_offense_scores[home] - self.team_defense_scores[away]
        away_score = self.team_offense_scores[away] - self.team_defense_scores[home]
            
        return get_winner_percentages(home, home_score, away, away_score)