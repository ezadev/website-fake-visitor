from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import Proxy,ProxyType
from time import sleep, ctime
import random
import asyncio
from proxybroker import Broker

HOMEPAGE = "https://khairu-aqsara.net"
BLOG_HOMEPAGE = "https://www.khairu-aqsara.net/blog"

class Visitor():
    def __init__(self,proxy_host,proxy_port, proxy_type):
        self.set_browser_proxy(proxy_host,proxy_port, proxy_type)
        print("[!] Visiting Url ", HOMEPAGE)
        opt = Options()
        opt.headless = True
        self.driver = webdriver.Chrome('./chromedriver', options=opt,desired_capabilities=self.capabilities)
        self.driver.get(HOMEPAGE)
        sleep(3)
        self.blog_link = self.driver.find_element_by_class_name('blog-link')
        self.blog_link.click()
        self.find_all_blog_post()

    def set_browser_proxy(self, host,port,isSSl):
        print("[!] Set Browser using Proxy {host}:{port}".format(host=host,port=port))
        self.prox = Proxy()
        self.prox.proxy_type = ProxyType.MANUAL
        if not isSSl:
            self.prox.http_proxy = "{ip_addr}:{port}".format(ip_addr=host,port=port)
        else:
            self.prox.ssl_proxy = "{ip_addr}:{port}".format(ip_addr=host,port=port)

        self.capabilities = webdriver.DesiredCapabilities.CHROME
        self.prox.add_to_capabilities(self.capabilities)

    def find_all_blog_post(self):
        print("[!] Finding all blog post link on ", BLOG_HOMEPAGE)
        self.blog_post = self.driver.find_elements_by_css_selector('.blog-post-title>a')
        self.list_page = []
        for link in self.blog_post:
            url_link = link.get_attribute('href')
            url_title= link.text
            self.list_page.append({'title':url_title,'url':url_link})
        
        print("[!] Found {num} blog post".format(num=len(self.list_page)))
        self.visit_random_blog_post()

    def visit_random_blog_post(self):
        print("[!] Visit random available blog post")
        selected_page = random.randint(0,len(self.list_page)-1)
        selected_page_info = self.list_page[selected_page]
        self.driver.get(selected_page_info['url'])
        assert selected_page_info['title'] == self.driver.title
        print("[!] Viewing page ", selected_page_info['title'])
        print("[!] stay on the page for 10s")
        sleep(10)
        self.quit_visitor()

    def quit_visitor(self):
        print("[!] Quiting browser")
        self.driver.quit()


async def run_visitor_from_proxy(proxies):
    while True:
        proxy = await proxies.get()
        if proxy is None:break
        isSSl = True if 'HTTPS' in proxy.types else False
        print('[!] Using Proxy:%s' % proxy)
        Visitor(proxy.host, proxy.port, isSSl)

proxies = asyncio.Queue()
broker = Broker(proxies)
task = asyncio.gather(
    broker.find(types=['HTTP','HTTPS'], limit=10),
    run_visitor_from_proxy(proxies)
)

loop = asyncio.get_event_loop()
loop.run_until_complete(task)