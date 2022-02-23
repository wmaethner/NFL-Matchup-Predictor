#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 31 19:43:08 2022

@author: willmaethner
"""

import pandas as pd

from nfl.Core.utilities import (PFR_BASE_URL, parse_page, get_table_by_id, 
                                parse_table,save_obj, load_obj, file_exists,
                                save_df, load_df)

base_url = "https://www.pro-football-reference.com"
teams = []
stats = {}


class Data_Scraper:  
    def __init__(self):
        self.stats = {}
        self.season_stats = load_df('season_stats') if file_exists('season_stats.pkl') else pd.DataFrame()
        self.season_stats_by_week = load_df('season_stats_by_week') if file_exists('season_stats_by_week.pkl') else pd.DataFrame()
        self.schedule = load_df('schedule') if file_exists('schedule.pkl') else pd.DataFrame()

    
    def data_columns(self):
        return ['Wins','Losses','Ties','PF','Yds','Ply','Y/P','TO','FL','1stD',
                'Cmp','Pass Att','Pass Yds','Pass TD','Int','NY/A','Pass 1stD',
                'Rush Att','Rush Yds','Rush Tds','Y/A','Rush 1stD','Pen','Pen Yds',
                '1stPy','#Dr','Sc%','TO%','Start','Time','Plays','Yds Per Drive','Pts']
    
    def load_stats(self, team_key, year):
        if file_exists(f'{team_key}.pkl'):
            self.stats[team_key] = load_obj(f'{team_key}.pkl')
            if year in self.stats[team_key].keys():
                return
        
        url = PFR_BASE_URL + f"/teams/{team_key}/{year}.htm"
        soup = parse_page(url)
        
        # Could get this info simpler from the main season page, but the parsing
        # takes forever so its quicker to just scrape through the team data
        meta_div = soup.find_all('div', {'data-template': 'Partials/Teams/Summary'})[0]
        record_p = meta_div.find_all('p')[0]
        end_tag = '</strong>'
        end_tag_index = str(record_p).find(end_tag)
        comma_index = str(record_p).find(',',end_tag_index)
        record = str(record_p)[end_tag_index+len(end_tag)+1:comma_index]
        record_parts = record.split('-')
        record_vals = [int(x) for x in record_parts]
        
        table = get_table_by_id(soup, 'team_stats')
        parsed_rows = parse_table(table)
        
        offense = [record_vals[0],record_vals[1],record_vals[2]]
        defense = [record_vals[0],record_vals[1],record_vals[2]]
        
        offense.extend(parsed_rows[2])
        defense.extend(parsed_rows[3])
        
        start_index = self.data_columns().index('Start')
        time_index = self.data_columns().index('Time')
        
        offense[start_index] = offense[start_index].split(' ')[1]
        defense[start_index] = defense[start_index].split(' ')[1]
        
        time = offense[time_index].split(':')
        offense[time_index]  = int(time[0]) + (int(time[1]) / 60)

        time = defense[time_index].split(':')
        defense[time_index]  = int(time[0]) + (int(time[1]) / 60)
        
        if not team_key in self.stats.keys():
            self.stats[team_key] = {}
            
        self.stats[team_key][year] = {}
        self.stats[team_key][year]['Offense'] = [float(x) for x in offense]
        self.stats[team_key][year]['Defense'] = [float(x) for x in defense]
        
        save_obj(f'{team_key}.pkl', self.stats[team_key])
    
    def get_teams_season_stats(self, team_key, year):       
        if team_key in self.season_stats.index.unique(0).array:
            if not year in self.season_stats.loc[team_key].index.unique(0).array:
                df_year = self.load_teams_season_stats(team_key, year)
                df_indexed = pd.concat({year: df_year})
                self.season_stats = pd.concat([self.season_stats, pd.concat({team_key: df_indexed})])
                save_df('season_stats', self.season_stats)
        else:
            df_year = self.load_teams_season_stats(team_key, year)
            df_indexed = pd.concat({year: df_year})
            self.season_stats = pd.concat([self.season_stats, pd.concat({team_key: df_indexed})])
            save_df('season_stats', self.season_stats)
        
        self.season_stats = self.season_stats.sort_index()
        return self.season_stats.loc[(team_key, year)]
    
    def get_teams_season_stats_by_week(self, team_key, year, week):
        if team_key in self.season_stats_by_week.index.unique(0).array:
            if not year in self.season_stats_by_week.loc[team_key].index.unique(0).array:
                df_year = self.get_teams_weekly_stats(team_key, year)
                df_indexed = pd.concat({year: df_year})
                self.season_stats_by_week = pd.concat([self.season_stats_by_week, pd.concat({team_key: df_indexed})])
                save_df('season_stats_by_week', self.season_stats_by_week)
        else:
            df_year = self.get_teams_weekly_stats(team_key, year)
            df_indexed = pd.concat({year: df_year})
            self.season_stats_by_week = pd.concat([self.season_stats_by_week, pd.concat({team_key: df_indexed})])
            save_df('season_stats_by_week', self.season_stats_by_week)
        
        self.season_stats_by_week = self.season_stats_by_week.sort_index()
        return self.season_stats_by_week.loc[(team_key, year)]  

    def get_teams_weekly_stats(self, team_key, year):
        url = PFR_BASE_URL + f"/teams/{team_key}/{year}.htm"
        soup = parse_page(url)
        table = get_table_by_id(soup, 'games')
        df = pd.read_html(str(table))[0]

        unnamed_vals = ['Time','Boxscore','Result','Home']        
        df.columns = pd.MultiIndex.from_tuples(
            [('Meta' if 'Unnamed' in x[0] else x[0],
              unnamed_vals.pop(0) if 'Unnamed' in x[1] else x[1]) 
             for x in df.columns])

        # Drop Expected points and box score columns
        df.drop(columns=('Expected Points'), level=0, inplace=True)
        df.drop(columns=('Meta','Boxscore'), inplace=True)
        
        # Drop bye week row
        df.drop(df[df[('Meta','Opp')] == 'Bye Week'].index, inplace = True)
        
        # Drop playoffs
        playoff_idx = min(df[df[('Meta','Date')] == 'Playoffs'].index.array)
        df.drop([x for x in df.index.array if x >= playoff_idx], inplace=True)
        
        # Set Home and Won columns
        df.loc[:, ('Meta','Home')] = df.apply(lambda row: 0 if row[('Meta','Home')] == '@' else 1, axis=1)
        df.loc[:, ('Meta', 'Win')] = df.apply(lambda row: 1 if row[('Meta','Result')] == 'W' else 0, axis=1)
        df.loc[:, ('Meta', 'Loss')] = df.apply(lambda row: 1 if row[('Meta','Result')] == 'L' else 0, axis=1)
        df.loc[:, ('Meta', 'Tie')] = df.apply(lambda row: 1 if row[('Meta','Result')] == 'T' else 0, axis=1)
    
        df.fillna(0, inplace=True)
        return df
        
        
        
    def get_schedule(self, year):
        if not year in self.schedule.index.unique(0).array:        
            url = PFR_BASE_URL + f"/years/{year}/games.htm"
            soup = parse_page(url)
            table = get_table_by_id(soup, 'games')
    
            df = pd.read_html(str(table))[0]
            df_filtered = df[df['Week'] != 'Week']
            df_filtered = df_filtered[df_filtered['Date'] != 'Playoffs']
    
            df_filtered.loc[:, 'Home'] = df_filtered.apply(lambda row: row['Loser/tie'] if row[5] == '@' else row['Winner/tie'], axis=1)
            df_filtered.loc[:, 'Away'] = df_filtered.apply(lambda row: row['Winner/tie'] if row[5] == '@' else row['Loser/tie']   , axis=1)
    
            df_filtered = df_filtered.drop(columns=[df_filtered.columns[5], df_filtered.columns[7]])
            self.schedule = pd.concat([self.schedule, pd.concat({year: df_filtered})]) 
            
            save_df('schedule', self.schedule)

        return self.schedule.loc[year]
    
    
    def load_teams_season_stats(self, team_key, year):
        url = PFR_BASE_URL + f"/teams/{team_key}/{year}.htm"
        soup = parse_page(url)
        
        # Could get this info simpler from the main season page, but the parsing
        # takes forever so its quicker to just scrape through the team data
        meta_div = soup.find_all('div', {'data-template': 'Partials/Teams/Summary'})[0]
        record_p = meta_div.find_all('p')[0]
        end_tag = '</strong>'
        end_tag_index = str(record_p).find(end_tag)
        comma_index = str(record_p).find(',',end_tag_index)
        record = str(record_p)[end_tag_index+len(end_tag)+1:comma_index]
        record_parts = record.split('-')
        record_vals = [int(x) for x in record_parts]
        
        table = get_table_by_id(soup, 'team_stats')
        parsed_rows = parse_table(table)
        
        offense = [record_vals[0],record_vals[1],record_vals[2]]
        defense = [record_vals[0],record_vals[1],record_vals[2]]
        
        offense.extend(parsed_rows[2])
        defense.extend(parsed_rows[3])
        
        start_index = self.data_columns().index('Start')
        time_index = self.data_columns().index('Time')
        
        offense[start_index] = offense[start_index].split(' ')[1]
        defense[start_index] = defense[start_index].split(' ')[1]
        
        time = offense[time_index].split(':')
        offense[time_index]  = int(time[0]) + (int(time[1]) / 60)

        time = defense[time_index].split(':')
        defense[time_index]  = int(time[0]) + (int(time[1]) / 60)
        
        df = pd.DataFrame({'Offense': [float(x) for x in offense], 
                           'Defense': [float(x) for x in defense]}).T
        df.columns = self.data_columns()
        return df
