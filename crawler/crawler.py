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

    def get_food_content(self):
        url = cons.DIAN_PING_URL % (cons.CITIES['zhengzhou'], cons.CATEGORIES['food'])
        tree = self.get_tree(url)
        shop_list = tree.xpath('//*[@id="shop-all-list"]/ul/li')
        for x in range(len(shop_list)):
            item = tree.xpath('//*[@id="shop-all-list"]/ul/li[%s]/div[2]/div[1]/a[1]/@href' % (x+1))
            shop_url = cons.DIAN_PING_SHOP_URL + item[0]
            shop_tree = self.get_tree(shop_url)
            re_method = re.compile(r'\\*(\d+)')
            ID = re_method.search(shop_url).group(1)
            title = shop_tree.xpath('//*[@id="basic-info"]/h1')[0].text
            region_url = shop_tree.xpath('//*[@id="body"]/div[2]/div[1]/a[3]/@href')[0]
            #http://www.dianping.com/search/category/160/10/r9191
            re_method = re.compile(r'')




''
# /li[1]/div[2]/div[1]/a[1]
# //*[@id="shop-all-list"]/ul/li[2]/div[2]/div[1]/a[1]






if __name__ == '__main__':
    s = Scrapy()
    s.get_food_content()