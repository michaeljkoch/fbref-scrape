#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on: 18 Aug 2023 16:03:50
By: Michael Koch
"""

from bs4 import BeautifulSoup
import requests
import time
import functools
import timeit
import pandas as pd


# <tbody> -> <tr data-row> -> <td data-stat="score"> -> <a href>

years = ['2016-2017']

# years = ['2022-2023', '2021-2022', '2020-2021', '2019-2020', '2018-2019']

URLS = [
    "https://fbref.com/en/comps/9/{}/schedule/{}-Premier-League-Scores-and-Fixtures".format(year, year) for year in years
]


def delay(func):
    """Sleep 3.5 seconds before calling function"""
    @functools.wraps(func)
    def wrapper_delay(*args, **kwargs):
        time.sleep(3.5)
        return func(*args, **kwargs)
    return wrapper_delay


@delay
def get_match_links(urls):
    """Gets links for each match during a season, specified by the URL

    @param urls: urls to the page with all matches for a season
    @return: a list containing the match urls
    """
    links = []

    for season in urls:
        page = requests.get(season)
        soup = BeautifulSoup(page.content, "html.parser")
        links.append(["https://fbref.com" + a['href'] for a in (td.a for td in soup.find_all('td', attrs={"data-stat": "score"})) if a])
        # print(links.append(["https://fbref.com" + a["href"] for a in (td.find('a') for td in soup.find_all('td', attrs={"data-stat": "score"})) if a]))

    return [match for year in links for match in year]

# match stats: tfoot -> td


@delay
def get_match_data(url):
    """
    
    @param url:
    @return:
    """
    print(url)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    scorebox = soup.find('div', class_='scorebox')
    facts = [(a.text, a["href"]) for a in (strong.find('a') for strong in scorebox.find_all('strong')) if a]
    match_data = [tfoot.find_all('td') for tfoot in soup.find_all('tfoot')]
    stats_dict = {
        'home_team': facts[0][0],
        'away_team': facts[1][0],
        'date': facts[2][1][-10:]
    }

    for stats in match_data[:6]:
        for stat in stats[5:]:
            stats_dict['home_' + stat['data-stat']] = stat.text

    for stats in match_data[6:]:
        for stat in stats[5:]:
            stats_dict['away_' + stat['data-stat']] = stat.text

    return stats_dict


match_links = get_match_links(URLS)

print(match_links)

# final_data = [get_match_data(match) for match in match_links]
# # print(final_data)
#
# match_df = pd.DataFrame(final_data)
# print(match_df)
#
# match_df.to_csv("epl_match_data_1617.csv", index=False)
