# -*- coding: utf-8 -*-
import requests.exceptions
import urllib3, sys, os
from bs4 import BeautifulSoup
import re
import pandas as pd
from collections import defaultdict
from itertools import repeat

output_path = os.path.dirname(os.path.realpath(__file__)).replace('module', 'msrp')

def getBeautifulSoup(page):
    url = page
    agent = {"User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
    http = urllib3.PoolManager()
    page = http.request('GET', url, headers=agent)
    return BeautifulSoup(page.data, features='lxml')

def getModelYear(page):
    secondPage = []
    soup = getBeautifulSoup(page)
    for year in soup.find_all('div', attrs={'class':'year-selector-container year-less'}):
        for model_year in year.find_all('a'):
            try:
                url = 'https://www.thecarconnection.com' + model_year.get('href')
                secondPage.append(url)
            except TypeError:
                pass
    return secondPage

def getAllLinks(brand):
    mainPage = []
    soup = getBeautifulSoup('https://www.thecarconnection.com/make/used,{}'.format(brand.lower().replace(' ', '-')))
    for model in soup.find_all('div', attrs={'id':'year-models'}):
        for link in model.find_all('div', attrs={'class': 'info'}):
            url = 'https://www.thecarconnection.com' + link.find_all('a')[0].get('href')
            mainPage.append(url)
    df = pd.DataFrame(mainPage, columns= ['Primary'])
    df['Secondary'] = df['Primary'].apply(getModelYear)
    df = df['Secondary'].apply(pd.Series)
    df = pd.DataFrame(df.stack(), columns=['Link'])
    return df

def getMSRP(page):
    page = page.replace('overview', 'specifications')
    soup = getBeautifulSoup(page)
    brand = []
    model = []
    trims = []
    trim_val = []
    msrp_val = []
    mpg_val = []
    engine_val = []
    horsepower_val = []
    drivetrain_val = []
    capacity_val = []
    transmission_val = []
    list_key = []

    for container in soup.find_all('div', attrs={'class':'features-specs-container'}):
        for trim in container.find_all('div', attrs={'class':re.compile(r'^selected-trim')}):
            trim_val.append(trim.text.strip())
        for msrp in container.find_all('div', attrs={'class':re.compile(r'^features-specs-value msrp')}):
            msrp_val.append(msrp.text.strip())
        for mpg in container.find_all('div', attrs={'class':re.compile(r'^features-specs-value mpg')}):
            mpg_val.append(mpg.text.strip())
        for engine in container.find_all('div', attrs={'class':re.compile(r'^features-specs-value engine')}):
            engine_val.append(engine.text.strip())
        for horsepower in container.find_all('div', attrs={'class':re.compile(r'^features-specs-value horsepower')}):
            horsepower_val.append(horsepower.text.strip())
        for drivetrain in container.find_all('div', attrs={'class':re.compile(r'^features-specs-value drivetrain')}):
            drivetrain_val.append(drivetrain.text.strip())
        for capacity in container.find_all('div', attrs={'class':re.compile(r'^features-specs-value capacity')}):
            capacity_val.append(capacity.text.strip())
        for transmission in container.find_all('div', attrs={'class':re.compile(r'^features-specs-value transmission')}):
            transmission_val.append(transmission.text.strip())

    for container in soup.find_all('div', attrs={'class': 'features-specs-container'}):
        for label in container.find_all('div', attrs={'class': re.compile(r'^features-specs-lable')}):
            list_key.append(label.text.strip())

    for title in soup.find_all('h1'):
        model.extend(repeat(title.text.replace('Specifications', '').strip(), len(msrp_val)))
        brand.extend(repeat('Year and Model', len(msrp_val)))
        trims.extend(repeat('Trim', len(msrp_val)))

    list_value = model + trim_val + msrp_val + mpg_val + engine_val + horsepower_val + drivetrain_val + capacity_val + transmission_val
    list_key = brand + trims + list_key
    dict = defaultdict(list)
    for key, value in zip(list_key, list_value):
        dict[key].append(value)

    df = pd.DataFrame.from_dict(dict)
    df['URL'] = page
    try:
        df.to_csv(output_path + '/' + model[0] + '.csv', index=False)
    except IndexError:
        pass





