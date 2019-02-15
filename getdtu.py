#!/usr/bin/python3
from urllib.request  import urlopen  
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os, sys
import re
from sys import argv
from tqdm import tqdm
import requests
import argparse
from programs import ProgOf
import jinja2
from jinja2 import Template
html_jinja_env = jinja2.Environment(
    trim_blocks = True,
    lstrip_blocks = True,
    autoescape = False,
    loader = jinja2.FileSystemLoader(os.path.abspath('.'))
    )
template = html_jinja_env.get_template('podcastpage_template.j2')
indexpagetemplate = html_jinja_env.get_template('indexpage_template.j2')

frontpageContext = {
'broadcast_date': '2019-02-11',
'title' : 'NotExist',
'episodes' : 0,
'podcasts' : []
}

# indexpageContext = {
#          'title' : ProgOf["287"]
#         'years' : [
#             {
#                 'name' : '2011',
#                 'podcasts' : [
#                     {
#                         'title' : 'sample',
#                         'episodes' : 14
#                         }
#                     ]
#                 }
#             ]        
# }

indexpageContext = {
'years' : []
}

def InsertIntoIndexPageContext():
    year = {}
    year["name"] = frontpageContext["broadcast_date"][0:4]
    podcast = {
            'title' : frontpageContext["title"],
            'episodes' : frontpageContext["episodes"]
            }
    found = False
    for itemyear in indexpageContext["years"]:
        if itemyear["name"] == year["name"]:
           itemyear["podcasts"].insert(0, podcast)
           found = True
           break
    if not found:
        year["podcasts"] = [ podcast ]
        indexpageContext["years"].insert(0, year)
    return

def PrintAllpCodes():
    i = 0
    for key in ProgOf:
       print('{0:>4s} : {1:20s}'.format(key,ProgOf[key]),end='  ')
       i += 1
       if i==4:
           print('')
           i=0
    if i > 0: print('')
    return 

def dl_tqdm_(url, file_name):
    # Streaming, so we can iterate over the response.
    r = requests.get(url, stream=True)

    # Total size in bytes.
    total_size = int(r.headers.get('content-length', 0)) 

    with tqdm(desc=file_name, total=total_size, ncols=50, unit='B', unit_scale=True) as pbar:
        with open(file_name, 'wb') as f:
            for data in r.iter_content(32*1024):
                f.write(data)
                pbar.update(len(data))

def Base(ProgramCode):
     return "http://podcast.rthk.hk/podcast/item_all.php?pid="+ProgramCode+"&lang=zh-CN"

def OutputOneSeriesHtml():
    # print(frontpageContext)
    f = open(frontpageContext["title"]+".html","w")
    f.write(template.render(frontpageContext))
    InsertIntoIndexPageContext()
    return

def CompileIndexPage():
    f = open("index.html","w")
    f.write(indexpagetemplate.render(indexpageContext))
    return

def ProcessEpisode(_date, _title, _url):
    if _title.find("（") == -1:
        x = _title.split("(")
    else:
        if _date == '2011-12-23':
            x = _title.split("(")
        else:    
            x = _title.split("（")    
    title = x[0].rstrip().lstrip()
    if title == '彼得大帝':
        title = '彼德大帝'
    try:
        caption = x[1]
    except:
        print(x)    
        print(frontpageContext)
    episode = {
                  'caption' : caption,
                  'url' : _url
              }
    if title != frontpageContext["title"]:
        if frontpageContext["title"] != "NotExist":
            OutputOneSeriesHtml()
        frontpageContext["broadcast_date"] = _date
        frontpageContext["title"] = title
        frontpageContext["episodes"] = 1
        frontpageContext["podcasts"] = [
            episode
        ]
    else:
        frontpageContext["broadcast_date"] = _date
        frontpageContext["podcasts"].insert(0, episode)
        frontpageContext["episodes"] = frontpageContext["episodes"] + 1
    return    




def grabPodcasts(pCode, from_date, to_date, pre_date, grab_now):
    if pCode not in ProgOf:
        PrintAllpCodes()
        return 1
    base = Base(pCode)
    html = urlopen(base)
    bsObj = BeautifulSoup(html,"lxml")
    indexpageContext["title"] = ProgOf[pCode]
    years = bsObj.findAll("a",{"class":re.compile("yearBox")})
    for year in years:
        if year["class"][1] == "close":
            html = urlopen(urljoin(base, year["href"]))
            bsObj = BeautifulSoup(html,"lxml")
        podcastList = bsObj.findAll("div",{"class":"epiItem video"})
        for podcast in podcastList:
            audio_html = urlopen(urljoin(base, podcast.a["href"]))
            bsObjAudio = BeautifulSoup(audio_html, "lxml")
            audio_url  = bsObjAudio.find("audio").get("src")
            audio_title = podcast.find("span",{"class":"title"}).string
            audio_date  = podcast.find("span",{"class":"date"}).string
            ProcessEpisode(audio_date, audio_title, audio_url)
    OutputOneSeriesHtml()
    CompileIndexPage()
    return 0

def check_arg(args=None):
    parser = argparse.ArgumentParser(description='Grab audio podcasts from RTHK 文化')
    parser.add_argument('-p', '--prog',
                        help='Program Code',
                        required='True',
                        default='287')
    parser.add_argument('-f', '--fromdate',
                        help='from YYYY-MM-DD',
                        default='1911-10-10')
    parser.add_argument('-t', '--todate',
                        help='to YYYY-MM-DD',
                        default='3000-07-01')
    parser.add_argument('-d', '--date',
                        action='store_true',
                        help='Prefix date to the mp3 filename')
    parser.add_argument('-g', '--grab',
                        action='store_true',
                        help='Grab podcasts')
    results = parser.parse_args(args)
    return (results.prog,
            results.fromdate,
            results.todate,
            results.date,
            results.grab)

if __name__ == '__main__':
    p, f, t, d, g = check_arg(sys.argv[1:])
    sys.exit(grabPodcasts(p, f, t, d, g))
