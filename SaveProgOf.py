#!/usr/bin/python3
from lxml import etree
import os, sys
import pickle
import requests
def allCulturalPodcastURL(page):
    return "https://podcast.rthk.hk/podcast/programmeList.php?type=audio&cid=0&page="+page+"&order=stroke&lang=zh-CN"
page = 0
remainder = '99'
ProgOf = {}
while (remainder != '0'):
    page = page + 1
    html = requests.get(allCulturalPodcastURL(str(page)))
    root = etree.fromstring(html.content)
    remainder = root.xpath('/programmeList/remainder')[0].text
    for programme in root.xpath('//programme'):
         title = programme.xpath('title')[0].text
         link = programme.xpath('link')[0].text
         x = link.split('=')
         id = x[1]
         ProgOf[id] = title
#print(ProgOf)         
pickle_out = open("ProgOf.pickle","wb")
pickle.dump(ProgOf, pickle_out)
pickle_out.close()        
