#!/usr/bin/env python3
#time: 2017/07/30 12:26
#version: 1.0
#_author_:Benty_Yu

from bs4 import BeautifulSoup
import urllib
import gzip
import inspect
import re
import pandas as pd
import datetime
from time import sleep
# from sqlalchemy import create_engine
import glob
import os

patt_no = re.compile('\d+')
patt_url = re.compile('src=')
patt_location = re.compile(b'[\d.]+,[\d.]+,[\d.]+,[\d.]+,[\d.]+')
err_house_urls = []

def read_zip_url(url, encoding="gb18030"):
    '''
    获取网页信息
    :param url: 目标url
    :param encoding: 目标编码
    :return: 绑定内容后的beautifulsoup对象
    :others: 反防爬,出错后sleep 5s重试,可根据实际情况调整
    '''
    try:
        content = urllib.request.urlopen(url).read()
        content = gzip.decompress(content).decode(encoding)  # 网页gb2312的编码要用这个
        soup = BeautifulSoup(content, "lxml")
        return soup
    except Exception as e:
        print(e)
        print(inspect.stack()[1][3] + ' occused error')
        global err_house_urls
        err_house_urls.append(url)
        sleep(5)


def area_fourth_func(li, area_fourth=None):
    '''
    获取具体url
    :param li: 目标url
    :param area_fourth: 全局area_fourth列表
    :return:全局area_fourth列表
    '''
    if area_fourth == None:
        area_fourth = []
    soup = read_zip_url(li)
    if soup.find(text=re.compile("很抱歉")) == None:
        pagenum1 = soup.find_all('span', class_='txt')[0].get_text()
        pagenum = int(re.findall(r'\d+', pagenum1)[0])
        if pagenum != 1:
            for j in range(1, int(pagenum) + 1):
                new_url = (li[:-1] + '-' + 'i3{}'.format(j) + '/')
                area_fourth.append(new_url)
    # print(len(area_fourth))
    return area_fourth


def get_links(li, finalinks=None):
    '''
    获取具体链接
    :param li:  目标url
    :param finalinks: 全局finalinks列表
    :return: 全局finalinks列表
    '''
    if finalinks == None:
        finalinks = []
    soup = read_zip_url(li)
    urlist = soup.select('a[href^="/chushou/"]')
    for i in urlist:
        href = 'http://esf.km.fang.com' + i.get('href')
        if href not in finalinks:
            finalinks.append(href)


def take_area_url(root, key, i_type, dfl=None):
    '''
    获取筛选后url
    :param root: 当前url
    :param key: 筛选id str
    :param i_type: 筛选标签str
    :param dfl: 全局url列表
    :return: 全局url列表
    '''
    if dfl == None:
        dfl = []
    soup = read_zip_url(root)
    area_first_soup = soup.find_all(i_type, id=key)[0].find_all('a')
    # del area_first_soup[-2]
    # del area_first_soup[0]
    pre = "http://esf.km.fang.com"
    area_first = {pre + str(i.get('href')): i.text for i in area_first_soup if i.get('href')}
    print(area_first)
    dfl += area_first
    return dfl


class Details():
    # TODO:根据需求补充字段及保存方法
    def __init__(self):
        self.csv_path = 'demo.csv'

    def save_csv(self):
        # today = datetime.date.today().strftime("%Y%m%d")
        # finalinks = pd.DataFrame(finalinks)
        # finalinks = finalinks.drop_duplicates()
        # finalinks.to_csv("%s" % 'km_links' + today + '.csv')
        pass

    def save_db(self):
        # csvlist = glob.glob(os.path.join("", 'sf_links*.csv'))
        # temp = {}
        # for i in csvlist:
        #     temp[i] = os.path.getmtime(i)
        # filename = sorted(temp.items(), key=lambda item: item[1], reverse=True)[0][0]
        #
        # engine = create_engine('sqlite:///%s' % 'fuck.db', echo=False)
        # fullset = list(pd.read_csv(filename)['0'])
        # try:
        #     dataset = pd.DataFrame(df_dic, index=number)
        #     dataset = dataset.drop(['number'], axis=1)
        # except:
        #     dataset = pd.DataFrame()
        # dataset.to_sql('basic_information', engine, if_exists='append')
        pass


