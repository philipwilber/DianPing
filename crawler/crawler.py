import re

import sys
import requests
from lxml import etree
import lxml.html
import time
import json
import webbrowser
import threading
from datetime import datetime


from utils import cons
from db import db_provider
from proxy import proxy_collect


class Crawler(object):
    """description of class"""

    def __init__(self, **kwargs):
        self.db = db_provider.DBProvider()

    def get_html(self, url, proxies, is_check_url):
        if is_check_url:
            is_exit = self.db.check_url_exit(url)
        else:
            is_exit = 'N'
        if is_exit != 'Y':
            proxy = proxy_collect.ProxyPool()
            try:
                # req = urllib.request.Request(url=url, headers=const.HEADER)
                # page = urllib.request.urlopen(req).read().decode(const.ENCODE_FORM)
                if proxies != None:
                    page = requests.get(url, headers=cons.HEADER, proxies=proxies, timeout=cons.TIMEOUT)
                else:
                    page = requests.get(url, headers=cons.HEADER, timeout=cons.TIMEOUT)
                if page.status_code == 200 or page.status_code == 404:
                    page.encoding = cons.ENCODE_FORM
                    return page.text
                else:
                    if page.status_code == 403:
                        # webbrowser.open_new(url)
                        input_text = input("Please Enter Verification Code in Browser!")
                    else:
                        print(str(url) + ' Connection Error : ' + str(page.status_code) + ' Change to new proxy : ')
                    proxies_set = proxy.getproxy()
                    print(proxies_set)
                    return self.get_html(url, proxies_set, is_check_url)
            except:
                print("Unexpected error:", sys.exc_info())
                print("Change to new proxy : ")
                proxies_set = proxy.getproxy()
                print(proxies_set)
                return self.get_html(url, proxies_set, is_check_url)
        else:
            return 'Y'


    def get_tree_direct(self, url):
        # get tree without checking auth code page
        try:
            page_text = self.get_html(url, None, False)
            tree = etree.HTML(page_text)
            print('(etree)Read Page Time:' + str(datetime.now()) + '   Url: ' + url)
            self.db.add_read_url(url, 0)
            return tree
        except:
            print("Unexpected error:", sys.exc_info())

    def get_tree(self, url, page_text, etree_to_html = False):
        # get tree with checking auth code page
        try:
            if(etree_to_html == False):
                # get xpath by etree
                tree = etree.HTML(page_text)
            else:
                # get xpath by lxml.html to handle multi-line text
                tree = lxml.html.fromstring(page_text)
            if tree.xpath('/html/head/title/text') == '验证码':
                if self.get_auth_code() == True:
                    self.get_tree(url, self.get_html(url, None), etree_to_html, False)
            else:
                if(etree_to_html == False):
                    print('(etree)Read Page Time:' + str(datetime.now()) + '   Url: ' + url)
                    self.db.add_read_url(url, 0)
                else:
                    print('(lxml.html.fromstring)Read Page Time:' + str(datetime.now()) + ' Url : ' + url)
                return tree
        except:
            print("Unexpected error:", sys.exc_info())


    def get_restaurant_content(self, url):
        thread = []
        page_text = self.get_html(url, None, False)
        if page_text != 'Y' :
            tree = self.get_tree(url, page_text, False)
            # get next page url, it will be used at the end of this method to recursive loop
            page_next = tree.xpath('//*[@id="top"]/div[6]/div[3]/div[1]/div[2]/a[@class="next"]/@href')
            # get all restaurant infomation in current page
            shop_list = tree.xpath('//*[@id="shop-all-list"]/ul/li/div[1]')

            for x in range(len(shop_list)):
                t = threading.Thread(target=self.get_restaurant_detail,
                                     args=(x, tree,))
                thread.append(t)

            for i in range(0, len(thread)):
                thread[i].start()

            for i in range(0, len(thread)):
                thread[i].join()

            if len(page_next) > 0:
                next_url = cons.DIAN_PING_URL + page_next[0]
                self.get_restaurant_content(next_url)
            else:
                return "next"
        else:
            print('Duplicate Url: ' + url)


    def get_restaurant_detail(self, x, tree):
            _shop_url = tree.xpath(
                '//*[@id="shop-all-list"]/ul/li[%s]/div[@class="txt"]/div[@class="tit"]/a[1]/@href' % (x + 1))
            ID = get_re_digits('\\\\*(\d+)', _shop_url[0])
            is_exit = self.db.check_shop_exist(ID)
            if is_exit != 'Y':
                title = \
                    tree.xpath(
                        '//*[@id="shop-all-list"]/ul/li[%s]/div[@class="txt"]/div[@class="tit"]/a[1]/@title' % (x + 1))[
                        0].strip()
                features_list = tree.xpath(
                    '//*[@id="shop-all-list"]/ul/li[%s]/div[@class="txt"]/div[@class="tit"]/div[@class="promo-icon"]/a/@class' % (
                        x + 1))
                features = {}
                for y in range(len(features_list)):
                    item = features_list[y]
                    if 'igroup' == item:
                        features["groupon"] = 1
                    elif 'ipromote' == item:
                        features["promotion"] = 1
                    elif 'iout' == item:
                        features["out"] = 1
                    elif 'icard' == item:
                        features["card"] = 1
                    elif 'ibook' == item:
                        features["book"] = 1

                shop_url = cons.DIAN_PING_URL + _shop_url[0]
                shop_tree = self.get_tree(shop_url, self.get_html(shop_url, None, False), False)
                region_url = shop_tree.xpath('//*[@id="body"]/div[2]/div[1]/a[2]/@href')[0]
                # eg. http://www.dianping.com/search/category/160/10/r7457
                region = 'r' + get_re_digits('r\/*(\d+)', region_url)

                cat_url = shop_tree.xpath('//*[@id="body"]/div[2]/div[1]/a[3]/@href')[0]
                # eg. http://www.dianping.com/search/category/160/10/g110r7457
                category = 'g' + get_re_digits('g\/*(\d+)', cat_url)
                address = \
                    shop_tree.xpath(
                        '//*[@id="basic-info"]/div[@class="expand-info address"]/span[@class="item"]/@title')[
                        0].strip()
                tel = shop_tree.xpath('//*[@id="basic-info"]/p[@class="expand-info tel"]/span[2]')
                if len(tel) > 0:
                    tel = shop_tree.xpath('//*[@id="basic-info"]/p[@class="expand-info tel"]/span[2]')[0].text.strip()
                info_indent_list = shop_tree.xpath('//*[@id="basic-info"]/div[@class="other J-other Hide"]/p')
                sys_upt_date = ''
                shop_desc = ''
                if len(info_indent_list) > 0:
                    for y in range(len(info_indent_list)):
                        node = shop_tree.xpath(
                            '//*[@id="basic-info"]/div[@class="other J-other Hide"]/p[%s]/span[1]' % (y + 1))
                        if len(node) > 0:
                            node_str = node[0].text.strip()
                            if node_str == '营业时间：':
                                open_hours = shop_tree.xpath(
                                    '//*[@id="basic-info"]/div[@class="other J-other Hide"]/p[%s]/span[2]' % (y + 1))[
                                    0].text.strip()
                            if node_str == '餐厅简介：':
                                shop_desc = \
                                    shop_tree.xpath(
                                        '//*[@id="basic-info"]/div[@class="other J-other Hide"]/p[%s]' % (y + 1))[
                                        0].text.strip()
                            if node_str == '会员贡献：':
                                sys_upt_date = shop_tree.xpath(
                                    '//*[@id="basic-info"]/div[@class="other J-other Hide"]/p[%s]/span[2]/span[3]/span' % (
                                        y + 1))[0].text.strip()
                                sys_upt_date = get_re_digits('\d+-\d+-\d+', sys_upt_date[0].text.strip())

                stars = shop_tree.xpath('//*[@id="basic-info"]/div[1]/span[1]/@title')[0].strip()
                review_span_num = shop_tree.xpath('//*[@id="basic-info"]/div[1]/span[@class="item"]')
                # 有无评论
                if len(review_span_num) > 4:
                    review_num = shop_tree.xpath('//*[@id="basic-info"]/div[1]/span[2]')[0].text.strip()
                    review_num = get_re_digits('\s*(\d+)', review_num)
                    per_price = shop_tree.xpath('//*[@id="basic-info"]/div[1]/span[3]')[0].text.strip()
                    per_price = get_re_digits('\s*(\d+)', per_price)
                    lvl_taste = shop_tree.xpath('//*[@id="basic-info"]/div[1]/span[4]')[0].text.strip()
                    lvl_taste = get_re_digits('\s*(\d.\d+)', lvl_taste)
                    lvl_env = shop_tree.xpath('//*[@id="basic-info"]/div[1]/span[5]')[0].text.strip()
                    lvl_env = get_re_digits('\s*(\d.\d+)', lvl_env)
                    lvl_serv = shop_tree.xpath('//*[@id="basic-info"]/div[1]/span[6]')[0].text.strip()
                    lvl_serv = get_re_digits('\s*(\d.\d+)', lvl_serv)
                else:
                    # 有均价无评论 或 无均价有评论
                    first_span_text =shop_tree.xpath('//*[@id="basic-info"]/div[1]/span[2]')[0].text.strip()
                    if first_span_text[0] == '人':
                        review_num = 0
                        per_price = shop_tree.xpath('//*[@id="basic-info"]/div[1]/span[2]')[0].text.strip()
                        per_price = get_re_digits('\s*(\d+)', per_price)
                    else:
                        review_num = shop_tree.xpath('//*[@id="basic-info"]/div[1]/span[2]')[0].text.strip()
                        review_num = get_re_digits('\s*(\d+)', review_num)
                        per_price = 0
                    lvl_taste = shop_tree.xpath('//*[@id="basic-info"]/div[1]/span[3]')[0].text.strip()
                    lvl_taste = get_re_digits('\s*(\d.\d+)', lvl_taste)
                    lvl_env = shop_tree.xpath('//*[@id="basic-info"]/div[1]/span[4]')[0].text.strip()
                    lvl_env = get_re_digits('\s*(\d.\d+)', lvl_env)
                    lvl_serv = shop_tree.xpath('//*[@id="basic-info"]/div[1]/span[5]')[0].text.strip()
                    lvl_serv = get_re_digits('\s*(\d.\d+)', lvl_serv)


                dic_review_list = []
                if review_num != 0:
                    # Review
                    review_url = shop_url + '/review_all'
                    review_page_text = self.get_html(review_url, None, True)
                    review_tree = self.get_tree(review_url, review_page_text, False)
                    review_tree_by_html = self.get_tree(review_url, review_page_text, True)

                    page_nums = review_tree.xpath(
                        '//*[@id="top"]/div[@class="shop-wrap shop-revitew"]/div[@class="main"]/div/div[@class="comment-mode"]/div[@class="Pages"]/div/a/@data-pg')
                    if len(page_nums) > 0:
                        page_nums = list(map(int, page_nums))
                        page_max = max(page_nums)
                    else:
                        page_max = 1
                    page_num = 1
                    while page_num <= int(page_max):
                        if page_num > 1:
                            review_url = shop_url + '/review_all' + cons.DIAN_PING_REV_PAGE + str(page_num)
                            review_page_text = self.get_html(review_url, None, False)
                            review_tree = self.get_tree(review_url, review_page_text, False)
                            review_tree_by_html = self.get_tree(review_url, review_page_text, True)
                            # inside loop
                        comment_list = review_tree.xpath(
                            '//*[@id="top"]/div[@class="shop-wrap shop-revitew"]/div[@class="main"]/div/div[@class="comment-mode"]/div[@class="comment-list"]/ul/li')
                        comment_id_list = review_tree.xpath(
                            '//*[@id="top"]/div[@class="shop-wrap shop-revitew"]/div[@class="main"]/div/div[@class="comment-mode"]/div[@class="comment-list"]/ul/li/@data-id')
                        comment_userid_list = review_tree.xpath(
                            '//*[@id="top"]/div[@class="shop-wrap shop-revitew"]/div[@class="main"]/div/div[@class="comment-mode"]/div[@class="comment-list"]/ul/li/div[@class="pic"]/a[1]/@user-id')
                        comment_username_list = review_tree.xpath(
                            '//*[@id="top"]/div[@class="shop-wrap shop-revitew"]/div[@class="main"]/div/div[@class="comment-mode"]/div[@class="comment-list"]/ul/li/div[@class="pic"]/p[@class="name"]/a/text()')

                        # move into for loop
                        # comment_desc_list = review_tree.xpath(
                        #     '//*[@id="top"]/div[@class="shop-wrap shop-revitew"]/div[@class="main"]/div/div[@class="comment-mode"]/div[@class="comment-list"]/ul/li/div[@class="content"]/div[@class="comment-txt"]/div')
                        comment_date_list = review_tree.xpath(
                            '//*[@id="top"]/div[@class="shop-wrap shop-revitew"]/div[@class="main"]/div/div[@class="comment-mode"]/div[@class="comment-list"]/ul/li/div[@class="content"]/div[@class="misc-info"]/span[1]/text()')

                        if len(comment_list) > 0:
                            for y in range(len(comment_list)):
                                # add date formating to fix review_date due to free-text-formate
                                review_date = comment_date_list[y]
                                if (len(review_date) > 5):
                                    review_date = get_re_digits("(\d+-\d+-\d+)", review_date)
                                else:
                                    review_date = time.strftime("%y", time.localtime()) + '-' + review_date

                                # if description includes "更多", the div will divides into two sub-div.
                                comment_desc_div = review_tree_by_html.xpath(
                                    '//*[@id="top"]/div[@class="shop-wrap shop-revitew"]/div[@class="main"]/div/div[@class="comment-mode"]/div[@class="comment-list"]/ul/li[%s]/div[@class="content"]/div[@class="comment-txt"]/div' % (
                                        y + 1))
                                comment_desc = ''
                                if len(comment_desc_div) > 1:
                                    comment_desc = comment_desc_div[1].text_content().strip()
                                else:
                                    comment_desc = comment_desc_div[0].text_content().strip()

                                # in case none rank or comment lvl
                                comment_rank = review_tree.xpath(
                                    '//*[@id="top"]/div[@class="shop-wrap shop-revitew"]/div[@class="main"]/div/div[@class="comment-mode"]/div[@class="comment-list"]/ul/li[%s]/div[@class="content"]/div[@class="user-info"]/span[1]/@title' % (y + 1))
                                if len(comment_rank) > 0:
                                    comment_rank_str = comment_rank
                                else:
                                    comment_rank_str = '无'
                                comment_taste_lvl = review_tree.xpath('//*[@id="top"]/div[@class="shop-wrap shop-revitew"]/div[@class="main"]/div/div[@class="comment-mode"]/div[@class="comment-list"]/ul/li[%s]/div[@class="content"]/div[@class="user-info"]/div/span[1]/text()' % (y + 1))
                                if len(comment_taste_lvl) > 0 :
                                    comment_taste_lvl_str = comment_taste_lvl[0]
                                else:
                                    comment_taste_lvl_str = '0'
                                comment_env_lvl = review_tree.xpath('//*[@id="top"]/div[@class="shop-wrap shop-revitew"]/div[@class="main"]/div/div[@class="comment-mode"]/div[@class="comment-list"]/ul/li[%s]/div[@class="content"]/div[@class="user-info"]/div/span[2]/text()' % (y + 1))
                                if len(comment_env_lvl) > 0:
                                    comment_env_lvl_str = comment_env_lvl[0]
                                else:
                                    comment_env_lvl_str = '0'
                                comment_ser_lvl = review_tree.xpath('//*[@id="top"]/div[@class="shop-wrap shop-revitew"]/div[@class="main"]/div/div[@class="comment-mode"]/div[@class="comment-list"]/ul/li[%s]/div[@class="content"]/div[@class="user-info"]/div/span[3]/text()' % (y + 1))
                                if len(comment_ser_lvl) > 0:
                                    comment_ser_lvl_str = comment_ser_lvl[0]
                                else:
                                    comment_ser_lvl_str = '0'

                                dic_review = {
                                    "ID": comment_id_list[y],
                                    "user_id": comment_userid_list[y],
                                    "user_name": comment_username_list[y].strip(),
                                    "rank": comment_rank_str,
                                    "taste_lvl": get_re_digits('(\d+)', comment_taste_lvl_str),
                                    "env_lvl": get_re_digits('(\d+)', comment_env_lvl_str),
                                    "ser_lvl": get_re_digits('(\d+)', comment_ser_lvl_str),
                                    "desc": comment_desc,
                                    "date": review_date
                                }
                                dic_review_list.append(dic_review)
                        page_num = page_num + 1
                        #

                dic = {"ID": ID,
                       "title": title,
                       "features": features,
                       "region": region,
                       "category": category,
                       "address": address,
                       "tel": tel,
                       "open_hour": open_hours,
                       "shop_desc": shop_desc,
                       "sys_upt_date": sys_upt_date,
                       "stars": stars,
                       "per_price": per_price,
                       "lvl_taste": lvl_taste,
                       "lvl_env": lvl_env,
                       "lvl_serv": lvl_serv,
                       "review_num": review_num,
                       "review": dic_review_list
                       }
                self.db.add_restaurant(dic)
                print('Records ID:' + ID + ' Title: ' + title)
            else:
                print('Duplicate record : ID"' + ID)

    def get_auth_code(self):
        # tree = self.get_tree(
        #     'http://h5.dianping.com/platform/secure/index.html?returl=http://www.dianping.com/shop/23437592/review_all?pageno=20')
        # url = tree.xpath('//*[@id="J_code"]/@src')
        # print(url)
        # webbrowser.open_new(url)
        content = requests.get(cons.DIAN_PING_AUTH_URL, headers=cons.HEADER)
        content_text = str(content.text)
        content_text = content_text.replace('EasyLoginCallBack1(','').replace('}})','}}')
        dic_image = json.loads(content_text)
        print(dic_image)
        pic_url = dic_image['msg']['url']
        webbrowser.open_new(pic_url)
        input_text = input("Enter Verification Code:")
        auth_content_text = requests.get('http://m.dianping.com/account/ajax/checkCaptcha?vcode='+input_text+'&signature='+dic_image['msg']['signature'], headers=cons.HEADER)
        dic_auth = json.loads(auth_content_text.text)
        if(dic_auth['code'] == 200):
            print("Verification Success")
            return True
        else:
            self.get_auth_code()


        #pic = requests.get(pic_url,headers=cons.HEADER)

    def get_all_cat_from_html(self, city, branch):
        url = 'https://www.dianping.com/shopall/' + str(city) +'/' + str(branch) + '#BDBlock'
        tree = self.get_tree_direct(url)
        url_list = tree.xpath('(//a[@class="B"]/@href)|(//a[@class="Bravia"]/@href)')
        name_list = tree.xpath('(//a[@class="B"]/text())|(//a[@class="Bravia"]/text())')
        for i in range(len(url_list)):
            dic={
                'url' : url_list[i],
                'name' : name_list[i],
                'city': city,
                'branch': branch,
                'is_crawler' : 0
            }
            self.db.add_cat(dic)
        return url_list

    def get_all_cat_url_from_db(self):
        # dic =  self.db.get_cat()
        # print(type(dic))
        # for item in dic:
        #     print(item['url'])
        returned_cursor = self.db.get_cat()
        # objects = []
        # for object in returned_cursor:
        #     objects.append(object)
        return returned_cursor


