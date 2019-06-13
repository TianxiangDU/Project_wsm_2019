# -*- coding: utf-8 -*-  
import urllib.request

class HtmlDownloader(object): # To downloader the urls.
    def download(self, url):
        if url is None:
            return None
        response = urllib.request.urlopen(url)
        if response.getcode() != 200: # 200 means that it is successfully connected.
            return None
        return response.read()
