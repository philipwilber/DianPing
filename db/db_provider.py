from pymongo import *

class DBProvider(object):
    client = MongoClient('localhost', 27017)
    db_dianping = client.DB_DIANPING
    tb_food = db_dianping.food

    def add_food_shop(self, food_dic):
        id = food_dic['id']


