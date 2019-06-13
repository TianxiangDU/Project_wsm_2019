# -*- coding: utf-8 -*-  
import url_manager
import html_downloader
import html_parser
import urllib
import mysql.connector
import traceback
#function of MySQL
db_cnx = mysql.connector.connect(user='root', password='123456', database='baidubaike',charset='utf8mb4')
def save_sql(data):
    cursor = db_cnx.cursor()
    
    add_entry = ("INSERT INTO BAIKE_ENTRY" \
        "(title, subtitle, url, summary, image_link)" \
        "VALUES (%(title)s, %(subtitle)s, %(url)s, %(summary)s, %(image_link)s)")
    data_entry = {
        'title':data["title"],
        'subtitle':data["subtitle"],
        'url':data["url"],
        'summary':data["summary"],
        'image_link':data["image"]
    }

    cursor.execute(add_entry, data_entry)

    db_cnx.commit()
    cursor.close()

class SpiderMain(object):
    def __init__(self):
        self.urls = url_manager.UrlManager()
        self.downloader = html_downloader.HtmlDownloader()
        self.parser = html_parser.HtmlParser()

    def crawl(self, root_url):
        count = 1
        self.urls.add_new_url(root_url)
        while self.urls.has_new_url():
            try:
                new_url = self.urls.get_new_url()
                print("crawl" %d : %s" %(count, new_url))
                html_cont = self.downloader.download(new_url)
                new_urls, new_data = self.parser.parse(new_url, html_cont)
                self.urls.add_new_urls(new_urls)
                save_sql(new_data) # save in MySQL.
                #print(new_data)

                if count == 250: # the number of crawls in one time.
                    break
                count = count + 1
            except:
                traceback.print_exc() # get the errer info.
                print('crawl failed')



keyword = "KEYWORD" # ANY keyword you want.
root_url = "http://baike.baidu.com/item/" + urllib.parse.quote(keyword, encoding='utf8')
obj_spider = SpiderMain()
obj_spider.crawl(root_url)

db_cnx.close() # close the connection of the MySQL.
