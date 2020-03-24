# -*- coding: utf-8 -*-
"""Worldometers Scrapping

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1h4ieSGCHonYbmReYxbV9AhjJz-SA1Fou
"""

import requests
import urllib.request
import time
from bs4 import BeautifulSoup
import json
import pandas as pd
import re
import pandas as pd


def world_data():

    LINK = "https://www.worldometers.info/world-population/population-by-country/"
	
    response = requests.get(LINK)
    soup = BeautifulSoup(response.text)
    table = soup.findAll("tbody")
    rows = [i for i in table[0].findAll("tr")]
    data = []
    for k in rows:
        elements = k.findAll("td")
        data.append({"Country" : elements[1].find("a").contents[0],
                     "Population": int(elements[2].contents[0].replace(",","")),
                     "Density" : elements[5].contents[0],
                     "Age" : elements[9].contents[0],
                     "Urban" : float(elements[11].contents[0][:-2])/100  })
    return pd.DataFrame(data)

def country_daily_data(country):
    link = "https://www.worldometers.info/coronavirus/" + country 
    response = requests.get(link)
    soup = BeautifulSoup(response.text)

    #We assume that the chart we want is the 11th script in the site !HIGH RISK TO BRAKE!
    js = soup.findAll("script", {"type" : "text/javascript"})[10].text.replace('\n', '').split(";")[1]

    #regular exp to extract the data and the values from Highcharts.chart
    values = re.findall('data: \[[0-9,]*\]', js)[0].split(": ")[1][1:-1].split(",")
    dates = re.findall('categories: \[[A-Za-z0-9," ]*\]', js)[0].split(": ")[1][1:-1].split(",")

    dates = [i.strip('"') for i in dates]
    values = [int(i) for i in values]

    return dict(zip(dates, values))

def main_page_scrape():

	LINK = "https://www.worldometers.info/coronavirus/"

    COL = ["Country","Total_Cases","New_Cases","Total_Deaths","New_Deaths","Total_Recovered","Active_Cases","Serious_Critical","Total_per_1M"]
    links = {}
    rows = []

    response = requests.get(LINK)
    soup = BeautifulSoup(response.text)
    table = soup.findAll("table", {"id" : "main_table_countries_today"})[0].findAll("tr")[1:]

    for i in table:
        row = i.findAll("td")
        link_details = row[0].find("a", {"class" : "mt_a"})
        if link_details is not None :
            con = link_details.contents[0]
            links = {**links, **{con : link_details['href']}}
        else:
            con = row[0].contents[0]
        dic ={COL[0] : con}
        for k,c in zip(row[1:], COL[1:]):
            try:
                dic = {**dic, **{c : k.contents[0]}}
            except:
                pass
        rows.append(dic)
    
    return links, pd.DataFrame(rows)