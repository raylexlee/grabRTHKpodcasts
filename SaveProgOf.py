#!/usr/bin/python3
from urllib.request  import urlopen  
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os, sys
import re
import pickle
# culturalPodcastsUrl = 'http://podcast.rthk.hk/podcast/list_category.php?lang=zh-CN&action=do_rthk_cat&rthk_cat=%E6%96%87%E5%8C%96'
# html = urlopen(culturalPodcastsUrl)
allPodcastsUrl = 'http://podcast.rthk.hk/podcast/list_all.php?lang=zh-CN'
html = urlopen(allPodcastsUrl)
bsObj = BeautifulSoup(html,"lxml")
podcastsLinks = bsObj.findAll("a",{"href":re.compile("item_epi")})
ProgOf = {}
for podcastsLink in podcastsLinks:
    id = podcastsLink["href"][17:]
    title = podcastsLink.find("div",{"class":"prog-title"})
    if title.span["class"][0] == "icon-audio":
        ProgOf[id] = title.get_text()
pickle_out = open("ProgOf.pickle","wb")
pickle.dump(ProgOf, pickle_out)
pickle_out.close()        
