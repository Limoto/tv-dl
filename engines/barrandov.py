#!/usr/bin/env python3
#
__author__ = "Jakub Lužný"
__desc__ = "TV Barrandov (Video archív)"
__url__ = r"https?://(www.)?barrandov\.tv/video/(\d+)-.+"

import re,os.path
import xml.etree.ElementTree as ElementTree
from urllib.request import urlopen

class BarrandovEngine:

    def __init__(self, url):
        id = re.findall(__url__, url)[0][1]
        self.page = urlopen(url).read().decode('utf-8')

    def movies(self):        
        return [ ('0', re.findall(r'<meta property="og:title" content="(.*) \| Barrandov', self.page)[0]) ]
  
    def qualities(self):
        q = []

        if "720p HD" in re.findall(r"label: \"(.+?)\"", self.page):
            q.append( ('hd', 'HD' ) )
        
        q.append( ('low', 'Nízká') )

        return q

    def download(self, quality, movie):
        if not quality:
            quality = self.qualities()[0][0]
        
        playpath = re.findall(r"file: \"(.+?)\",", self.page)[0] #/video/2013/06/13102000060046_600_wide.mp4

        if quality == 'hd':
            playpath = playpath.replace('600_wide', 'HD_wide')

        filename = os.path.basename(playpath)
        return ("http", filename, {"url" : "http://www.barrandov.tv"+playpath})
