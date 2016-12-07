import re

import requests
from lxml import etree
from lxml.html.soupparser import fromstring
import time

from utils import cons


class Crawler(object):
    """description of class"""

    def __init__(self, **kwargs):
        pass

    def get_tree(self, url):
        # req = urllib.request.Request(url=url, headers=const.HEADER)
        # page = urllib.request.urlopen(req).read().decode(const.ENCODE_FORM)
        page = requests.get(url, headers=cons.HEADER)
        page.encoding = cons.ENCODE_FORM
        tree = fromstring(page.text)
        return tree

    def get_food_content(self, url, city, branch):
        url = url % (city, branch)
        tree = self.get_tree(url)
        shop_list = tree.xpath('//*[@id="shop-all-list"]/ul/li')
        for x in range(len(shop_list)):
            _shop_url = tree.xpath(
                '//*[@id="shop-all-list"]/ul/li[%s]/div[@class="txt"]/div[@class="tit"]/a[1]/@href' % (x + 1))
            ID = get_re_digits('\\\\*(\d+)', _shop_url[0])
            title = \
            tree.xpath('//*[@id="shop-all-list"]/ul/li[%s]/div[@class="txt"]/div[@class="tit"]/a[1]/@title' % (x + 1))[
                0].strip()
            features_list = tree.xpath(
                '//*[@id="shop-all-list"]/ul/li[%s]/div[@class="txt"]/div[@class="tit"]/div[@class="promo-icon"]/a/@class' % (
                x + 1))
            features = {}
            for y in range(len(features_list)):
                str = features_list[y]
                if 'igroup' == str:
                    features["groupon"] = 1
                elif 'ipromote' == str:
                    features["promotion"] = 1
                elif 'iout' == str:
                    features["out"] = 1
                elif 'icard' == str:
                    features["card"] = 1
                elif 'ibook' == str:
                    features["book"] = 1

            shop_url = cons.DIAN_PING_URL + _shop_url[0]
            shop_tree = self.get_tree(shop_url)
            region_url = shop_tree.xpath('//*[@id="body"]/div[2]/div[1]/a[2]/@href')[0]
            # eg. http://www.dianping.com/search/category/160/10/r7457
            region = 'r' + get_re_digits('r\/*(\d+)', region_url)

            cat_url = shop_tree.xpath('//*[@id="body"]/div[2]/div[1]/a[3]/@href')[0]
            # eg. http://www.dianping.com/search/category/160/10/g110r7457
            category = 'g' + get_re_digits('g\/*(\d+)', cat_url)
            address = \
            shop_tree.xpath('//*[@id="basic-info"]/div[@class="expand-info address"]/span[@class="item"]/@title')[
                0].strip()
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
                            shop_tree.xpath('//*[@id="basic-info"]/div[@class="other J-other Hide"]/p[%s]' % (y + 1))[
                                0].text.strip()
                        if node_str == '会员贡献：':
                            sys_upt_date = shop_tree.xpath(
                                '//*[@id="basic-info"]/div[@class="other J-other Hide"]/p[%s]/span[2]/span[3]/span' % (
                                y + 1))[0].text.strip()
                            sys_upt_date = get_re_digits('\d+-\d+-\d+', sys_upt_date[0].text.strip())

            stars = shop_tree.xpath('//*[@id="basic-info"]/div[1]/span[1]/@title')[0].strip()
            per_price = shop_tree.xpath('//*[@id="basic-info"]/div[1]/span[3]')[0].text.strip()
            per_price = get_re_digits('\s*(\d+)', per_price)
            lvl_taste = shop_tree.xpath('//*[@id="basic-info"]/div[1]/span[4]')[0].text.strip()
            lvl_taste = get_re_digits('\s*(\d.\d+)', lvl_taste)
            lvl_env = shop_tree.xpath('//*[@id="basic-info"]/div[1]/span[5]')[0].text.strip()
            lvl_env = get_re_digits('\s*(\d.\d+)', lvl_env)
            lvl_serv = shop_tree.xpath('//*[@id="basic-info"]/div[1]/span[6]')[0].text.strip()
            lvl_serv = get_re_digits('\s*(\d.\d+)', lvl_serv)
            review_num = shop_tree.xpath('//*[@id="basic-info"]/div[1]/span[2]')[0].text.strip()
            review_num = get_re_digits('\s*(\d+)', review_num)

            # Review
            dic_review = {}
            review_url = shop_url + '/review_all'
            review_tree = self.get_tree(review_url)
            page_nums = review_tree.xpath(
                '//*[@id="top"]/div[@class="shop-wrap shop-revitew"]/div[@class="main"]/div/div[@class="comment-mode"]/div[@class="Pages"]/div/a/@data-pg')
            page_nums = list(map(int, page_nums))
            page_max = max(page_nums)
            page_num = 1
            while page_num <= int(page_max):
                if page_num > 1:
                    review_url + cons.DIAN_PING_REV_PAGE + page_num
                    review_tree = self.get_tree(review_url)
                    # inside loop
                comment_list = review_tree.xpath(
                        '//*[@id="top"]/div[@class="shop-wrap shop-revitew"]/div[@class="main"]/div/div[@class="comment-mode"]/div[@class="comment-list"]/ul/li')
                comment_id_list = review_tree.xpath(
                        '//*[@id="top"]/div[@class="shop-wrap shop-revitew"]/div[@class="main"]/div/div[@class="comment-mode"]/div[@class="comment-list"]/ul/li/@data-id')
                comment_userid_list = review_tree.xpath(
                        '//*[@id="top"]/div[@class="shop-wrap shop-revitew"]/div[@class="main"]/div/div[@class="comment-mode"]/div[@class="comment-list"]/ul/li/div[@class="pic"]/a[1]/@user-id')
                comment_username_list = review_tree.xpath(
                        '//*[@id="top"]/div[@class="shop-wrap shop-revitew"]/div[@class="main"]/div/div[@class="comment-mode"]/div[@class="comment-list"]/ul/li/div[@class="pic"]/p[@class="name"]/a/text()')
                comment_rank_list = review_tree.xpath(
                        '//*[@id="top"]/div[@class="shop-wrap shop-revitew"]/div[@class="main"]/div/div[@class="comment-mode"]/div[@class="comment-list"]/ul/li/div[@class="content"]/div[@class="user-info"]/span[1]/@title')
                comment_taste_lvl_list = review_tree.xpath(
                        '//*[@id="top"]/div[@class="shop-wrap shop-revitew"]/div[@class="main"]/div/div[@class="comment-mode"]/div[@class="comment-list"]/ul/li/div[@class="content"]/div[@class="user-info"]/div/span[1]/text()')
                comment_env_lvl_list = review_tree.xpath(
                        '//*[@id="top"]/div[@class="shop-wrap shop-revitew"]/div[@class="main"]/div/div[@class="comment-mode"]/div[@class="comment-list"]/ul/li/div[@class="content"]/div[@class="user-info"]/div/span[2]/text()')
                comment_ser_lvl_list = review_tree.xpath(
                        '//*[@id="top"]/div[@class="shop-wrap shop-revitew"]/div[@class="main"]/div/div[@class="comment-mode"]/div[@class="comment-list"]/ul/li/div[@class="content"]/div[@class="user-info"]/div/span[3]/text()')
                comment_desc_list = review_tree.xpath(
                    '//*[@id="top"]/div[@class="shop-wrap shop-revitew"]/div[@class="main"]/div/div[@class="comment-mode"]/div[@class="comment-list"]/ul/li/div[@class="content"]/div[@class="comment-txt"]/div')
                comment_date_list = review_tree.xpath(
                    '//*[@id="top"]/div[@class="shop-wrap shop-revitew"]/div[@class="main"]/div/div[@class="comment-mode"]/div[@class="comment-list"]/ul/li/div[@class="content"]/div[@class="misc-info"]/span[1]/text()')

                if len(comment_list) > 0:
                    for y in range(len(comment_list)):
                        review_date = comment_date_list[y]
                        if(len(review_date) > 5):
                            review_date = get_re_digits("(\d+-\d+-\d+)", review_date)
                        else:
                            review_date = time.strftime("%y", time.localtime()) +'-'+ review_date
                        dic_review = {
                            "ID": comment_id_list[y],
                            "user_id": comment_userid_list[y],
                            "user_name": comment_username_list[y].strip(),
                            "rank": comment_rank_list[y],
                            "taste_lvl": get_re_digits('(\d+)', comment_taste_lvl_list[y]),
                            "env_lvl": get_re_digits('(\d+)', comment_env_lvl_list[y]),
                            "ser_lvl": get_re_digits('(\d+)', comment_ser_lvl_list[y]),
                            "desc": comment_desc_list[y].text_content().strip(),
                            "date": review_date
                        }
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
                   "review": dic_review
                   }






# /li[1]/div[2]/div[1]/a[1]
# //*[@id="shop-all-list"]/ul/li[2]/div[2]/div[1]/a[1]

def get_re_digits(pre_str, target_str):
    search_data = re.compile(r'' + pre_str)
    value_search = search_data.search(target_str)
    value = ''
    if value_search is not None:
        value = value_search.group(1)
    return value


if __name__ == '__main__':
    s = Crawler()
    s.get_food_content(cons.DIAN_PING_SEARCH_URL, cons.CITIES['zhengzhou'], cons.CATEGORIES['food'])