def take_detail(finalinks, encoding="utf-8"):
    ret_list = []
    for url in finalinks:
        global errorlist
        try:
            soup = read_zip_url(url, encoding)
            title = soup.find_all('div', class_='title', id='lpname')[0].get_text().strip()
            community = soup.find_all('div', class_='rcont')[0].find('a').get_text()
            area = soup.find_all('div', class_='rcont', id='address')[0].get_text().strip()
            # TODO:根据需要补充字段
            # info = soup.find_all('div', class_='inforTxt')
        except Exception as e:
            errorlist.append(url)
            print(e)

        # df_dic = {'title': title, 'area': area, 'community': community, 'price': price, 'room': room, 'date': date,
        #           'longitude': longitude, 'latitude': latitude, 'number': number, 'URL': URL, 'source': "房天下"}
        # TODO:根据需要补充字段
        df_dic = {'title': title, 'area': area, 'community': community, 'source': "房天下"}
        ret_list.append(df_dic)
    return ret_list


def take_1st_time():
    error_list = []
    start_url = "http://esf.km.fang.com/house/i31/"
    area_url_urls = take_area_url(start_url, 'list_D02_10', 'div')
    area_second = []
    for i in area_url_urls:
        take_area_url(i, 'list_D02_11', 'li', dfl=area_second)
        area_second = list(set(area_second))
    area_third = []
    for i in area_second:
        take_area_url(i, 'list_D02_13', 'li', dfl=area_third)
    area_third = list(set(area_third))
    area_fourth = []
    for i in area_third:
        area_fourth_func(i, area_fourth=area_fourth)
    area_fourth = list(set(area_fourth))
    finalinks = []
    for i in area_fourth:
        get_links(i, finalinks)
        detail_list = take_detail(finalinks)
        details = Details(detail_list)
        details.save_csv()
        finalinks = []  # 分步存储,防止数据太大爆内存及异常结束无结果


def take_house_page(url, all_list=None):
    if all_list == None:
        all_list = []
    soup = read_zip_url(url)
    brf = '/'.join(url.split('/')[:-2]) + '/'
    lists = soup.find_all('div', class_='listBox floatl')[0]
    page_str = lists.find_all('span', class_='txt')[0].text
    pages = int(patt_no.findall(page_str)[0])
    nums = patt_no.findall(url)
    url_patt = '%s__%s_%s_%s_%s_%s_%s_%s/'
    for i in range(1, pages + 1):
        new_list = nums[:-3] + [str(i), ] + nums[-2:]
        n_url = brf + url_patt % tuple(new_list)
        if n_url not in all_list:
            all_list.append(n_url)


class House:
    def __init__(self, url):
        self.url = url
        self.name = ''
        self.location = ()
        self.addr = ''
        self.area = ''
        self.post_code = ''
        self.ring_location = ''
        self.right_description = ''
        self.type = ''
        self.built_time = ''
        self.developer = ''
        self.building_structure = ''
        self.building_type = ''
        self.buiding_area = ''
        self.all_area = ''
        self.lived_in_no = ''
        self.all_in_no = ''
        self.green_rate = ''
        self.volume_ratio = ''
        self.manage_phone_num = ''
        self.payment = ''
        self.extra = ''
        self.manage_location = ''
        self.price = ''
        self.price_diff_last_month = ''
        self.selling_no = ''
        self.to_rent_no = ''
        self.location = 0, 0

    def do_print(self):
        # 要控制台输出啥自己改
        patt = 'name: {}, ring_location:{}, addr: {}\n green_rate: {}, developer: {}\n' \
               'lived_in: {}, phone: {}, selling_no: {}, to_rent_no: {}\nurl: {}'
        str_2_print = patt.format(self.name,  self.ring_location, self.addr,  self.green_rate,
                                  self.developer, self.lived_in_no, self.manage_phone_num, self.selling_no,
                                  self.to_rent_no, self.url)
        print(str_2_print)

    def to_csv_print(self):
        # 要csv保存输出啥自己改
        patt = '{},{},{}, {}, {}, {},{}, {}\n'
        str_2_print = patt.format(self.name, self.ring_location, self.addr,  self.green_rate,self.volume_ratio,
                                  self.developer,self.payment,  self.url)
        try:
            fp = open('小区详情.csv', 'a')
            fp.write(str_2_print)
            fp.close()
        except Exception as err:
            print('Handling save failed in url: %s, name: %s' % (self.url, self.name), err)





