# -*- coding: utf-8 -*-
"""
Simple Web Scrape of Vassar Athletics And Other Libery Athletic Teams 

"""


import pandas as pd 
import numpy as np 
from datetime import datetime

from bs4 import BeautifulSoup
import urllib
from timeit import default_timer as timer

headers = { 'User-Agent' : 'Mozilla/5.0' }

def scores(base_url):
    req = urllib.request.Request(base_url, None, headers)
    r = urllib.request.urlopen(req).read()
    
    soup = BeautifulSoup(r)
    
    test = soup.find("main",{'id':'ctl00_contentDiv_container'})
    first_half = test.find_all( "div", {"class":"schedule_game_results"})
    #home_away = test.find_all( "div", {"style": "margin:2px;"})

    return (first_half)

def array(base_url):
    
    df = scores(base_url)
    
    result_array = []
    score_array = []
    
    for i in df: 
        z = str(i)
        j = [n for n, x in enumerate(z) if x in ["W", "L", "T"]][0]
        result_array.append(z[j])
        score_array.append(z[j+2:j+5])
    
    final_frame = pd.DataFrame(data = [result_array, score_array]).T
    final_frame.columns = ['Result', 'Score']
    
    GF  = []
    GA = []
    for i in final_frame['Score']:
        GF.append(str(i)[0])
        GA.append(str(i)[2])
    final_frame['GF'] = GF
    final_frame['GA'] = GA
    
    
    return(final_frame)

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def home_away(base_url):
    
    req = urllib.request.Request(base_url, None, headers)
    r = urllib.request.urlopen(req).read()
    
    soup = BeautifulSoup(r) 
    
    test = soup.find("main",{'id':'ctl00_contentDiv_container'})
    
    title = soup.find_all( "div", {"class": "sport_title"})
    try: 
        if str(title).find("Men's Soccer") >= 0: 
            test = test.find_all( "div", {"style": "margin:2px;"})
            home_away_array = []
            for i in test:
                if str(i).find("schedule_game schedule_game_home") != -1:
                    home_away_array.append("Home")
                else: home_away_array.append("Away")
                
            date = [] 
            for i in test:
                date.append(find_between(str(i), '\t\t\t\t', '\t\t\t\t'))
             
            home_away_df = pd.DataFrame([home_away_array, date]).T
            home_away_df.columns = ['Location', 'Date']
            return(home_away_df)
    except: 
        pass
   

def combine_frames(base_url, LL_Team):
    HOME = home_away(base_url)
    try: 
        scores = array(base_url).iloc[range(len(HOME))]
        
        final_df = (pd.concat([HOME, scores], axis = 1))
        final_df['LL Team'] = np.repeat(LL_Team, len(final_df))
        return(final_df)
    except: 
        pass
### What if we looped through these numbers for 200 numbers #### 


def get_all_results(base_url, LL_Team):
    
    final_df = combine_frames(base_url, LL_Team)
    final_df['source'] = base_url
    for i in reversed(range(25,400)): 
        try: 
            next_url = (base_url[0:base_url.find('?')+1] + str('schedule=') + str(i) + 
                                 str('&path=') + str(base_url)[(str(base_url).find('path='))+5::])

            historical_df = combine_frames(str(next_url), LL_Team)
            try:
                historical_df['source'] = str((base_url[0:base_url.find('?')+1] + str('schedule=') + str(i) + 
                                 str('&path=') + str(base_url)[(str(base_url).find('path='))+5::]))
                
                final_df = pd.concat([final_df, historical_df], axis = 0)
            except: 
                pass
            
        except IndexError: 
            pass 
    return(final_df)
    
Vassar = get_all_results('http://www.vassarathletics.com/schedule.aspx?path=msoc', 'Vassar')
Union = get_all_results('http://www.unionathletics.com/schedule.aspx?path=msoccer', 'Union')

RIT = get_all_results('http://www.ritathletics.com/schedule.aspx?path=msoc', 'RIT')
RPI = get_all_results('https://www.rpiathletics.com/schedule.aspx?path=msoc', 'RPI')
Skidmore = get_all_results('https://www.skidmoreathletics.com/schedule.aspx?path=msoc', 'Skidmore')
Bard = get_all_results('http://www.bardathletics.com/schedule.aspx?path=msoc', 'Bard')

LL_Teams = pd.concat([Vassar, Union, RIT, RPI, Skidmore, Bard], axis = 0)

#SLU = get_all_results('http://saintsathletics.com/schedule.aspx?path=msoc', 'SLU')
#Hobart = get_all_results('http://www.hwsathletics.com/schedule.aspx?path=msoc', 'Hobart')
#
#
#final_df = pd.concat([combine_frames('http://www.vassarathletics.com/schedule.aspx?path=msoc', 'Vassar'),
#        combine_frames('http://www.vassarathletics.com/schedule.aspx?schedule=369&path=msoc', "Vassar"), 
#        combine_frames('http://www.vassarathletics.com/schedule.aspx?schedule=323&path=msoc', 'Vassar'), 
#        combine_frames('http://www.vassarathletics.com/schedule.aspx?schedule=294&path=msoc', 'Vassar'), 
#        combine_frames('http://www.vassarathletics.com/schedule.aspx?schedule=265&path=msoc', 'Vassar'), 
#        combine_frames('http://www.vassarathletics.com/schedule.aspx?schedule=229&path=msoc', 'Vassar')], axis = 0)

