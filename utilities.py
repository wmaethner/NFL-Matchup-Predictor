#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 14 16:12:56 2022

@author: willmaethner
"""

import os
import requests
import pickle

from pathlib import Path  
from time import perf_counter
from bs4 import BeautifulSoup as Soup

#############
# CONSTANTS #
#############

PFR_BASE_URL = "https://www.pro-football-reference.com"



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
def start_timer():
    return perf_counter()

def stop_timer(start):
    return perf_counter()-start

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

def file_exists(path, filename):
    filepath = Path(f'{path}/{filename}')  
    return filepath.exists()

def save_obj(path, filename, obj):
    if not os.path.exists(path):
        os.makedirs(path)
    
    f = open(f'{path}/{filename}', 'wb')
    pickle.dump(obj, f)
    f.close()
    
def load_obj(path, filename):
    with open(f'{path}/{filename}', 'rb') as p:
        return pickle.load(p)

