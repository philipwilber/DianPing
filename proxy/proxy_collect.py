import re
import sys
import requests

# reload(sys)
# sys.setdefaultencoding('utf-8')

# from crawler.crawler import Crawler
from utils import cons


# class ProxyCollection(object):
#     '''
#     ref. jhao104/proxy_pool
#     '''
#
#     def __init__(self):
#         self.craw = Crawler()
#         self.raw_proxy_queue = 'raw_proxy'
#         self.useful_proxy_queue = 'useful_proxy_queue'
#
#     def freeProxyFirst(self, page=10):
#         """
#         抓取快代理IP http://www.kuaidaili.com/
#         :param page: 翻页数
#         :return:
#         """
#         url_list = ('http://www.kuaidaili.com/proxylist/{page}/'.format(page=page) for page in range(1, page + 1))
#         # 页数不用太多， 后面的全是历史IP， 可用性不高
#         for url in url_list:
#             tree = self.craw.get_tree_direct(url)
#             proxy_list = tree.xpath('.//div[@id="index_free_list"]//tbody/tr')
#             for proxy in proxy_list:
#                 yield ':'.join(proxy.xpath('./td/text()')[0:2])
#
#     def freeProxySecond(self, proxy_number=100):
#         """
#         抓取代理66 http://www.66ip.cn/
#         :param proxy_number: 代理数量
#         :return:
#         """
#         url = "http://m.66ip.cn/mo.php?sxb=&tqsl={}&port=&export=&ktip=&sxa=&submit=%CC%E1++%C8%A1&textarea=".format(
#                 proxy_number)
#         html = requests.get(url)
#         #html.encoding = cons.ENCODE_FORM
#         for proxy in re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}', html.text):
#             yield proxy
#
#     def freeProxyThird(self, days=1):
#         """
#         抓取有代理 http://www.youdaili.net/Daili/http/
#         :param days:
#         :return:
#         Disabled now
#         """
#         url = "http://www.youdaili.net/Daili/http/"
#         tree = self.craw.get_tree_direct(url)
#         page_url_list = tree.xpath('.//div[@class="chunlist"]/ul//a/@href')[0:days]
#         for page_url in page_url_list:
#             html = requests.get(page_url).content
#             proxy_list = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}', html)
#             for proxy in proxy_list:
#                 yield proxy
#
#     def freeProxyFourth(self):
#         """
#         抓取西刺代理 http://api.xicidaili.com/free2016.txt
#         :return:
#         """
#         url = "http://api.xicidaili.com/free2016.txt"
#         html = requests.get(url).text
#         for proxy in re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}', html):
#             yield proxy
#
#     def freeProxyFifth(self):
#         """
#         抓取guobanjia http://www.goubanjia.com/free/gngn/index.shtml
#         :return:
#         """
#         url = "http://www.goubanjia.com/free/gngn/index.shtml"
#         tree = self.craw.get_tree_direct(url)
#         proxy_list = tree.xpath('.//td[@class="ip"]')
#         for proxy in proxy_list:
#             yield ''.join(proxy.xpath('.//text()'))


import re,requests,random

header={'headers':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}

class GatherProxy(object):
	'''To get proxy from http://gatherproxy.com/'''
	url='http://gatherproxy.com/proxylist'
	pre1=re.compile(r'<tr.*?>(?:.|\n)*?</tr>')
	pre2=re.compile(r"(?<=\(\').+?(?=\'\))")

	def getelite(self,pages=1,uptime=70,fast=True):
		'''Get Elite Anomy proxy
		Pages define how many pages to get
		Uptime define the uptime(L/D)
		fast define only use fast proxy with short reponse time'''

		proxies=set()
		for i in range(1,pages+1):
			params={"Type":"elite","PageIdx":str(i),"Uptime":str(uptime)}
			r=requests.post(self.url+"/anonymity/?t=Elite",params=params,headers=header)
			for td in self.pre1.findall(r.text):
				if fast and 'center fast' not in td:
					continue
				try:
					tmp= self.pre2.findall(str(td))
					if(len(tmp)==2):
						proxies.add(tmp[0]+":"+str(int('0x'+tmp[1],16)))
				except:
					pass
		return proxies

class ProxyPool(object):
	'''A proxypool class to obtain proxy'''

	gatherproxy=GatherProxy()

	def __init__(self):
		self.pool=set()

	def updateGatherProxy(self,pages=1,uptime=70,fast=True):
		'''Use GatherProxy to update proxy pool'''
		self.pool.update(self.gatherproxy.getelite(pages=pages,uptime=uptime,fast=fast))

	def removeproxy(self,proxy):
		'''Remove a proxy from pool'''
		if (proxy in self.pool):
			self.pool.remove(proxy)

	def randomchoose(self):
		'''Random Get a proxy from pool'''
		if (self.pool):
			return random.sample(self.pool,1)[0]
		else:
			self.updateGatherProxy()
			return random.sample(self.pool,1)[0]

	def getproxy(self):
		'''Get a dict format proxy randomly'''
		proxy=self.randomchoose()
		proxies={'http':'http://'+proxy,'https':'https://'+proxy}
		#r=requests.get('http://icanhazip.com',proxies=proxies,timeout=1)
		try:
			r=requests.get('http://www.baidu.com/',proxies=proxies,timeout=1)
			# http://icanhazip.com/
			if (r.status_code == 200 ):
				return proxies
			else:
				self.removeproxy(proxy)
				return self.getproxy()
		except:
			self.removeproxy(proxy)
			return self.getproxy()


if __name__ == '__main__':
    # test = ProxyCollection()
    # for e in test.freeProxyFifth():
    #     print(e)
    pro = ProxyPool()
    pool = pro.getproxy()
    print(pool)