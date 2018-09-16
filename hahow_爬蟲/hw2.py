#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 16 15:45:36 2018

@author: glenn
"""

#找出範例網頁一 總共有幾篇 blog 貼文
import requests
from bs4 import BeautifulSoup

def main():
    resp = requests.get('http://blog.castman.net/web-crawler-tutorial/ch2/blog/blog.html')
    soup = BeautifulSoup(resp.text, 'html.parser')
    main_titles = soup.find_all('h4')

    print(len(main_titles))


if __name__ == '__main__':
         main()

#找出範例網頁一 總共有幾張圖片網址含有 'crawler' 字串
import requests
import re
from bs4 import BeautifulSoup

def main():
    resp = requests.get('http://blog.castman.net/web-crawler-tutorial/ch2/blog/blog.html')
    soup = BeautifulSoup(resp.text, 'html.parser')
    imgs = soup.find_all('img')
    sum = 0
    for img in imgs:
        if 'crawler' in img['src'] :
            sum = sum + 1
    print(sum)


if __name__ == '__main__':
         main()

#找出範例網頁二 總共有幾堂課程
import requests
import re
from bs4 import BeautifulSoup

resp = requests.get('http://blog.castman.net/web-crawler-tutorial/ch2/table/table.html')

soup = BeautifulSoup(resp.text, 'html.parser')

rows = soup.find('table', 'table').tbody.find_all('tr')

all_tds = []

for row in rows:
    tds = []
    tds = row.find_all('td')[0].text
    all_tds.append(tds)

print(len(all_tds))


#用 Chrome 開發者工具, 找出 Dcard 的今日熱門文章區塊, 然後取得前十篇熱門文章的標題 (提示: 每一篇熱門文章都是 class 為 PostEntry_container_ 開頭的 div, 可以用 find_all() 加上 regular expression 找出來; 標題文字被 <strong> 包圍)
import requests

import re

from bs4 import BeautifulSoup

def main():
    resp = requests.get('https://www.dcard.tw/f')
    soup = BeautifulSoup(resp.text, 'html.parser')
    dcard = soup.find_all('h3')[:10]
    n = 1
    for post in dcard:
        print('熱門話題Top'+str(n)+':'+post.text)
        n=n+1          

if __name__ == '__main__':
    main()