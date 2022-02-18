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
        data[t.id_num] = tm.get_teams_stats(t.id_num, year, 1)
    return data

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
    stats_normal = stats_normal.fillna(0)
    corr = averaged_stats.corr() 
    win_corr = corr.iloc[0,3:]
    return (win_corr, stats_normal)

def normalized_stats(year, offense = True):
    stats = get_mean_stats([year], 0 if offense else 1)
    normal = (stats-stats.min())/(stats.max()-stats.min())
    return normal.fillna(0)

def get_winner_percentages(home, home_score, away, away_score):
    total = home_score + away_score
    return home if (home_score > away_score) else away, (home_score/total, away_score/total)

class YearsNormalStats:
    def __init__(self, year):
        self.offense = normalized_stats(year)
        self.defense = normalized_stats(year, False)

class PredicterBase:
    def __init__(self, years):
        self.years = years
        self.normalized_stats = {}
        
        for year in years:
            self.normalized_stats[year] = YearsNormalStats(year)

class Offense_Correlation(PredicterBase):
    def __init__(self, years):
        PredicterBase.__init__(self, years)
        
        df_means = get_mean_stats(years, 0)
        win_corr, offense_normal = get_correlation_normalized_stats(df_means)
        
        self.correlations = {}
        self.correlations['Offense'] = win_corr
        
    
    def predict_winner(self, home, away, year):
        offense_normal = self.normalized_stats[year].offense
        
        home_score = 0
        away_score = 0
        for key in self.correlations['Offense'].index:
            home_score += self.correlations['Offense'][key] * offense_normal.loc[home, key]
            away_score += self.correlations['Offense'][key] * offense_normal.loc[away, key]
            
        return get_winner_percentages(home, home_score, away, away_score)
    
class Team_Stats_Only_Correlation:
    def __init__(self, years):
        PredicterBase.__init__(self, years)
        
        df_means_off = get_mean_stats(years, 0)
        df_means_def = get_mean_stats(years, 1)

        offense_corr, offense_normal = get_correlation_normalized_stats(df_means_off)
        defense_corr, defense_normal = get_correlation_normalized_stats(df_means_def)
        
        self.correlations = {}
        self.correlations['Offense'] = offense_corr
        self.correlations['Defense'] = defense_corr

    
    def predict_winner(self, home, away, year):
        offense_normal = self.normalized_stats[year].offense
        defense_normal = self.normalized_stats[year].defense
        
        home_score = 0
        away_score = 0
        for key in self.correlations['Offense'].index:
            home_score += self.correlations['Offense'][key] * offense_normal.loc[home, key]
            home_score += self.correlations['Defense'][key] * defense_normal.loc[home, key]
            away_score += self.correlations['Offense'][key] * offense_normal.loc[away, key]
            away_score += self.correlations['Defense'][key] * defense_normal.loc[away, key]
            
        return get_winner_percentages(home, home_score, away, away_score)
       
class TensorFlowBasic:
    def __init__(self, years):
        self.train_data = []
        self.train_results = []
        self.test_data = []
        self.test_results = []
        
        self.tm = Team_Manager()
        self.stats = {}
        
        ds = Data_Scraper()       
        
        for year in years:    
            offense_normal = normalized_stats(year)
           
            offense_numpy = offense_normal.to_numpy()
            self.stats[year] = offense_numpy
            
            schedule = ds.get_schedule(year)
            for index, row in schedule.iterrows():
                home = self.tm.get_team_id(row['Home'])
                away = self.tm.get_team_id(row['Away'])
                winner = 1 if self.tm.get_team_id(row['Winner/tie']) == home else 0
                
                data = [offense_numpy[home].tolist(), offense_numpy[away].tolist()]           
                
                self.train_data.append(data)
                self.train_results.append(winner)
          
    
        self.model = tf.keras.models.Sequential([
            tf.keras.layers.Flatten(input_shape=(2, len(self.train_data[0][0]))),
            tf.keras.layers.Dense(10, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(2)
            ])
        
        self.model.compile(optimizer='adam',
                      loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                      metrics=['accuracy'])

        self.model.fit(self.train_data, self.train_results, epochs=50, verbose=False)      
        self.probability_model = tf.keras.Sequential([self.model, tf.keras.layers.Softmax()])
        
    def predict_winner(self, home, away, year):
        if not year in self.stats.keys():
            print(f'{year} was not included in data')
            return
        
        data = [self.stats[year][home].tolist(), self.stats[year][away].tolist()]     
        data_exp = (np.expand_dims(data,0))
        
        result = self.probability_model.predict(data_exp)
     
        return home if np.argmax(result) == 1 else away, np.max(result)
        
  
class TensorFlowBothStats:
    def __init__(self, years):
        self.train_data = []
        self.train_results = []
        self.test_data = []
        self.test_results = []
        
        self.tm = Team_Manager()
        self.stats = {}
        
        ds = Data_Scraper()       
        
        for year in years:    
            offense_normal = normalized_stats(year)
            defense_normal = normalized_stats(year, False)
            
            offense_numpy = offense_normal.to_numpy()
            defense_numpy = defense_normal.to_numpy()
            self.stats[year] = {}
            self.stats[year]['Offense'] = offense_numpy
            self.stats[year]['Defense'] = defense_numpy
            
            schedule = ds.get_schedule(year)
            for index, row in schedule.iterrows():
                home = self.tm.get_team_id(row['Home'])
                away = self.tm.get_team_id(row['Away'])
                winner = 1 if self.tm.get_team_id(row['Winner/tie']) == home else 0
                
                data = [offense_numpy[home].tolist(), 
                        defense_numpy[home].tolist(),
                        offense_numpy[away].tolist(),
                        defense_numpy[away].tolist()]           
                
                self.train_data.append(data)
                self.train_results.append(winner)
          
    
        self.model = tf.keras.models.Sequential([
            tf.keras.layers.Flatten(input_shape=(4, len(self.train_data[0][0]))),
            tf.keras.layers.Dense(10, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(2)
            ])
        
        self.model.compile(optimizer='adam',
                      loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                      metrics=['accuracy'])
    
        self.model.fit(self.train_data, self.train_results, epochs=50, verbose=False)      
        self.probability_model = tf.keras.Sequential([self.model, tf.keras.layers.Softmax()])
        
    def predict_winner(self, home, away, year):
        if not year in self.stats.keys():
            print(f'{year} was not included in data')
            return
        
        data = [self.stats[year]['Offense'][home].tolist(), 
                self.stats[year]['Defense'][home].tolist(), 
                self.stats[year]['Offense'][away].tolist(), 
                self.stats[year]['Defense'][away].tolist()]     
        data_exp = (np.expand_dims(data,0))
        
        result = self.probability_model.predict(data_exp)
     
        return home if np.argmax(result) == 1 else away, np.max(result)   
            
        
        
        
    
    
    
    
    
    
    
    
    