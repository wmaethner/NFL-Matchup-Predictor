#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  6 20:30:48 2022

@author: willmaethner
"""

import pandas as pd

from Data.TeamManager import Team_Manager

from Data.DataScraper import (get_teams, get_all_teams_stats, get_teams_stats, get_team_id)


def get_all_stats1(year):
    tm = Team_Manager()
    data = {}
    for t in tm.teams:
        data[t.id_num] = tm.get_teams_stats(t.id_num, year)
    return data

def get_all_stats(year):
    data = get_all_teams_stats(year)
    return {get_team_id(key):value for key,value in data[year].items()}

def concat_year_stats(yearly_stats, row_index):
    all_stats = pd.DataFrame()
    for stats in yearly_stats:
        all_stats = pd.concat((all_stats, 
                               pd.concat({key: x.iloc[[row_index]] for key, x in stats.items()}, axis=0)))
    return all_stats.reset_index(level=1, drop=True)

def get_mean_stats(years, row_index):
    year_stats = []
    for year in years:
        year_stats.append(get_all_stats(year))
    all_stats = concat_year_stats(year_stats, row_index)
    by_row_index = all_stats.groupby(all_stats.index)
    return by_row_index.mean()

def get_correlation_normalized_stats(averaged_stats):
    stats_normal = (averaged_stats-averaged_stats.min())/(averaged_stats.max()-averaged_stats.min())
    corr = averaged_stats.corr() 
    win_corr = corr.iloc[0,3:]
    return (win_corr, stats_normal)

def get_winner_percentages(home, home_score, away, away_score):
    total = home_score + away_score
    return home if (home_score > away_score) else away, (home_score/total, away_score/total)

class Offense_Correlation:
    def __init__(self, years):
        self.years = years
        self.team_offense_scores = {}
        
        df_means = get_mean_stats(years, 0)

        win_corr, offense_normal = get_correlation_normalized_stats(df_means)
        
        for team in offense_normal.index:
            total = 0
            for key in win_corr.index:
                total += win_corr[key] * offense_normal.loc[team, key]
            self.team_offense_scores[team] = total
    
    def predict_winner(self, home, away):
        home_score = self.team_offense_scores[get_team_id(home)]
        away_score = self.team_offense_scores[get_team_id(away)]
            
        return get_winner_percentages(home, home_score, away, away_score)
    
class Team_Stats_Only_Correlation:
    def __init__(self, years):
        self.years = years
        self.team_scores = {}
        
        df_means_off = get_mean_stats(years, 0)
        df_means_def = get_mean_stats(years, 1)

        offense_corr, offense_normal = get_correlation_normalized_stats(df_means_off)
        defense_corr, defense_normal = get_correlation_normalized_stats(df_means_def)
        
        
        for team in offense_normal.index:
            total = 0
            for key in offense_corr.index:
                total += offense_corr[key] * offense_normal.loc[team, key]
                total += defense_corr[key] * defense_normal.loc[team, key]
            self.team_scores[team] = total
    
    def predict_winner(self, home, away):
        home_score = self.team_scores[get_team_id(home)]
        away_score = self.team_scores[get_team_id(away)]
            
        return get_winner_percentages(home, home_score, away, away_score)
    
# Pretty sure this just ends up being the same as the All Stats one mathematically
# The results always end up the exact same. Probably should remove.
class Offense_Minus_Defense_Correlation:
    def __init__(self, years):
        self.years = years
        self.team_offense_scores = {}
        self.team_defense_scores = {}
        
        df_means_off = get_mean_stats(years, 0)
        df_means_def = get_mean_stats(years, 1)
        
        offense_corr, offense_normal = get_correlation_normalized_stats(df_means_off)
        defense_corr, defense_normal = get_correlation_normalized_stats(df_means_def)
        
        for team in offense_normal.index:
            total_off = 0
            total_def = 0
            for key in offense_corr.index:
                total_off +=  offense_corr[key] * offense_normal.loc[team, key]
                total_def +=  defense_corr[key] * defense_normal.loc[team, key]
            self.team_offense_scores[team] = total_off
            self.team_defense_scores[team] = total_def
    
    def predict_winner(self, home, away):
        home_score = self.team_offense_scores[get_team_id(home)] - self.team_defense_scores[get_team_id(away)]
        away_score = self.team_offense_scores[get_team_id(away)] - self.team_defense_scores[get_team_id(home)]
            
        return get_winner_percentages(home, home_score, away, away_score)