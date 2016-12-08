from utils import cons
from crawler import crawler



if __name__ == '__main__':
    cr = crawler.Crawler()
    cr.get_restaurant_content(cons.DIAN_PING_SEARCH_URL, cons.CITIES['zhengzhou'], cons.CATEGORIES['food'])
