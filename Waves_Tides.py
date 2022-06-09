# -*- coding: utf-8 -*-
"""
Created on Wed Jun  1 20:44:34 2022
Print current tide and bouy data from NOAA stations
@author: daniel anzelon
"""
import requests
import json
from datetime import datetime
import urllib.request
from urllib.request import urlopen
from bs4 import BeautifulSoup

def todays_tides(station_num):
    api_url = 'https://api.tidesandcurrents.noaa.gov/api/prod/datagetter'
    #api documentation: https://api.tidesandcurrents.noaa.gov/api/prod/
    #parameters for tide predictions
    params1 = {'date':'today','station':station_num, 
              'format':'json','product':'predictions',
              'units':'english','time_zone':'lst_ldt',
               'datum':'MLLW','interval':'hilo' }
    #parameters to extract station data. Tide prediction results don't include station metadata
    params2 = {'date':'today','station':station_num, 
              'format':'json','product':'water_level',
              'units':'english','time_zone':'lst_ldt',
              'datum':'MLLW','interval':'hilo' }
    
    #api request and convert to json
    req1 = requests.get(api_url, params1).json()
    req2 = requests.get(api_url, params2).json()

    #print out station information
    station_info = req2['metadata']
    station_id, station_name = (station_info['id'], station_info['name'])
    print(f'-Tide data for: {station_name}, Station No: {station_id}')
    
    #extract and print out tide data
    tide_predictions = req1['predictions']
    for dicts in tide_predictions:
        if dicts['type'] == 'L':
            dicts['type'] = 'Low'
        else:
            dicts['type'] = 'High'

        dicts['t'] = datetime.strptime(dicts['t'], "%Y-%m-%d %H:%M")
        dicts['t'] = dicts['t'].strftime("%I:%M %p")
    #create a list of tuples for each tide
    tides = [(d['t'], round(float(d['v']),1), d['type']) for d in tide_predictions]
    for tups in tides:
        print(f'{tups[0]} | {tups[2]} tide: {tups[1]}ft')

#example station data        
La_Jolla = '9410230'
Portland_ME = '8418150'      
todays_tides(La_Jolla)

print()

def current_bouy_data(station_num):
    #using BeautifulSoup to scrape table data from NOAA bouy page
    url = 'https://www.ndbc.noaa.gov/station_page.php?station='+str(station_num)

    html = urlopen(url).read()
    bs = BeautifulSoup(html,features="lxml")

    station_name = bs.find('h1', {'style':"text-align:center; margin:3px;" }).getText()
    
    table1 = bs.find('table', { 'bgcolor' : '#f0f8fe' })
    try:
        wavedata = table1.find_all('td')[1:]
        wavedata_list = [items.getText('',strip = True) for items in wavedata]
        #remove empty strings in list
        #test_list = list(filter(None, test_list))
        wavedata_list = [i for i in wavedata_list if i]     
        #create a list of tuples with matching elements
        L = list(zip(wavedata_list[::2], wavedata_list[1::2]))
        #print header
        print(f'-Current Conditions at: {station_name}')
        #print out tuple
        for l in L:
            print(l[0], l[1])
    except:
        print(f'***NO DATA FOUND FOR STATION: {station_num}***')

#stationlist - https://www.ndbc.noaa.gov/to_station.shtml
#not all stations produce data
Oceanside = '46224'
DelMar = '46266'

current_bouy_data(DelMar)