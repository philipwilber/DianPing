from pymongo import *

class DBProvider(object):

    def __init__(self):
        conn = MongoClient('localhost', 27017)
        self.db = conn.DB_DIANPING
        self.tb_food_shop = self.db.TB_RESTAURANT




    def add_food_shop(self, food_dic):
        self.tb_food_shop.insert(food_dic)


    def get_food_shop(self):
        for item in self.tb_food_shop.find():
           print(item)





if __name__ == '__main__':
    s = DBProvider()
    s.get_food_shop()