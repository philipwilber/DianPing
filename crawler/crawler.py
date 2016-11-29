import requests
from lxml import etree

from utils import constant


class Scrapy(object):
    """description of class"""

    def __init__(self, **kwargs):
        return super().__init__(**kwargs)

    def get_tree(self, url, city, cat):
        url = url % (city, cat)
        # req = urllib.request.Request(url=url, headers=const.HEADER)
        # page = urllib.request.urlopen(req).read().decode(const.ENCODE_FORM)
        page = requests.get(url, headers=constant.HEADER)
        page.encoding = constant.ENCODE_FORM
        tree = etree.HTML(page.text)
        return tree

    def get_food_content(self):
        tree = self.get_tree(constant.DIAN_PING_URL, constant.CITIES['zhengzhou'], constant.CATEGORIES['food'])
        shop_list = tree.xpath('//*[@id="shop-all-list"]/ul/li')
        for x in range(len(shop_list)):
            item = tree.xpath('//*[@id="shop-all-list"]/ul/li[%s]/div[2]/div[1]/a[1]/@href' % (x+1))
            shop_url = constant.DIAN_PING_SHOP_URL + item[0]


# /li[1]/div[2]/div[1]/a[1]
# //*[@id="shop-all-list"]/ul/li[2]/div[2]/div[1]/a[1]






if __name__ == '__main__':
    s = Scrapy()
    s.get_food_content()