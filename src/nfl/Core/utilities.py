#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 14 16:12:56 2022

@author: willmaethner
"""

import os
import requests
import pickle

import pandas as pd

from pathlib import Path  
from time import perf_counter
from bs4 import BeautifulSoup as Soup

#############
# CONSTANTS #
#############

PFR_BASE_URL = "https://www.pro-football-reference.com"
CACHE_PATH = "../Data/Cache"



# HTTP Requests and Parsing
def parse_page(request_url):
    """
    Parameters
    ----------
    request_url : str
        Url of the web page to parse.

    Returns
    -------
    BeautifulSoup object
        Soup object after parsing the web page.

    """
    r = requests.get(request_url)
    return Soup(r.content, 'lxml')

def get_table_by_id(soup, table_id):
    return soup.select(f"table#{table_id}")[0]

def get_table_body_rows(soup, table_id):
    table = get_table_by_id(soup, table_id)
    body = table.find('tbody')
    return body.find_all('tr')
    
def parse_table(table):
    rows = table.find_all('tr')
    return [[str(x.string) for x in row.find_all('td')] for row in rows]





# Timer functions
def start_timer(label):
    data = {'label':label, 'start':perf_counter()}
    return data

def stop_timer(start_obj, print_results = False):
    start_obj['elapsed'] = perf_counter() - start_obj['start'] 
    if print_results:
        print(f'{start_obj["label"]}: {start_obj["elapsed"]}')
    return start_obj

# Serialization
def path_exists(path):
    """
    Parameters
    ----------
    path : str
        Path to check.

    Returns
    -------
    bool
        True if the path exists.

    """
    return os.path.exists(path)

def pickle_file_exists(filename, path = CACHE_PATH):
    return file_exists(f'{filename}.pkl')

def file_exists(filename, path = CACHE_PATH):
    filepath = Path(f'{path}/{filename}')  
    return filepath.exists()

def save_obj(filename, obj, path = CACHE_PATH):
    if not os.path.exists(path):
        os.makedirs(path)
    
    f = open(f'{path}/{filename}', 'wb')
    pickle.dump(obj, f)
    f.close()
    
def load_obj(filename, path = CACHE_PATH):
    with open(f'{path}/{filename}', 'rb') as p:
        return pickle.load(p)

def save_df(filename, df, path = CACHE_PATH):
    if not os.path.exists(path):
        os.makedirs(path)
        
    df.to_pickle(f'{path}/{filename}.pkl')

def load_df(filename, path = CACHE_PATH):
    return pd.read_pickle(f'{path}/{filename}.pkl')


# Display Helpers
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '???', printEnd = "\r"):
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