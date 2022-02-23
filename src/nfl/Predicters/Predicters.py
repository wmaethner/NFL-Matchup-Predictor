#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  6 20:30:48 2022

@author: willmaethner
"""

import pandas as pd
import tensorflow as tf
import numpy as np

from nfl.Core.utilities import (printProgressBar, start_timer, stop_timer)
from nfl.Data.TeamManager import Team_Manager
from nfl.Data.DataScraper import Data_Scraper

def get_all_stats(year):
    tm = Team_Manager()
    data = {}
    # printProgressBar(0, len(tm.teams), prefix = 'Progress:', suffix = 'Complete', length = 50)
    for index, t in enumerate(tm.teams):
        # printProgressBar(index + 1, len(tm.teams), prefix = 'Progress:', suffix = 'Complete', length = 50)
        data[t.id_num] = tm.get_teams_season_stats(t.id_num, year)
    return data

def concat_year_stats(yearly_stats, row_index):
    all_stats = pd.DataFrame()
    for stats in yearly_stats:
        all_stats = pd.concat((all_stats, 
                               pd.concat({key: x.loc[[row_index]] for key, x in stats.items()}, axis=0)))
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
    stats_normal.fillna(0, inplace=True)
    corr = stats_normal.corr()
    print(corr)
    win_corr = corr.iloc[0,3:]
    return (win_corr, stats_normal)

def normalized_stats(year, offense = True):
    stats = get_mean_stats([year], 'Offense' if offense else 'Defense')
    normal = (stats-stats.min())/(stats.max()-stats.min())
    return normal.fillna(0)

def get_winner_percentages(home, home_score, away, away_score):
    total = home_score + away_score
    return home if (home_score > away_score) else away, (home_score/total, away_score/total)

class YearsNormalStats:
    def __init__(self, year):
        self.offense = normalized_stats(year)
        self.defense = normalized_stats(year, False)
        
    def get_normals(self):
        return (self.offense, self.defense)
    
    def get_normals_as_numpy(self):
        return (self.offense.to_numpy(), self.defense.to_numpy())

class Correlations:
    def __init__(self, years):
        df_means_off = get_mean_stats(years, 'Offense')
        df_means_def = get_mean_stats(years, 'Defense')

        offense_corr, offense_normal = get_correlation_normalized_stats(df_means_off)
        defense_corr, defense_normal = get_correlation_normalized_stats(df_means_def)
        
        self.offense = offense_corr
        self.defense = defense_corr
    
    def get_corrs(self):
        return (self.offense, self.defense)

class PredicterBase:
    def __init__(self, years, include_defense):
        self.years = years
        self.include_defense = include_defense
        self.normalized_stats = {}
        
        for year in years:
            self.normalized_stats[year] = YearsNormalStats(year)

class Offense_Correlation(PredicterBase):
    def __init__(self, years, include_defense):
        PredicterBase.__init__(self, years, include_defense)
        self.correlations = Correlations(years)     
    
    def predict_winner(self, home, away, year):
        if year not in self.normalized_stats.keys():
            self.normalized_stats[year] = YearsNormalStats(year)
            
        offense_normal, defense_normal = self.normalized_stats[year].get_normals()
        offense_corr, defense_corr = self.correlations.get_corrs()
        
        home_score = 0
        away_score = 0
        for key in offense_corr.index:
            home_score += offense_corr[key] * offense_normal.loc[home, key]
            away_score += offense_corr[key] * offense_normal.loc[away, key]
            if self.include_defense:
                home_score += defense_corr[key] * defense_normal.loc[home, key]
                away_score += defense_corr[key] * defense_normal.loc[away, key]              
            
        return get_winner_percentages(home, home_score, away, away_score)
        
 
class TensorFlowBasic(PredicterBase):
    def __init__(self, years, include_defense):
        PredicterBase.__init__(self, years, include_defense)
        
        train_data = []
        train_results = []
        # self.test_data = []
        # self.test_results = []
        
        tm = Team_Manager()      
        ds = Data_Scraper()       
        
        for year in years:    
            offense_normal, defense_normal = self.normalized_stats[year].get_normals_as_numpy()
            
            schedule = ds.get_schedule(year)
            for index, row in schedule.iterrows():
                home = tm.get_team_id(row['Home'])
                away = tm.get_team_id(row['Away'])
                winner = 1 if tm.get_team_id(row['Winner/tie']) == home else 0
                
                data = [offense_normal[home].tolist(), offense_normal[away].tolist()]   
                if self.include_defense:
                    data.insert(1, defense_normal[home].tolist())
                    data.append(defense_normal[away].tolist())
                
                train_data.append(data)
                train_results.append(winner)    
    
        self.model = tf.keras.models.Sequential([
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(2)
            ])
        
        self.model.compile(optimizer='adam',
                      loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                      metrics=['accuracy'])

        self.model.fit(train_data, train_results, epochs=50, verbose=False)      
        self.probability_model = tf.keras.Sequential([self.model, tf.keras.layers.Softmax()])
        
    def predict_winner(self, home, away, year):     
        if year not in self.normalized_stats.keys():
            self.normalized_stats[year] = YearsNormalStats(year)
            
        offense_normal, defense_normal = self.normalized_stats[year].get_normals_as_numpy()
        data = [offense_normal[home].tolist(), offense_normal[away].tolist()]     
        
        if self.include_defense:
            data.insert(1, defense_normal[home].tolist())
            data.append(defense_normal[away].tolist())
        
        data_exp = (np.expand_dims(data,0))
        
        result = self.probability_model.predict(data_exp)
        
        return home if np.argmax(result) == 1 else away, np.max(result)
    
    
    
    
    
    
    
    
    