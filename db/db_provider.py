from pymongo import *

class DBProvider(object):

    def __init__(self):
        conn = MongoClient('localhost', 27017)
        self.db = conn.DB_DIANPING
        self.tb_food_shop = self.db.TB_RESTAURANT
        self.tb_cat = self.db.TB_CAT




    def add_food_shop(self, food_dic):
        self.tb_food_shop.insert(food_dic)


    def get_food_shop(self):
        return self.tb_food_shop.find()

    def check_shop_exist(self, ID):
        count = self.tb_food_shop.find({'ID': ID}).count()
        if count > 0 :
            return 'Y'
        else:
            return 'N'

    def add_cat(self, cat_dic):
        self.tb_cat.insert(cat_dic)

    def get_cat(self):
        return self.tb_cat.find()





if __name__ == '__main__':
    s = DBProvider()
    dic = s.get_food_shop()
    count = 0
    for item in dic:
        count = count + int(item['review_num'])
    print(count)