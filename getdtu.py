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

frontpageContext = {
'broadcast_date': '2019-02-11',
'title' : 'NotExist',
'podcasts' : []
}

def SetupJinja():
    html_jinja_env = jinja2.Environment(
	    trim_blocks = True,
	    lstrip_blocks = True,
	    autoescape = False,
	    loader = jinja2.FileSystemLoader(os.path.abspath('.'))
    )
    template = html_jinja_env.get_template('frontpage_template.j2')
    return

#print(template.render(frontpageContext))

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
    total_size = int(r.headers.get('content-length', 0)); 

    with tqdm(desc=file_name, total=total_size, ncols=50, unit='B', unit_scale=True) as pbar:
        with open(file_name, 'wb') as f:
            for data in r.iter_content(32*1024):
                f.write(data)
                pbar.update(len(data))

def Base(ProgramCode):
     return "http://podcast.rthk.hk/podcast/item_all.php?pid="+ProgramCode+"&lang=zh-CN"

def OutputOneSeriesHtml():
    return

def ProcessEpisode(_date, _title, _url):
    x = _title.split("(")
    title = x[0].rstrip()
    caption = x[1]
    episode = {
                  'caption' : caption,
                  'url' : _url
              }
    if title != frontpageContext["title"]:
        OutputOneSeriesHtml()
        frontpageContext["broadcast_date"] = _date
        frontpageContext["title"] = title
        frontpageContext["podcasts"] = [
            episode
        ]
    else:
        frontpageContext"podcasts"].insert(0, episode)
    return    




def grabPodcasts(pCode, from_date, to_date, pre_date, grab_now):
    if pCode not in ProgOf:
        PrintAllpCodes()
        return 1
    base = Base(pCode)
    in_tran  = '/:上中下一二三四五六七八九十'
    out_tran = '-_ABC123456789O'
    del_tran = " ()\t"
    tranTable = str.maketrans(in_tran, out_tran, del_tran)
    html = urlopen(base)
    bsObj = BeautifulSoup(html,"lxml")
    titlePath = bsObj.title.string[9:].translate(tranTable)
    # if grab_now == True:
    #    if os.path.exists(titlePath) == False:
    #        os.mkdir(titlePath)
    print(titlePath)
    years = bsObj.findAll("a",{"class":re.compile("yearBox")})
    for year in years:
        if pre_date == False:
            print(year.string)
        if year["class"][1] == "close":
            html = urlopen(urljoin(base, year["href"]))
            bsObj = BeautifulSoup(html,"lxml")
        podcastList = bsObj.findAll("div",{"class":"epiItem video"})
        for podcast in podcastList:
            audio_html = urlopen(urljoin(base, podcast.a["href"]))
            bsObjAudio = BeautifulSoup(audio_html, "lxml")
            audio_url  = bsObjAudio.find("audio").get("src")
     #       audio_title = podcast.find("span",{"class":"title"}).string.translate(tranTable)
            audio_title = podcast.find("span",{"class":"title"}).string
            audio_date  = podcast.find("span",{"class":"date"}).string
            if pre_date == True: 
                audio_title = audio_date + audio_title
            if from_date <= audio_date <= to_date:
                #download(audio_url, titlePath+'/'+audio_title+'.mp3')
                if grab_now == True:
                #    dl_tqdm_(audio_url, titlePath+'/'+audio_title+'.mp3')
                    print(audio_title+' '+audio_url)
                else:
                    print(audio_title)
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
    SetupJinja()
    p, f, t, d, g = check_arg(sys.argv[1:])
    sys.exit(grabPodcasts(p, f, t, d, g))
