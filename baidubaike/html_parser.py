# -*- coding: utf-8 -*-  
import re
from urllib.parse import urljoin
from bs4 import  BeautifulSoup


class HtmlParser(object):
    def parse(self, page_url, html_content):
        if page_url == None or html_content == None:
            return
        soup = BeautifulSoup(
            html_content,
            "html.parser",
            from_encoding="utf-8"
        )
        new_urls  = self._get_new_urls(page_url, soup)
        new_data =  self._get_new_data(page_url, soup)
        return new_urls, new_data
        
    def _get_new_urls(self, page_url, soup):
        new_urls = set()
        links1 = soup.select('li.item > a')
        links2 = soup.select('div.lemma-summary > div.para > a')
        links = links1 + links2
        #print(links)
        if links == None:
            new_urls == None
        else:
            for link in links:
                new_url = link.get("href")
                new_full_url =  urljoin(page_url, new_url)
                new_urls.add(new_full_url)
        return new_urls

    def _get_new_data(self, page_url, soup):
        res_data ={}

        title_node = soup.find("dd", class_="lemmaWgt-lemmaTitle-title").find("h1")
        res_data["title"] =  title_node.get_text()

        summary_node = soup.find("div",class_="lemma-summary")
        res_data["summary"]  = summary_node.get_text()

        res_data["url"]  = page_url

        subtitle_node = soup.find("dd", class_="lemmaWgt-lemmaTitle-title").find("h2")
        if subtitle_node == None:
            res_data["subtitle"] = ""
        else:
            res_data["subtitle"] = subtitle_node.get_text()

        image_node = soup.find("div", class_="summary-pic")
        if image_node == None:
            res_data["image"] = ""
        else:
            url_image = soup.select('div.summary-pic > a')[0]["href"]
            res_data["image"] = urljoin(page_url, url_image)
            
        return res_data