def take_house_detail(url):
    detail_url = url + 'xiangqing/'
    house = House(detail_url)
    soup0 = read_zip_url(url)
    try:
        house_br = soup0.find_all('div', class_='Rbigbt clearfix')[0]
        house.name = house_br.select('h1')[0].text
        
        soup1 = read_zip_url(detail_url)
        
        info = soup1.find_all('div', class_='inforwrap clearfix')[0]
        infos = info.select('dl > dd')
        for i in infos:
            if "：" in i.text:
                key, value = i.text.split('：')
                if key == "小区地址":
                    house.addr = value.strip()
                elif key == "所属区域":
                    house.area = value.strip()
                elif key == "邮    编":
                    house.post_code = value.strip()
                elif key == "环线位置":
                    house.ring_location = value.strip()
                elif key == "产权描述":
                    house.right_description = value.strip()
                elif key == "物业类别":
                    house.type = value.strip()
                elif key == "竣工时间":
                    house.built_time = value.strip()
                elif key == "开 发 商":
                    house.developer = value.strip()
                elif key == "建筑结构":
                    house.building_structure = value.strip()
                elif key == "建筑类别":
                    house.building_type = value.strip()
                elif key == "建筑面积":
                    house.buiding_area = value.strip()
                elif key == "占地面积":
                    house.all_area = value.strip()
                elif key == "当前户数":
                    house.lived_in_no = value.strip()
                elif key == "总 户 数":
                    house.all_in_no = value.strip()
                elif key == "绿 化 率":
                    house.green_rate = value.strip()
                elif key == "容 积 率":
                    house.volume_ratio = value.strip()
                elif key == "物业办公电话":
                    house.manage_phone_num = value.strip()
                elif key == "物 业 费":
                    house.payment = value.strip()
                elif key == "附加信息":
                    house.extra = value.strip()
                elif key == "物业办公地点":
                    house.manage_location = value.strip()
                else:
                    print(key.strip(), value.strip())
            else:
                print(detail_url, i.text)
    except Exception as err:
        print(err)
        print('error content with {}'.format(url))

    # house.do_print()
    house.to_csv_print()


def take_house(url):
    soup = read_zip_url(url)
    lists = soup.find_all('div', class_='listBox floatl')[0]
    house = lists.find_all('a', class_='plotTit')
    house_detail = []
    return [i.attrs.get('href') for i in house]
    # for i in house:
    #     act_url = i.attrs.get('href')
    #     house_detail.append(take_house_detail(act_url))
    # return house_detail


def take_all_areas(st):
    op, on = st.split('housing')
    on = '/housing' + on
    soup = read_zip_url(st)
    sch = soup.find_all('div', class_='search-con')[0]
    all_areas = sch.find_all('div', class_='qxName')[0]
    all_areas = all_areas.find_all('a')
    arr = []
    for i in all_areas:
        href = i.attrs.get('href')
        if not href.split('housing/')[-1].startswith('_'):
            i_url = op[:-1] + href
            if i_url != st:
                arr.append(i_url)
    return arr


def take_2nd_time():
    start_url = 'http://esf.km.fang.com/housing/__0_0_0_0_1_0_0/'
    fp = open('小区详情.csv', 'w')
    fp.write('name, type, price, addr, built_time, green_rate, developer, lived_in, phone,'
             'selling_no, to_rent_no, url, location\n')
    fp.close()
    all_areas = take_all_areas(start_url)
    # 分页不超过100， 无数据丢失，不再细分类型
    all_house_page = []
    for i in all_areas:
        take_house_page(i, all_house_page)
    all_house_url = []
    for i in all_house_page:
        all_house_url += take_house(i)
    all_house_url = list(set(all_house_url))
    print("Take all house url done! Count to {}".format(len(all_house_url)))
    url_str = '\n'.join(all_house_url)
    fp = open('house_url.txt', 'w')
    fp.write(url_str)
    fp.close()
    # house = [take_house(j) for j in all_house_page]
    # house = list(set(house))


def take_detail_of_house():
    fp = open('house_url.txt', 'r')
    house_urls = fp.readlines()
    fp.close()
    for i in house_urls:
        if i.startswith('http://'):
            take_house_detail(i.strip())
    global err_house_urls
    if err_house_urls:
        take_house_detail(i.strip())


def main():
    '''
    入口
    :return: None
    '''
    # take_1st_time() # 第一次需求，抓取单次房屋信息
    # take_2nd_time()  # 第二次需求，抓取小区信息，记录于house_url.txt
    take_detail_of_house()  # 小区url和detail分步处理节省时间


def test():
    url = 'http://esf.km.fang.com/chushou/3_154146002.htm'
    ret_list = [url, ]
    take_detail(ret_list)
    print(ret_list)
    return ret_list
    # get_links()


if __name__ == '__main__':
    main()  # 实际全量运行入口
    # test()  # 测试某功能入口
