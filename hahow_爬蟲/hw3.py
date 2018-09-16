#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 16 15:50:15 2018

@author: glenn
"""

#3-1: PTT 八卦版今天有多少不同的 5566 id 發文
import requests

import time

import json

from bs4 import BeautifulSoup

PTT_URL = 'https://www.ptt.cc'

def get_web_page(url):

    resp = requests.get(
        url=url,
        cookies={'over18': '1'}
    )
    if resp.status_code != 200:
        print('Invalid url:', resp.url)
        return None
    else:
        return resp.text

def get_articles(dom, date):
    soup = BeautifulSoup(dom, 'html5lib')
    # 取得上一頁的連結
    paging_div = soup.find('div', 'btn-group btn-group-paging')
    prev_url = paging_div.find_all('a')[1]['href']
    articles = []  # 儲存取得的文章資料
    divs = soup.find_all('div', 'r-ent')
    for d in divs:
        if d.find('div', 'date').text.strip() == date:  # 發文日期正確
            # 取得文章連結及標題
            if d.find('a'):  # 有超連結，表示文章存在，未被刪除
                href = d.find('a')['href']
                title = d.find('a').text
                author = d.find('div', 'author').text if d.find('div', 'author') else ''
                articles.append({
                    'title': title,
                    'href': href,
                    'author': author
                })
    return articles, prev_url
def get_author_ids(posts, pattern):
    ids = set()
    for post in posts:
        if post['author'].find(pattern) > 0:
            ids.add(post['author'])
    return ids

if __name__ == '__main__':
    current_page = get_web_page(PTT_URL + '/bbs/Gossiping/index.html')
    if current_page:
        articles = []  # 全部的今日文章
        today = time.strftime("%m/%d").lstrip('0')  # 今天日期, 去掉開頭的 '0' 以符合 PTT 網站格式
        current_articles, prev_url = get_articles(current_page, today)  # 目前頁面的今日文章
        while current_articles:  # 若目前頁面有今日文章則加入 articles，並回到上一頁繼續尋找是否有今日文章
            articles += current_articles
            current_page = get_web_page(PTT_URL + prev_url)
            current_articles, prev_url = get_articles(current_page, today)
        # 儲存或處理文章資訊
        print('今天有', len(articles), '篇文章')
        #印出所有不同的 5566 id有幾個
        print('今天有', len(get_author_ids(articles, '5566')), '個"5566"的id')   

#3-2: 取得每部電影的全文介紹
import requests

import re

import json

from bs4 import BeautifulSoup

Y_MOVIE_URL = 'https://tw.movies.yahoo.com/movie_thisweek.html'

# 以下網址後面加上 "/id=MOVIE_ID" 即為該影片各項資訊

Y_INTRO_URL = 'https://tw.movies.yahoo.com/movieinfo_main.html'  # 詳細資訊

Y_PHOTO_URL = 'https://tw.movies.yahoo.com/movieinfo_photos.html'  # 劇照

Y_TIME_URL = 'https://tw.movies.yahoo.com/movietime_result.html'  # 時刻表

def get_web_page(url):
    resp = requests.get(url)
    if resp.status_code != 200:
        print('Invalid url:', resp.url)
        return None
    else:
        return resp.text
def get_movies(dom):
    soup = BeautifulSoup(dom, 'html5lib')
    movies = []
    rows = soup.find_all('div', 'release_info_text')
    for row in rows:
        movie = dict()
        movie['expectation'] = row.find('div', 'leveltext').span.text.strip()
        movie['ch_name'] = row.find('div', 'release_movie_name').a.text.strip()
        movie['eng_name'] = row.find('div', 'release_movie_name').find('div', 'en').a.text.strip()
        movie['movie_id'] = get_movie_id(row.find('div', 'release_movie_name').a['href'])
        movie['poster_url'] = row.parent.find_previous_sibling('div', 'release_foto').a.img['src']
        movie['release_date'] = get_date(row.find('div', 'release_movie_time').text)
        #movie['intro'] = row.find('div', 'release_text').text.replace(u'詳全文', '').strip()
        trailer_a = row.find_next_sibling('div', 'release_btn color_btnbox').find_all('a')[1]
        movie['trailer_url'] = trailer_a['href'] if 'href' in trailer_a.attrs.keys() else ''
        movie['complete_info'] = "".join(get_complete_intro(get_movie_id(row.find('div', 'release_movie_name').a['href'])).replace(u'詳全文', '').strip().split())
        movies.append(movie)
    return movies

def get_date(date_str):
    # e.g. "上映日期：2017-03-23" -> match.group(0): "2017-03-23"
    pattern = '\d+-\d+-\d+'
    match = re.search(pattern, date_str)
    if match is None:
        return date_str
    else:
        return match.group(0)

def get_movie_id(url):
    # 20180515: URL 格式有變, e.g., 'https://movies.yahoo.com.tw/movieinfo_main/%E6%AD%BB%E4%BE%8D2-deadpool-2-7820.html

    # e.g., "https://tw.rd.yahoo.com/referurl/movie/thisweek/info/*https://tw.movies.yahoo.com/movieinfo_main.html/id=6707"

    #       -> match.group(0): "/id=6707"
    try:
        movie_id = url.split('.html')[0].split('-')[-1]
    except:
        movie_id = url
    return movie_id

def get_complete_intro(movie_id):
    page = get_web_page(Y_INTRO_URL + '/id=' + movie_id)
    if page:

        soup = BeautifulSoup(page, 'html5lib')
        infobox = soup.find('div', 'gray_infobox_inner')
        title_span = infobox.find('span', 'title2')
        if title_span:
            paragraph = title_span['title2']
        else:
            paragraph = infobox.text.strip()

    return paragraph

def main():
    page = get_web_page(Y_MOVIE_URL)
    if page:
        movies = get_movies(page)
        for movie in movies:
            print(movie)            

if __name__ == '__main__':

    main()

#第三章課後作業: Yahoo 奇摩字典
import requests

from bs4 import BeautifulSoup

import urllib.parse

Y_DICT_URL = 'https://tw.dictionary.search.yahoo.com/search?p='

def get_web_page(url, query):

    query = urllib.parse.quote_plus(query)

    resp = requests.get(url+query)

    if resp.status_code != 200:

        print('Invalid url:', resp.url)

        return None

    else:

        return resp.text

def get_dict_info(dom):
    try:
        soup = BeautifulSoup(dom, 'html5lib')

        for li in soup.find('div', 'p-rel').find_all('li'):

            print(li.text)
    except:
        print('查無此片語!')
#查詢片語，例如：out of order
if __name__ == '__main__':

    query = input('請輸入要查詢的字詞: ') 

    page = get_web_page(Y_DICT_URL, query)

    if page:

        get_dict_info(page)


