#!/usr/bin/env python3
#time: 2017/07/29 21:50
#version: 1.0
#_author_:Benty_Yu

import urllib
import urllib.request
from bs4 import BeautifulSoup
import inspect
from multiprocessing.dummy import Pool as ThreadPool
import math
import datetime
from time import sleep
from cons import headers
import gzip
import pandas as pd

city = input("请输入城市简写")
page = input("请在此输入网页数：")
first_urlset = []
for i in range(1, int(page)+1):
    url = "http://esf."+str(city)+".fang.com/housing/__1_0_0_0_"+str(i)+"_0_0_0/"
    first_urlset.append(url)
	
print(url)

def read_url(url, encoding="gb18030"):
    try:
        req = urllib.request.Request(url)
        req.add_header('user-agent',headers())
        content = urllib.request.urlopen(req,timeout = 5).read()
        content = gzip.decompress(content).decode(encoding)
    except Exception as e:
        print(e)
        print(inspect.stack()[1][3] + ' occused error')
        sleep(5)
        req = urllib.request.Request(url)
        req.add_header('user-agent', headers())
        content = urllib.request.urlopen(req).read()
        content = gzip.decompress(content).decode("gb18030")  # 网页gb2312的编码要用这个
    soup = BeautifulSoup(content,"lxml")
    return soup


urls = []
sales = []
rents = []
sector = []
sitte = []
name = []
time = []
price = []


def get_urls(url):
	soup = read_url(url)
	table = soup.find('div',class_="houseList").find_all('div',class_="list rel")
	for item in table:
		urls.append(item.find('dl',class_="plotListwrap clearfix").find('a').get('href'))
	return urls
    	

def get_sales(url):
	soup = read_url(url)
	table = soup.find('div',class_="houseList").find_all('div',class_="list rel")
	for item in table:
		sales.append(item.find('ul', class_="sellOrRenthy clearfix").find_all('a')[0].get_text())
	return sales
	    	
def get_rents(url):
	soup = read_url(url)
	table = soup.find('div',class_="houseList").find_all('div',class_="list rel")
	for item in table:
		rents.append(item.find('ul', class_="sellOrRenthy clearfix").find_all('a')[1].get_text())
	return rents


def get_time(url):
    soup = read_url(url)
    table = soup.find('div',class_="houseList").find_all('div',class_="list rel")
    for item in table:
        time.append(item.find('ul', class_="sellOrRenthy clearfix").find_all('li')[2].get_text())
    return time

def get_sector(url):
    soup = read_url(url)
    table = soup.find('div',class_="houseList").find_all('div',class_="list rel")
    for item in table:
        sector.append(item.find_all('a')[2].get_text())
    return sector

def get_sitte(url):
    soup = read_url(url)
    table = soup.find('div',class_="houseList").find_all('div',class_="list rel")
    for item in table:
        sitte.append(item.find_all('a')[3].get_text())
    return sitte

def get_name(url):
    soup = read_url(url)
    table = soup.find('div',class_="houseList").find_all('div',class_="list rel")
    for item in table:
        name.append(item.find('a', class_="plotTit").get_text())
    return name

def get_price(url):
    soup = read_url(url)
    table = soup.find('div',class_="houseList").find_all('div',class_="listRiconwrap")
    for item in table:
        price.append(item.find('p', class_="priceAverage").find_all('span')[0].get_text())
    return price






def main(url):
    get_urls(url)
    get_sales(url)
    get_rents(url)
    get_sitte(url)
    get_sector(url)
    get_name(url)
    get_time(url)
    get_price(url)


df_dic={'urls':urls,'price':price,'sales':sales,'rents':rents,'sector':sector,'sitte':sitte,'time':time,'name':name}


	
pool = ThreadPool(4)
pool.map(main, first_urlset)
pool.close()
pool.join()


today = datetime.date.today().strftime("%Y%m%d")
finalinks = pd.DataFrame(df_dic)
finalinks = finalinks.drop_duplicates()
finalinks.to_csv("%s" %'小区'+today + '.csv')






