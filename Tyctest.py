# -*- coding: utf-8 -*-
import random
import time
import json
import pymysql

from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains
from pyquery import PyQuery as pq

class Tyc(object):
    def __init__(self):
        global Url
        # browser = webdriver.Chrome()
        Url = 'https://www.tianyancha.com/'
        chrome_path = 'E:\chromedriver_win32\chromedriver.exe'
        self.conn = pymysql.connect(host="127.0.0.1", user="root", passwd="", db="cms", port=3306)
        self.cursor = self.conn.cursor()
        #self.driver = webdriver.Chrome(executable_path=chrome_path)
        #self.driver.get(Url)

    def parser_one_page(self, u, cityNum, areaName):
        try:
            #self.driver.get(u)
            # 获得页面
            html = self.driver.page_source
            doc = pq(html)
            items = doc('.result-list .search-item').items()
            for item in items:
                company_name = item.find('.content .header a').text()  # 公司名称
                company_link = item.find('.content .header a').attr('href')  # 详细链接
                zhuangtai = item.find('.content .header div').text()  # 公司状态
                daibiao = item.find('.content .info .title').eq(0).text().replace("法定代表人：", "")  # 法定代表人
                zhuceziben = item.find('.content .info .title').eq(1).text().replace("注册资本：", "")  # 注册资本
                chengli = item.find('.content .info .title').eq(2).text().replace("成立日期：", "")  # 成立日期
                dianhua = item.find('.content .contact div').eq(0).find('span').eq(1).text().replace("查看更多", "")  # 电话
                if item.find('.content .contact div').eq(0).find("script").text() != '':
                    dianhua = item.find('.content .contact div').eq(0).find("script").text().replace("[", "").replace(
                        "]", "").replace("\"", "")
                youxiang = item.find('.content .contact div').eq(1).find('span').eq(1).text()  # 邮箱
                if item.find('.content .contact div').eq(1).find('script').text() != '':
                    youxiang = item.find('.content .contact div').eq(1).find('script').text().replace("[", "").replace(
                        "]", "").replace("\"", "")
                qita = item.find('.content .match span').eq(1).text()  # 其他信息
                shengfen = item.find('.site').text()  # 省份
                score = item.find('.score').text()  # 评分

                yield {
                    'name': company_name,
                    'homepage': company_link,
                    'biz_status': zhuangtai,
                    'representative': daibiao,
                    'registered_capital': zhuceziben,
                    'setup_time': chengli,
                    'phone': dianhua,
                    'email': youxiang,
                    'other': qita,
                    'region': shengfen,
                    'score': score,
                    'address': '-',
                    'city': cityNum,
                    'district': areaName,
                    'lat_long': '-',
                    'register_code': '-',
                    'industry': '-',
                    'biz_scope': '-',
                    'company_type': '-',
                    'actual_capital': '-',
                    'taxpayer_code': '-',
                    'organization_code': '-',
                    'english_name': '-',
                    'authorization': '-',
                    'used_name': '-',
                    'credit_code': '-'
                }
        except IndexError as e:
            self.parser_one_page(u, cityNum, areaName)


    def get_plan(self):
        sql = "SELECT * FROM plan WHERE STATUS = 0 AND pvc_code = 'hun' AND city_code = 'zhangsha' AND (getnum < " \
              "total OR (getnum = 0 AND getnum = total))  ORDER BY id ASC"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        for pl in result:
            url = Url + 'search?key=' + pl[1] + '&base=' + pl[5] + '&areaCode=' + pl[7]
            #self.driver.get(url)
            print(url)
            #page = self.get_detail(".num.-end")
            #print(page)
            #self.update_page(pl[0], page)
            if pl[8] != pl[9] and pl[8] != 0:
                start = pl[8]
                end = pl[9] + 1
            else:
                start = 1
                end = pl[9] + 1
            print(start, end)
            for p in range(start, end):
                #self.update_per_page(pl[0], p)
                preurl = Url + 'search/p' + str(p) + '?key=' + str(pl[1]) + '&base=' + str(pl[5]) + '&areaCode=' + str(
                    pl[7])
                print(preurl)
                '''
                self.driver.get(preurl)
                for item in self.parser_one_page(preurl, pl[4], pl[6]):
                    # print(item)
                    # self.write_to_file(item)
                    self.insertdb(item)
                '''


    # 写入文件
    def write_to_file(self, c):  # 写入文本
        with open('tianyancha.txt', 'a', encoding='utf-8') as f:
            f.write(json.dumps(c, ensure_ascii=False) + '\n')


    def insertdb(self, data):
        sql = 'insert into enterprise(`name`,`representative`,`address`,`region`,`city`,`district`,' \
              '`lat_long`,`biz_status`,`credit_code`,`register_code`,`phone`,`email`,`setup_time`,' \
              '`industry`, `biz_scope`,`company_type`,`registered_capital`,`actual_capital`,' \
              '`taxpayer_code`, `organization_code`,`english_name`,`authorization`,`homepage`,' \
              '`used_name`,`gmt_create`, `gmt_modify`) ' \
              'values(%(name)s,%(representative)s,%(address)s,%(region)s,%(city)s,%(district)s,' \
              '%(lat_long)s,%(biz_status)s,%(credit_code)s,%(register_code)s,%(phone)s,%(email)s,' \
              '%(setup_time)s, %(industry)s,%(biz_scope)s,%(company_type)s,%(registered_capital)s,' \
              '%(actual_capital)s, %(taxpayer_code)s,%(organization_code)s,%(english_name)s,' \
              '%(authorization)s,%(homepage)s, %(used_name)s,now(),now()) '
        self.write_tx(sql, data)


    def update_per_page(self, id, page):
        sql = "update plan set getnum = " + str(page) + " where id = " + str(id)
        self.cursor.execute(sql)
        self.conn.commit()

    def update_page(self, id, total):
        sql = "update plan set total =" + str(total) + " where id = " + str(id)
        self.cursor.execute(sql)
        self.conn.commit()

    def get_detail(self, selector):
        html = self.driver.page_source
        doc = pq(html)
        item = doc.find(selector).text()
        if item == "":
            return 0
        else:
            item = int(item[3:])
        return item

    def entrace(self):
        self.get_plan()
        # for i in range(1, 250):
        # u = Url +'search/p'+str(i)+'?key=管道'
        # self.driver.get(u)
        # for item in self.parser_one_page(u):
        # print(item)
        # self.write_to_file(item)
        # self.insertdb(item)
        self.cursor.close()
        self.conn.close()


if __name__ == '__main__':
    tyc = Tyc()
    tyc.entrace()
