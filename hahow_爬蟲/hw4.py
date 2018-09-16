#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 16 16:09:32 2018

@author: glenn
"""
#比較momo和pchome商品價格程式
import urllib.parse
import requests
import time
import json
import os
from bs4 import BeautifulSoup
import html
import time
from requests.adapters import HTTPAdapter
from matplotlib import pyplot as plt
#momo網路商城

def search_momo(query):
    query_enc = urllib.parse.quote(query)
    url = "http://m.momoshop.com.tw/mosearch/" + query_enc + ".html"
    headers = {'User-Agent': 'mozilla/5.0 (Linux; Android 6.0.1; '
                             'Nexus 5x build/mtc19t applewebkit/537.36 (KHTML, like Gecko) '
                             'Chrome/51.0.2702.81 Mobile Safari/537.36'}
    resp = requests.get(url, headers=headers)
    if not resp:
        return []
    resp.encoding = 'utf-8'
    soup = BeautifulSoup(resp.text, 'html.parser')
    items = []
    for elem in soup.find(id='itemizedStyle').ul.find_all('li'):
        item_name = elem.find('p', 'prdName').text
        item_price = elem.find("b", 'price').text.replace(',', '')
        if not item_price:
            continue
        item_price = int(item_price)
        item_url = 'http://m.momoshop.com.tw' + elem.find('a')['href']
        item_img_url = elem.a.img['src']

        item = {
            'name': item_name,
            'price': item_price,
            'url': item_url,
            'img_url': item_img_url,
        }
        items.append(item)
    return items


if __name__ == '__main__':
    query = 'iphone 7 128g plus'
    items = search_momo(query)
    today = time.strftime('%m-%d')
    print('%s 搜尋 %s 共 %d 筆資料' % (today, query, len(items)))
    for i in items:
        print(i)
    data = {
        'date': today,
        'store': 'momo',
        'items': items
    }
    with open(os.path.join('json', today + '-momo.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

#pchome網路商城

def get_resp(url, timeout=3, max_retries=3):
    # 3 秒未回應即為失敗, 最多失敗 3 次
    s = requests.Session()
    s.mount(url, HTTPAdapter(max_retries=max_retries))
    try:
        resp = s.get(url, timeout=timeout)
    except requests.exceptions.RequestException as e:
        print(e)
        return None
    return resp


def search_pchome(query):
    query = urllib.parse.quote(query)
    # &price=10000-40000: 鎖定價格帶 10000-40000
    query_url = "http://ecshweb.pchome.com.tw/search/v3.3/all/results?q=" + query + "&sort=rnk&price=10000-40000"
    resp = get_resp(query_url)
    if not resp:
        return []

    resp.encoding = 'utf-8'
    data = resp.json()  # 直接將 response 轉為 json
    if data['prods'] is None:
        return []

    total_page_count = int(data['totalPage'])
    if total_page_count == 1:
        return get_items(data)

    # 若不只一頁, 則取得各頁 url 再依序取得各頁的物件
    urls = []
    cur_page = 1
    while cur_page <= total_page_count:
        cur_page_url = query_url + '&page=' + str(cur_page)
        urls.append(cur_page_url)
        cur_page += 1
    items = []
    for url in urls:
        resp = get_resp(url)
        if resp:
            resp.encoding = 'utf-8'
            items += get_items(resp.json())
    return items


def get_items(json_dict):
    item_list = list()
    item_objects = json_dict['prods']
    for item_obj in item_objects:
        try:
            item = dict()
            item['name'] = html.unescape(item_obj['name'])
            item['price'] = int(item_obj['price'])
            item['describe'] = item_obj['describe']
            item['img_url'] = 'http://ec1img.pchome.com.tw/' + item_obj['picB']
            item['url'] = 'http://24h.pchome.com.tw/prod/' + item_obj['Id']
            item_list.append(item)
        except Exception:
            pass
    return item_list


if __name__ == '__main__':
    query = 'iphone 7 128g plus'
    items = search_pchome(query)
    today = time.strftime('%m-%d')
    print('%s 搜尋 %s 共 %d 筆資料' % (today, query, len(items)))
    for i in items:
        print(i)
    data = {
        'date': today,
        'store': 'pchome',
        'items': items
    }
    with open(os.path.join('json', today + '-pchome.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

#畫出兩個網站的比較圖
def get_avg_price(json_data):
    sum = 0
    for item in json_data:
        sum += int(item['price'])
    return sum/len(json_data)


if __name__ == '__main__':
    json_files = [f for f in os.listdir('json')
                  if os.path.isfile(os.path.join('json', f)) and f.endswith('.json')]
    avg_prices_momo = dict()
    avg_prices_pchome = dict()
    for json_file in json_files:
        with open(os.path.join('json', json_file), 'r', encoding='utf-8') as f:
            data = json.load(f)
            date = data['date']
            if data['store'] == 'momo':
                avg_prices_momo[date] = get_avg_price(data['items'])
            elif data['store'] == 'pchome':
                avg_prices_pchome[date] = get_avg_price(data['items'])

    # 排序日期
    keys = avg_prices_momo.keys()
    date = sorted(keys)
    print('momo')
    for d in date:
        print(d, int(avg_prices_momo[d]))
    print('pchome')
    for d in date:
        print(d, int(avg_prices_pchome[d]))

    # x-axis
    x = [int(i) for i in range(len(date))]
    plt.xticks(x, date)  # 將 x-axis 用字串標註
    price_momo = [avg_prices_momo[d] for d in date]  # y1-axis
    price_pchome = [avg_prices_pchome[d] for d in date]  # y2-axis
    plt.plot(x, price_momo, marker='o', linestyle='solid')
    plt.plot(x, price_pchome, marker='o', linestyle='solid')
    plt.legend(['momo', 'pchome'])
    # specify values on ys
    for a, b in zip(x, price_momo):
        plt.text(a, b, str(int(b)))
    for a, b in zip(x, price_pchome):
        plt.text(a, b, str(int(b)))
    plt.show()


