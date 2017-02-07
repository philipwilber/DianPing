from pymongo import *

class DBProvider(object):

    def __init__(self):
        conn = MongoClient('localhost', 27017)
        self.db = conn.DB_DIANPING
        self.tb_restaurant = self.db.TB_RESTAURANT
        self.tb_cat = self.db.TB_CAT
        self.tb_url = self.db.TB_URL

    def add_restaurant(self, food_dic):
        self.tb_restaurant.insert(food_dic)

    def get_restaurant(self):
        return self.tb_restaurant.find()

    def check_shop_exist(self, ID):
        count = self.tb_restaurant.find({'ID': ID}).count()
        if count > 0:
            return 'Y'
        else:
            return 'N'

    def add_cat(self, cat_dic):
        self.tb_cat.insert(cat_dic)

    def get_cat(self):
        return self.tb_cat.find()

    def add_read_url(self, url, error):
        url_dic = {'url': url,
                   'error': error}
        self.tb_url.insert(url_dic)

    def check_url_exit(self, url):
        count = self.tb_url.find({'url': url}).count()
        if count > 0:
            return 'Y'
        else:
            return 'N'

if __name__ == '__main__':
    s = DBProvider()
    dic = s.get_restaurant()
    count = 0
    for item in dic:
        count = count + int(item['review_num'])
    print(count)