#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 14 15:52:01 2022

@author: willmaethner
"""

from nfl.Core.utilities import (PFR_BASE_URL, parse_page, get_table_by_id, get_table_body_rows,
                                             save_obj, load_obj, file_exists, start_timer, stop_timer)
from nfl.Data.DataScraper import Data_Scraper

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

        
    def load_teams(self):
        if file_exists('teams.pkl'):
            self.teams = load_obj('teams.pkl')
            return
        
        soup = parse_page(PFR_BASE_URL + '/teams/')
        rows = get_table_body_rows(soup, 'teams_active')
        # table = get_table_by_id(soup, 'teams_active')
        
        # body = table.find('tbody')
        # rows = body.find_all('tr')
        
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
        return self.data_scraper.get_teams_stats(self.get_team(team_id).abbr, year, fmt)
    