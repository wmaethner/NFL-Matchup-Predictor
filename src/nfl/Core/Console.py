#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 31 21:57:47 2022

@author: willmaethner
"""

import os
import typing
import pickle

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


from nfl.Data.DataScraper import Data_Scraper
from nfl.Data.TeamManager import Team_Manager

from nfl.Predicters.Predicters import (Offense_Correlation,
                                       Weekly_Correlation,
                                       TensorFlowBasic)
from nfl.Predicters.Analyzer import analyze_predicter


from nfl.Performance.Performance import (start_metric, stop_metric, display_metrics)

from utilities import (PFR_BASE_URL, start_timer, stop_timer, parse_page, 
                       get_table_by_id, parse_table, parse_page, printProgressBar)


def explore(obj):
    if type(obj) is dict:
        explore_dict(obj)
    elif type(obj) is list:
        for x in obj:
            print(x)
    else:
        print(obj)

def explore_dict(dictionary):
    mapped = {}
    
    selection = '.'
    
    while (selection != '') and (selection != 'q'):
        # print options
        for index, k in enumerate(dictionary.keys()):
            mapped[f'{index+1}'] = k
            print(f'[{index+1}] {k}')
            
        selection = input('Selection: ')
        if selection in mapped.keys():
            selection = explore(dictionary[mapped[selection]])
              
    return selection 
        

def make_prediction(year, home, away):
    off = Offense_Correlation(year)
    # stats = Team_Stats_Only_Correlation(year)
    # off_def = Offense_Minus_Defense_Correlation(year)
    print(f'Matchup: {home} - {away}')
    print(off.predict_winner(home, away))
    # print(stats.predict_winner(home, away))
    # print(off_def.predict_winner(home, away))

def save_stats_to_csvs(years):
    tm = Team_Manager()

    for year in years:   
        data = {}
        for index, t in enumerate(tm.teams):
            data[t.id_num] = tm.get_teams_stats(t.id_num, year, 1)
        
        offense = pd.concat({key: x.iloc[[0]] for key, x in data.items()}, axis=0).reset_index(level=1, drop=True)
        defense = pd.concat({key: x.iloc[[1]] for key, x in data.items()}, axis=0).reset_index(level=1, drop=True)
        
        offense.rename(index={team: tm.get_team(team).name for team in range(32)}, inplace=True)
        defense.rename(index={team: tm.get_team(team).name for team in range(32)}, inplace=True)
        
        offense.to_csv(f'CSVs/{year}_offense.csv')
        defense.to_csv(f'CSVs/{year}_defense.csv')  


def analyze_predicters(train_years, test_years):
    data = []
    
    s = start_timer('Build OffCorr')
    off = Offense_Correlation(train_years, False)
    data.append(stop_timer(s))
    
    s = start_timer('Build OffCorrDef')
    both = Offense_Correlation(train_years, True)
    data.append(stop_timer(s))
    
    s = start_timer('Build WeekCorr')
    week = Weekly_Correlation(train_years, True)
    data.append(stop_timer(s))
    
    s = start_timer('Build Tensor')
    tfb = TensorFlowBasic(train_years, False)
    data.append(stop_timer(s))
    
    s = start_timer('Build TensorDef')
    tfb_both = TensorFlowBasic(train_years, True)
    data.append(stop_timer(s))
    
    s = start_timer('Predict OffCorr')
    analyze_predicter(off, test_years)
    data.append(stop_timer(s))
    
    s = start_timer('Predict OffCorrDef')
    analyze_predicter(both, test_years)
    data.append(stop_timer(s))
    
    s = start_timer('Predict WeekCorr')
    analyze_predicter(week, test_years)
    data.append(stop_timer(s))
    
    s = start_timer('Predict Tensor')
    analyze_predicter(tfb, test_years)
    data.append(stop_timer(s))
    
    s = start_timer('Predict TensorDef')
    analyze_predicter(tfb_both, test_years)
    data.append(stop_timer(s))
    
    for x in data:
        print(f'{x["label"]}: {x["elapsed"]}')
      

def get_all_stats(year):
    tm = Team_Manager()
    data = {}
    # printProgressBar(0, len(tm.teams), prefix = 'Progress:', suffix = 'Complete', length = 50)
    # for index, t in enumerate(tm.teams):
    #     # printProgressBar(index + 1, len(tm.teams), prefix = 'Progress:', suffix = 'Complete', length = 50)
    #     data[t.id_num] = tm.get_teams_season_stats(t.id_num, year)
        
    data[0] = tm.get_teams_season_stats(0, year)
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


def main():
    # pd.set_option('display.max_columns', None)
    
    
    # ds = Data_Scraper()
    # tm = Team_Manager()
    
    
    # year_right = 0
    # schedule = ds.get_schedule(2021)
    
    # print(schedule)
    # print(len(schedule))
    
    
    # printProgressBar(0, len(schedule), prefix = 'Schedule Progress:', suffix = 'Complete', length = 50)
    # for index, row in schedule.iterrows():
    #     print(f'{schedule.loc[index,"Home"]} - {schedule.loc[index,"Away"]}')
        # printProgressBar(index+1, len(schedule), prefix = 'Schedule Progress:', suffix = 'Complete', length = 50)                    

    # for i in range(len(schedule)):
    #     row = schedule.iloc[i,:]
    #     print(f'{row["Home"]} - {row["Away"]}')
        # print(f'{schedule.iloc[i,"Home"]} - {schedule.iloc[i,"Away"]}')

   
    # print(tm.get_teams_stats_by_week(0, 2021, 2, only_data_columns=True))
    
    # data = tm.get_teams_stats_by_week(0, 2021, 2, average_results=True)
    # print(data)
    # print(data[('Offense','1stD')])
    
    # years = [2020,2021]
    # week = Weekly_Correlation(years, True)
    # # off = Offense_Correlation(years, True)
    # # prediction = off.predict_winner(0, 1, 2021)
    # # print(prediction)
    # prediction = week.predict_winner(0, 1, 2021, '2')
    # print(prediction)

    # return
    
    # stats = []
    # for year in years:
    #     stats.append(get_all_stats(year))
    # # print(len(stats))
    # all_stats = concat_year_stats(stats, 'Offense')
    # row_index = all_stats.groupby(all_stats.index)
    # print(row_index.mean())
    
    
    # data = tm.get_teams_season_stats(0, 2021)
    # data = tm.get_teams_stats_by_week(0, 2021, all_weeks=True, sum_results=False, only_data_columns=True)
    # stats_normal = (data-data.min())/(data.max()-data.min())
    # stats_normal.fillna(0, inplace=True)
    # corr = stats_normal.corr() 
    # print(stats_normal)
    # print(corr)
    # print(corr[('Meta','Win')])
    
    # data = tm.get_teams_stats_by_week(0, 2021, 15, all_weeks=True, sum_results=True)
    # print(data)
    # print(ds.season_stats_by_week)
    # data = ds.get_teams_weekly_stats('crd', 2021)
    # print(data)
    # print(data)
    # print(data.columns)
    # idx = data.columns
    
    # # print(idx)
    # idx = pd.MultiIndex.from_tuples([('Meta' if 'Unnamed' in x[0] else x[0],x[1]) for x in idx])
    # # print(idx)
    # data.columns = idx
    # print(data)
    # data.columns.set_levels(['b1','c1','f1'],level=1,inplace=True)
    # print(data)
    
    # print(ds.season_stats)
    # data = ds.get_teams_stats('crd', 2021)
    # print(data)
    # print(data.loc[['Offense']])
    # return
    # print(ds.stats)
    # data = ds.get_teams_season_stats('crd', 2021)
    # print(data)
   
    # data = ds.get_teams_stats_1('crd', 2018)
    # print(data)
    
    # data = ds.load_teams_season_stats('crd', 2021)
    # print(data)
    
    
    # df1 = pd.DataFrame(np.arange(40).reshape(10, 4),
    #               columns=[[1,1,2,2],['A', 'B', 'C', 'D']])
    
    # print(df1)
    
    # df1.columns = df1.columns.set_levels([[1,2],[1,2,3,4]])
    # print(df1)
    
    
    # idx = df1.index.array
    # to_remove = [x for x in idx if x > 5]
    # df1.drop(to_remove, inplace=True)
    
    # print(df1)
    
    # df2 = pd.DataFrame(np.arange(12).reshape(3, 4),
    #               columns=['A', 'B', 'C', 'D'])
    # df2.iloc[1] = df2.iloc[1].apply(lambda x: x + 1)
    
    # df_first = pd.concat({'Foo': df1, 'Bar': df2})

    # df3 = pd.DataFrame(np.arange(12).reshape(3, 4),
    #               columns=['A', 'B', 'C', 'D'])
    # df4 = pd.DataFrame(np.arange(12).reshape(3, 4),
    #               columns=['A', 'B', 'C', 'D'])
    # df4.iloc[1] = df2.iloc[1].apply(lambda x: x + 5)
    
    # df_second = pd.concat({'Foo': df3, 'Bar': df4})
    
    # df_all = pd.concat({'first': df_first, 'second': df_second})
    # # print(df_first)
    # # print(df_second)
    # print(df_all)
    # print(df_all.loc[('second', 'Bar')])
    
  
    
    # test = {'A': np.arange(100).reshape(10,10),
    #         'B': np.arange(100).reshape(10,10),
    #         'C': np.arange(100).reshape(10,10),
    #         'D': np.arange(100).reshape(10,10) }
    
    # s = start_timer('save dict')
    # f = open(f'testdict.pkl', 'wb')
    # pickle.dump(test, f)
    # f.close()
    # stop_timer(s, True)
    

    # test_df = pd.DataFrame(test, columns=list(range(10)))

   
    # ds.get_teams_weekly_stats('crd', 2021)
    
    # data = []
    train_years = [2017,2018,2019,2020]
    test_years = [2021]
    # analyze_predicters(train_years, test_years)
    
    start_metric('Analyze Weekly Correlation')
    # pred = Offense_Correlation(train_years, False)
    pred = Weekly_Correlation(train_years, False)
    data = analyze_predicter(pred, test_years, True)
    stop_metric()
    # # print(data)
    # week_df = pd.DataFrame(data['by_year_and_week'][test_years[0]]).T
    # week_df.loc[:, 'percent'] = week_df.apply(lambda row: 100*(row['right']/row['total']), axis=1)
    # # print(week_df.iloc[:18])
    # week_df.iloc[:18].loc[:,'percent'].plot()
    
    # xpoints = [x for x in data['by_year_and_week'][2021].keys()]
    # print(xpoints)
    
    
    # s = start_timer('Build Tensor')
    # tfb = TensorFlowBasic(train_years, False)
    # stop_timer(s)
    
    # s = start_timer('Build TensorDef')
    # tfb_both = TensorFlowBasic(train_years, True)
    # data.append(stop_timer(s))
    
    display_metrics()
    return
   
    
   
    



if __name__ == "__main__":
    main()