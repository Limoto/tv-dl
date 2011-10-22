#!/usr/bin/env python3
#
__author__ = "Jakub Lužný"
__desc__ = "TV Barrandov (Video archív)"
__url__ = r"http://(www.)?barrandov\.tv/(\d+)-.+"

import re,os.path
import xml.etree.ElementTree as ElementTree
from urllib.request import urlopen

class BarrandovEngine:

    def __init__(self, url):
        id = re.findall(__url__, url)[0][1]
        self.page = urlopen(url).read().decode('utf-8')
        self.playlist = ElementTree.fromstring( urlopen('http://www.barrandov.tv/special/videoplayerdata/'+id).read().decode('utf-8') )

    def movies(self):        
        return [ ('0', re.findall(r'<title>(.+?) -  Video Archív - TV Barrandov', self.page)[0]) ]
  
    def qualities(self):
        q = []
        
        if self.playlist.find('hasquality').text == 'true':
            q.append( ('high', 'Vysoká' ) )
        
        if self.playlist.find('hashdquality').text == 'true':
            q.append( ('hd', 'HD' ) )

        q.append( ('low', 'Nízká') )

        return q

    def download(self, quality, movie):
        if not quality:
            quality = 'low'
        
        playpath = self.playlist.find('streamname').text
        hostname = self.playlist.find('hostname').text
        if quality == 'high':
            playpath = playpath.replace('500', '1000')
        elif quality == 'hd':
            playpath = playpath.replace('500', 'HD')
        
        rtmp = 'rtmpe://' + hostname + '/' + playpath
  
        
        filename = os.path.basename(playpath)[4:-3] + 'flv'

        return ("rtmp", filename , { 'url' : rtmp,
                                     'token' : '#ed%h0#w@1',
                                     'rtmpdump_args' : '--live' } )
