import re

import requests
from lxml import etree

from utils import cons


class Scrapy(object):
    """description of class"""

    def __init__(self, **kwargs):
        return super().__init__(**kwargs)

    def get_tree(self, url):
        # req = urllib.request.Request(url=url, headers=const.HEADER)
        # page = urllib.request.urlopen(req).read().decode(const.ENCODE_FORM)
        page = requests.get(url, headers=cons.HEADER)
        page.encoding = cons.ENCODE_FORM
        tree = etree.HTML(page.text)
        return tree

    def get_food_content(self, city, branch):
        url = cons.DIAN_PING_SEARCH_URL % (city, branch)
        tree = self.get_tree(url)
        shop_list = tree.xpath('//*[@id="shop-all-list"]/ul/li')
        for x in range(len(shop_list)):
            item = tree.xpath('//*[@id="shop-all-list"]/ul/li[%s]/div[2]/div[1]/a[1]/@href' % (x+1))
            shop_url = cons.DIAN_PING_URL + item[0]
            shop_tree = self.get_tree(shop_url)
            ID = get_re_digits('\\\\*(\d+)', shop_url)
            title = shop_tree.xpath('//*[@id="basic-info"]/h1')[0].text.strip()

            region_url = shop_tree.xpath('//*[@id="body"]/div[2]/div[1]/a[2]/@href')[0]
            # eg. http://www.dianping.com/search/category/160/10/r7457
            region = 'r' + get_re_digits('r\/*(\d+)', region_url)

            cat_url = shop_tree.xpath('//*[@id="body"]/div[2]/div[1]/a[3]/@href')[0]
            # eg. http://www.dianping.com/search/category/160/10/g110r7457
            category = 'g' + get_re_digits('g\/*(\d+)', cat_url)
            address = shop_tree.xpath('//*[@id="basic-info"]/div[@class="expand-info address"]/span[@class="item"]/@title')[0].strip()
            tel = shop_tree.xpath('//*[@id="basic-info"]/p[@class="expand-info tel"]/span[2]')[0].text.strip()
            #open_hour = shop_tree.xpath('//*[@id="basic-info"]/div[@class="other J-other"]/p[@class="info info-indent"]/span[@class="item"]')[0].text.strip()
            #open_hour = shop_tree.xpath('//*[@id="basic-info"]/div[3]/p[1]/span[2]')[0].text.strip()
            info_indent_list = shop_tree.xpath('//*[@id="basic-info"]/div[@class="other J-other"]/p')
            if len(info_indent_list) > 0:
                #for y in range(len(info_indent_list)):
                for item in info_indent_list:
                    str = item.xpath('//*span[1]')[0].text.strip()
                    if str == '营业时间：':
                        str2 = item.xpath('//*span[2]')[0].text.strip()


            stars = shop_tree.xpath('//*[@id="basic-info"]/div[1]/span[1]/@title')[0].strip()
            comment_num = shop_tree.xpath('//*[@id="basic-info"]/div[1]/span[2]')[0].text.strip()
            comment_num = get_re_digits('\s*(\d+)', comment_num)
            per_price = shop_tree.xpath('//*[@id="basic-info"]/div[1]/span[3]')[0].text.strip()
            per_price = get_re_digits('\s*(\d+)', per_price)
            lvl_taste = shop_tree.xpath('//*[@id="basic-info"]/div[1]/span[4]')[0].text.strip()
            lvl_taste = get_re_digits('\s*(\d.\d+)', lvl_taste)
            lvl_env = shop_tree.xpath('//*[@id="basic-info"]/div[1]/span[5]')[0].text.strip()
            lvl_env = get_re_digits('\s*(\d.\d+)', lvl_env)
            lvl_serv = shop_tree.xpath('//*[@id="basic-info"]/div[1]/span[6]')[0].text.strip()
            lvl_serv = get_re_digits('\s*(\d.\d+)', lvl_serv)


            dic = {"ID" : ID,
                   "title" : title,
                   "region" : region,
                   "category" : category,
                   "address" : address,
                   "tel": tel,
                   "open_hour": open_hour,
                   "stars": stars,
                   "comment_num": comment_num,
                   "per_price": per_price,
                   "lvl_taste": lvl_taste,
                   "lvl_env": lvl_env,
                   "lvl_serv": lvl_serv}





''
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
    s = Scrapy()
    s.get_food_content(cons.CITIES['zhengzhou'], cons.CATEGORIES['food'])