from utils import cons
from crawler import crawler
import threading
from datetime import datetime


cr = crawler.Crawler()

def main_crawler(url):
    cr.get_restaurant_content(url)

def main():
    now = datetime.now()  # start timing
    print(now)
    thread = []
    url_list = []
    dic_cat = cr.get_all_cat_url_from_db()
    for item in dic_cat:
        url = cons.DIAN_PING_URL + str(item['url'])
        # main_crawler(url)
        next = False
        for url_str in url_list:
            if url_str == url:
                next = True
                break
        if next == False:
            print('Now to get -------- ' + url)
            t = threading.Thread(target=main_crawler,
                                 args=(url,))
        thread.append(t)

    for i in range(0, 3):
        thread[i].start()

    for i in range(0, 3):
        thread[i].join()

    end = datetime.now()  # end timing
    print(end)
    print('Run time： ' + str(end - now))


if __name__ == '__main__':
    main()


