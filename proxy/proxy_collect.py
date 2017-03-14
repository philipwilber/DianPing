import re, requests, random
import json

header = {
    'headers': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}


class GatherProxy(object):
    '''To get proxy from http://gatherproxy.com/'''
    url = 'http://gatherproxy.com/proxylist'
    # update regular expression rule
    # pre1 = re.compile(r'<tr.*?>(?:.|\n)*?</tr>')
    # pre2 = re.compile(r"(?<=\(\').+?(?=\'\))")
    pre = re.compile(r'(?<=insertPrx\().+?(?=\)\;)')

    def getelite(self, pages=1, uptime=70, fast=True):
        '''Get Elite Anomy proxy
        Pages define how many pages to get
        Uptime define the uptime(L/D)
        fast define only use fast proxy with short reponse time'''

        proxies = set()
        for i in range(1, pages + 1):
            params = {"Type": "elite", "PageIdx": str(i), "Uptime": str(uptime)}
            r = requests.post(self.url + "/anonymity/?t=Elite", params=params, headers=header)
            for item in self.pre.findall(r.text):
                data = json.loads(item)
                if int(data['PROXY_TIME']) <= 150:
                    try:
                        proxies.add(data['PROXY_IP'] + ':' + str(int('0x' + data['PROXY_PORT'], 16)))
                    except:
                        pass

            # for td in self.pre1.findall(r.text):
            #     if fast and 'center fast' not in td:
            #         continue
            #     try:
            #         tmp = self.pre2.findall(str(td))
            #         if (len(tmp) == 2):
            #             proxies.add(tmp[0] + ":" + str(int('0x' + tmp[1], 16)))
            #     except:
            #         pass
        return proxies


class ProxyPool(object):
    '''A proxypool class to obtain proxy'''

    gatherproxy = GatherProxy()

    def __init__(self):
        self.pool = set()

    def updateGatherProxy(self, pages=1, uptime=70, fast=True):
        '''Use GatherProxy to update proxy pool'''
        self.pool.update(self.gatherproxy.getelite(pages=pages, uptime=uptime, fast=fast))

    def removeproxy(self, proxy):
        '''Remove a proxy from pool'''
        if (proxy in self.pool):
            self.pool.remove(proxy)

    def randomchoose(self):
        '''Random Get a proxy from pool'''
        if (self.pool):
            return random.sample(self.pool, 1)[0]
        else:
            self.updateGatherProxy()
            return random.sample(self.pool, 1)[0]

    def getproxy(self):
        '''Get a dict format proxy randomly'''
        proxy = self.randomchoose()
        proxies = {'http': 'http://' + proxy, 'https': 'https://' + proxy}
        # r=requests.get('http://icanhazip.com',proxies=proxies,timeout=1)
        try:
            r = requests.get('http://www.baidu.com/', proxies=proxies, timeout=1)
            # http://icanhazip.com/
            if (r.status_code == 200):
                return proxies
            else:
                self.removeproxy(proxy)
                return self.getproxy()
        except:
            self.removeproxy(proxy)
            return self.getproxy()


if __name__ == '__main__':
    pro = ProxyPool()
    pool = pro.getproxy()
    print(pool)
