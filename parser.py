#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
"""Seekingalpha website StockTalks parser."""
from __future__ import print_function
import os
import csv
from datetime import datetime, timedelta

from selenium import webdriver
from bs4 import BeautifulSoup


def get_time(timestamp):
    """Converting website date reference to datetime object."""
    if timestamp.endswith('d'):
        delta = timestamp.split(' ')[0]
        return datetime.now() - timedelta(days=int(delta))
    else:
        return datetime.strptime(timestamp, '%m/%d/%Y')


def write_data(output, date, data):
    """Writing data to CSV file."""
    short_path = output + '/' + date
    path = short_path + '/comments.csv'
    if not os.path.exists(short_path):
        os.makedirs(short_path)
    if os.path.exists(path):
        with open(path, 'a') as csvfile:
            fieldnames = ['date', 'text', 'tickers']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow(data)
    else:
        with open(path, 'w') as csvfile:
            fieldnames = ['date', 'text', 'tickers']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(data)


def parse_data(time_window, output):
    """Parsing posts in user-defined time window."""
    time_delta = datetime.now() - timedelta(days=int(time_window))
    driver = webdriver.PhantomJS(executable_path="./phantomjs")
    driver.get("""https://seekingalpha.com/author/the-geoteam/"""
               """stocktalks#view=posts_activities""")
    feed = BeautifulSoup(driver.page_source,
                         'html.parser').findAll('div',
                                                {'class':
                                                 'card'})
    driver.quit()
    driver.close()
    for i in feed:
        if get_time(i.span.string) >= time_delta:
            data = {}
            data['date'] = get_time(i.span.string).strftime('%Y/%m/%d')
            data['text'] = i.find('div',
                                  {'class':
                                   'headline'}).text.encode('utf-8')
            tickers = i.find('div', {'class': 'title'}).findAll('a')
            if len(tickers) > 1:
                data['tickers'] = (', ').join([i.string
                                               for i in tickers][1:])
            else:
                data['tickers'] = ''
            write_data(output, data['date'], data)


if __name__ == '__main__':
    output = raw_input('Output folder: ')
    time_window = raw_input('Days timedelta: ')
    parse_data(time_window, output)
