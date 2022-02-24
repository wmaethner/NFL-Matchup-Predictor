#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 14 15:52:01 2022

@author: willmaethner
"""

import pandas as pd

from nfl.Core.utilities import (PFR_BASE_URL, parse_page, get_table_by_id, 
                                get_table_body_rows, save_obj, load_obj, 
                                file_exists, start_timer, stop_timer, 
                                printProgressBar)
from nfl.Data.DataScraper import Data_Scraper
from nfl.Performance.Performance import (start_metric, stop_metric)

class Team:
    def __init__(self, team_tag):
        self.id_num = 1
        self.name = team_tag.a.get_text()
        self.abbr = team_tag.a.get('href').split('/')[-2]
        self.aliases = []
        
    def __repr__(self):
        return f"{self.name} - {self.abbr}"
    
    def __str__(self):
        return f"{self.name} - {self.abbr}"
    
    def set_id(self, id_num):
        self.id_num = id_num
        
    def add_alias(self, alias):
        self.aliases.append(alias)

class Team_Manager:
    def __init__(self):
        self.teams = []
        self.data_scraper = Data_Scraper()
        self.load_teams()
        self.cache = {}

        
    def load_teams(self):
        if file_exists('teams.pkl'):
            self.teams = load_obj('teams.pkl')
            return
        
        soup = parse_page(PFR_BASE_URL + '/teams/')
        rows = get_table_body_rows(soup, 'teams_active')
        
        current = Team(rows[0].find('th'))
        for x in rows[1:]:
            th_tag = x.find('th')
            classes = x.attrs.get('class')
            if (not classes is None) and ('partial_table' in classes):
                current.add_alias(th_tag.get_text())
            else:
                self.teams.append(current)
                current = Team(th_tag)
        self.teams.append(current)    

        for index, t in enumerate(self.teams):
            t.set_id(index)
            
        save_obj('teams.pkl', self.teams)
    
    def get_team_id(self, name_or_alias):
        for t in self.teams:
            options = [x for x in t.aliases]
            options.append(t.name)
            if name_or_alias in options:
                return t.id_num
    
    def get_team(self, team_id):
        for t in self.teams:
            if t.id_num == team_id:
                return t
        else:
            raise ValueError
            
    def get_teams_stats(self, team_id, year, fmt = 0):
        return self.data_scraper.get_teams_season_stats(self.get_team(team_id).abbr, year)
    
    def get_teams_season_stats(self, team_id, year):
        return self.data_scraper.get_teams_season_stats(self.get_team(team_id).abbr, year)
    
    def get_teams_stats_by_week(self, 
                                team_id, 
                                year, 
                                week = 0, 
                                all_weeks = False, 
                                sum_results = False,
                                only_data_columns = False,
                                average_results = False):
        
        if team_id in self.cache.keys():
            if year in self.cache[team_id].keys():
                if week in self.cache[team_id][year].keys():
                    df = self.cache[team_id][year][week]
                elif all_weeks and ('all' in self.cache[team_id][year].keys()):
                    df = self.cache[team_id][year]['all']
        else:
            start_metric('Get team stats from scraper')
            df = self.data_scraper.get_teams_season_stats_by_week(self.get_team(team_id).abbr, year, week)
            stop_metric()

            if not all_weeks:
                df.drop(df[df[('Meta','Week')].astype(int) > week].index, inplace = True)
            
            if not team_id in self.cache.keys():
                self.cache[team_id] = {}
            if not year in self.cache[team_id].keys():
                self.cache[team_id][year] = {}
            
            self.cache[team_id][year]['all' if all_weeks else week] = df.copy()
            
        # start_metric('Get team stats from scraper')
        # df = self.data_scraper.get_teams_season_stats_by_week(self.get_team(team_id).abbr, year, week)
        # stop_metric()

        if not all_weeks:
            df.drop(df[df[('Meta','Week')].astype(int) > week].index, inplace = True)
        
        
        if sum_results:
            df.loc['Total'] = pd.Series(df.sum())
        
        data_cols = [('Offense',   '1stD'),
                     ('Offense',  'TotYd'),
                     ('Offense',  'PassY'),
                     ('Offense',  'RushY'),
                     ('Offense',     'TO'),
                     ('Defense',   '1stD'),
                     ('Defense',  'TotYd'),
                     ('Defense',  'PassY'),
                     ('Defense',  'RushY'),
                     ('Defense',     'TO')]
        meta_cols = [('Meta','Home'),
                     ('Meta','Win'),
                     ('Meta','Loss'),
                     ('Meta','Tie')]
        if only_data_columns:
            return df[data_cols+meta_cols]
        
        if average_results:
            start_metric('Average results')
            data = df[data_cols]
            df = data.mean().T
            stop_metric()
        
        return df
    
    def load_all_teams_stats(self, year):
        pass
    