def get_re_digits(pre_str, target_str):
    search_data = re.compile(r'' + pre_str)
    value_search = search_data.search(target_str)
    value = ''
    if value_search is not None:
        value = value_search.group(1)
    return value


if __name__ == '__main__':
    s = Crawler()
    # print(s.get_all_cat_url_from_db())
    s.get_all_cat_from_html(cons.CITIES['zhengzhou'], cons.CATEGORIES['food'])
    #s.get_restaurant_content('http://www.dianping.com/search/category/160/10/r65849')
    # s.get_auth_code()
    #s.get_all_cat_from_db()
    #s.get_restaurant_content(cons.DIAN_PING_SEARCH_URL, cons.CITIES['zhengzhou'], cons.CATEGORIES['food'])
    # s.get_auth_code()

    # review_page_text = s.get_html('http://www.dianping.com/shop/23603901/review_all?pageno=79', None)
    # review_tree = s.get_tree('http://www.dianping.com/shop/23603901/review_all?pageno=79', review_page_text, False)
    # comment_taste_lvl = review_tree.xpath(
    #     '//*[@id="top"]/div[@class="shop-wrap shop-revitew"]/div[@class="main"]/div/div[@class="comment-mode"]/div[@class="comment-list"]/ul/li[%s]/div[@class="content"]/div[@class="user-info"]/div/span[1]/text()' % (
    #     4))
    # if len(comment_taste_lvl) > 0:
    #     comment_taste_lvl_str = comment_taste_lvl[0]
    # else:
    #     comment_taste_lvl_str = '0'
    # comment_env_lvl = review_tree.xpath(
    #     '//*[@id="top"]/div[@class="shop-wrap shop-revitew"]/div[@class="main"]/div/div[@class="comment-mode"]/div[@class="comment-list"]/ul/li[%s]/div[@class="content"]/div[@class="user-info"]/div/span[2]/text()' % (
    #     4))
    # if len(comment_env_lvl) == 0:
    #     comment_env_lvl_str = comment_env_lvl[0]
    # else:
    #     comment_env_lvl_str = '0'
    # comment_ser_lvl = review_tree.xpath(
    #     '//*[@id="top"]/div[@class="shop-wrap shop-revitew"]/div[@class="main"]/div/div[@class="comment-mode"]/div[@class="comment-list"]/ul/li[%s]/div[@class="content"]/div[@class="user-info"]/div/span[3]/text()' % (
    #     4))
    # if len(comment_ser_lvl) == 0:
    #     comment_ser_lvl_str = comment_ser_lvl[0]
    # else:
    #     comment_ser_lvl_str = '0'
