#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 31 19:43:08 2022

@author: willmaethner
"""

import pandas as pd

import requests

from pathlib import Path  
from pandas import DataFrame
from bs4 import BeautifulSoup as Soup

base_url = "https://www.pro-football-reference.com"
teams = []
stats = {}

class team:
    def __init__(self, team_tag):
        self.id_num = 1
        self.name = team_tag.a.get_text()
        self.abbr = team_tag.a.get('href').split('/')[-2]
        self.aliases = []
        
    def __str__(self):
        return f"{self.name} - {self.abbr}"
    
    def set_id(self, id_num):
        self.id_num = id_num
        
    def add_alias(self, alias):
        self.aliases.append(alias)


def get_teams() -> list:
    if teams:
        return teams
    
    r = requests.get(base_url + "/teams/")
    soup = Soup(r.content, 'html.parser')
    table = soup.select('table#teams_active')[0]
    body = table.find('tbody')
    rows = body.find_all('tr')
    
    current = team(rows[0].find('th'))
    for x in rows[1:]:
        th_tag = x.find('th')
        classes = x.attrs.get('class')
        if (not classes is None) and ('partial_table' in classes):
            current.add_alias(th_tag.get_text())
        else:
            teams.append(current)
            current = team(th_tag)
    teams.append(current)    

    for index, t in enumerate(teams):
        t.set_id(index)

    return teams

def get_team_id(name_or_alias):
    for t in teams:
        options = [x for x in t.aliases]
        options.append(t.name)
        if name_or_alias in options:
            return t.id_num

def get_schedule(year):
    url = base_url + f'/years/{year}/games.htm'
    r = requests.get(url)
    soup = Soup(r.content, 'html.parser')
    table = soup.select('table#games')[0]
    df = pd.read_html(str(table))[0]
    df_filtered = df[df['Week'] != 'Week']
    df_filtered = df_filtered[df_filtered['Date'] != 'Playoffs']

    df_filtered.loc[:, 'Home'] = df_filtered.apply(lambda row: get_home_team(row), axis=1)
    df_filtered.loc[:, 'Away'] = df_filtered.apply(lambda row: get_away_team(row), axis=1)
    df_filtered = df_filtered.drop(columns=[df_filtered.columns[5], df_filtered.columns[7]])

    return df_filtered

def get_home_team(row):
    return row['Loser/tie'] if row[5] == '@' else row['Winner/tie']
def get_away_team(row):
    return row['Winner/tie'] if row[5] == '@' else row['Loser/tie']    

def get_all_teams_stats(year, reload = False):
    if year in stats.keys():
        return stats
    
    data = {}
    year_data = {}
    teams = get_teams()
    
    printProgressBar(0, len(teams), prefix = 'Progress:', suffix = 'Complete', length = 50)
    for index, team in enumerate(teams):
        printProgressBar(index + 1, len(teams), prefix = 'Progress:', suffix = 'Complete', length = 50)
        year_data[team.name] = get_teams_stats(team.abbr, year, reload)
        
    data[year] = year_data
    stats[year] = year_data
    return data

def get_teams_stats(team_abbr: str, year: str, reload = False):
    df = get_stats_from_csv(f'{team_abbr}_{year}')
    
    if (df is None) or reload:    
        column_names = []
    
        url = base_url + f"/teams/{team_abbr}/{year}.htm"
        r = requests.get(url)
        # TODO: This is the slow up, look for more efficient parsing methods.
        #       The html returned is huge especially given we only need the first
        #       table, can we be more specific?
        soup = Soup(r.content, 'lxml')
     
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
        
        # table = soup.find('table')
        table = soup.select("table#team_stats")[0]
        # head = table.find('thead')
        rows = table.find_all('tr')
        
        # second_header = head.find_all('tr')[1]
        # parsed_header = parse_header(second_header)
        # column_names = parsed_header[1:]
        
        # Hard coded the columns because the column headers repeat causing data to 
        # to be lost. For example there are 'Yds' columns for Total, Passing, Rushing,
        # Penalties, and Average Drive which overwrite eachother.
        column_names = ['PF','Yds','Ply','Y/P','TO','FL','1stD','Cmp','Pass Att',
                        'Pass Yds','Pass TD','Int','NY/A','Pass 1stD','Rush Att',
                        'Rush Yds','Rush Tds','Y/A','Rush 1stD','Pen','Pen Yds',
                        '1stPy','#Dr','Sc%','TO%','Start','Time','Plays',
                        'Yds Per Drive','Pts']
    
        list_of_parsed_rows = [parse_row(row) for row in rows]
        data = {'Wins':[record_vals[0],record_vals[0]],
                'Losses':[record_vals[1],record_vals[1]],
                'Ties':[record_vals[2],record_vals[2]]}
        
        data.update({x:[list_of_parsed_rows[2][index], list_of_parsed_rows[3][index]] for index, x in enumerate(column_names)})
        df = pd.DataFrame(data, index=['Offense', 'Defense'])
        for index in df.index:
            df.loc[index, 'Start'] = df.loc[index, 'Start'].split(' ')[1]
            time = df.loc[index, 'Time'].split(':')
            df.loc[index, 'Time'] = int(time[0]) + (int(time[1]) / 60)
    
        df = df.apply(pd.to_numeric)
        save_stats_to_csv(df, f'{team_abbr}_{year}')
    
    return df

def parse_header(header):
    return [str(x.string) for x in header.find_all('th')]
    
def parse_row(row):
    """
    Take in a tr tag and get the data out of it in the form of a list of
    strings.
    """
    return [str(x.string) for x in row.find_all('td')]

def save_stats_to_csv(df, filename):
    filepath = Path(f'Data/Stats/{filename}.csv')  
    filepath.parent.mkdir(parents=True, exist_ok=True)  
    df.to_csv(filepath)

def get_stats_from_csv(filename):
    filepath = Path(f'Data/Stats/{filename}.csv')  
    if filepath.exists():
        return pd.read_csv(filepath, index_col=[0])
    return None

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()
