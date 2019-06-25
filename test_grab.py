#!/usr/bin/python3
from lxml import etree
import os, sys
from sys import argv
from tqdm import tqdm
import requests
import argparse
# from programs import ProgOf
import pickle
import jinja2
from jinja2 import Template
pickle_in = open('ProgOf.pickle','rb')
ProgOf = pickle.load(pickle_in)
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
Pages = []

indexpageContext = {
'years' : []
}

def SavePickle():
    #pickle_out = open("Pages.pickle","wb")
    #pickle.dump(Pages, pickle_out)
    #pickle_out.close()
    #print(Pages)
    for page in Pages:
        OutputOneSeriesHtml(page)
    #print(indexpageContext)    
    #pickle_out = open("Index.pickle","wb")
    #pickle.dump(indexpageContext, pickle_out)
    #pickle_out.close()
    return

def getPage(title):
    for page in Pages:
        if page["title"] == title:
            return page
    newpageContext = frontpageContext.copy()        
    newpageContext["broadcast_date"] = ""
    newpageContext["title"] = title
    newpageContext["episodes"] = 0
    newpageContext["podcasts"] = []
    Pages.append(newpageContext)
    return newpageContext

def InsertIntoIndexPageContext(page):
    year = {}
    year["name"] = page["broadcast_date"][0:4]
    podcast = {
            'title' : page["title"],
            'episodes' : page["episodes"]
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

def OutputOneSeriesHtml(page):
    # print(page)
    f = open(page["title"]+".html","w")
    f.write(template.render(page))
    print(page["title"]+".html")
    InsertIntoIndexPageContext(page)
    return

def CompileIndexPage():
    f = open("index.html","w")
    f.write(indexpagetemplate.render(indexpageContext))
    return

def ProcessEpisode(_date, _title, _url, pCode, generate_pickle):
    if pCode == '287':
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
    elif pCode == '1069':
        if _title.find("（") == -1:
            if _title.find("(") == -1:
                x = [_title, _title]
            else:
                x = _title.split("(")    
        else:    
            x = _title.split("（")    
        title = x[0].rstrip().lstrip()
    #elif pCode == '328':        
    elif pCode == '486':        
        if _title.find("(") == -1:
            x = [_title, _title]
        else:
            x = _title.split("(")    
        title = x[0].rstrip().lstrip()
    elif pCode == '249':        
        if _title.startswith("佛經講座："):
            _title = _title[5:]
        if _title.find("之") == -1:
            if _title.find("（") == -1:
               if _title.find("(") == -1:
                   x = [_title, _title]
               else:
                   x = _title.split("(")    
            else:    
               x = _title.split("（")
        else:           
            x = _title.split("之")    
        title = x[0].rstrip().lstrip()
    else:
        if _title.find("(") == -1:
            x = _title.split("-")
        else:
            x = _title.split("(")    
        title = x[0].rstrip().lstrip()
    try:
        caption = x[1]
    except:
        print(x)    
        print(frontpageContext)
    episode = {
                  'caption' : caption,
                  'url' : _url
              }
    if generate_pickle:
        page = getPage(title)
        page["broadcast_date"] = _date
        page["podcasts"].insert(0, episode)
        page["episodes"] = page["episodes"] + 1
        return          
    
    if title != frontpageContext["title"]:
        if frontpageContext["title"] != "NotExist":
            OutputOneSeriesHtml(frontpageContext)
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

def NewBase(ProgramCode):
     return "https://podcast.rthk.hk/podcast/item.php?pid="+ProgramCode

def episodeList(ProgramCode, Year, Page):
     return "https://podcast.rthk.hk/podcast/episodeList.php?pid="+ProgramCode+"&year="+Year+"&page="+Page+"&lang=zh-CN"

def grabPodcasts(pCode, from_date, to_date, display_only, generate_pickle):
    if pCode not in ProgOf:
        PrintAllpCodes()
        return 1
  # in_tran  = '/:上中下一二三四五六七八九十'
    in_tran  = ''
  # out_tran = '-_ABC123456789O'
    out_tran = ''
    del_tran = " ?\t'"
    tranTable = str.maketrans(in_tran, out_tran, del_tran)
    html=requests.get(NewBase(pCode))
    indexpageContext["title"] = ProgOf[pCode]
    years = etree.HTML(html.content).xpath('//option[@value]')
    for year in years:
        page = 0
        remainder = "99"
        while (remainder != "0"):
            page = page + 1
            xml = requests.get(episodeList(pCode, year.text, str(page))) 
            root = etree.fromstring(xml.content)
            remainder = root.xpath('/episodeList/remainder')[0].text
            for episode in root.xpath('//episode'):
                audio_date = episode.xpath('episodeDate')[0].text
                audio_title = episode.xpath('episodeTitle')[0].text
                audio_url = episode.xpath('mediafile')[0].text
##            if display_only:
                print(audio_date, audio_title, audio_url)
##            else:    

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
    parser.add_argument('-d', '--displayonly',
                        action='store_true',
                        help='Display the list of date,title,url')
    parser.add_argument('-g', '--generate',
                        action='store_true',
                        help='Generate pickle')
    results = parser.parse_args(args)
    return (results.prog,
            results.fromdate,
            results.todate,
            results.displayonly,
            results.generate)

if __name__ == '__main__':
    p, f, t, d, g = check_arg(sys.argv[1:])
    sys.exit(grabPodcasts(p, f, t, d, g))
