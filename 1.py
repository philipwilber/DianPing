import requests
from lxml import etree



def get_tree():
        #url = DIAN_PING_URL  % (CITIES['zhengzhou'], CATEGORIES['food'])
        # req = urllib.request.Request(url=url, headers=const.HEADER)
        # page = urllib.request.urlopen(req).read().decode(const.ENCODE_FORM)
        r = requests.get(DIAN_PING_URL, headers=HEADER)
        r.close()
        #r.encoding = ENCODE_FORM
        #tree = etree.HTML(page.text)
        print(r.decode('utf-8').text)


get_tree()
