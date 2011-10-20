#!/usr/bin/env python3
#
# založeno na původním nova-dl
__author__ = "Jakub Lužný"
__desc__ = "Nova (VOYO)"
__url__ = r"http://voyo\.nova\.cz/.+"

import re,os.path, hashlib, base64
import xml.etree.ElementTree as ElementTree
from urllib.request import urlopen
from urllib.parse import urlencode
from datetime import datetime

class NovaEngine:

    def __init__(self, url):
        self.page = urlopen(url).read().decode('utf-8')
        self.get_playlist()
        
    def qualities(self):
        return [ ("mp4", "Vysoká"), ("flv", "Nízká") ]

    def movies(self):        
        return [ ('0', re.findall(r'<title>(.+?) - Voyo.cz', self.page)[0]) ]

    def get_playlist(self):

        self.media_id = re.search(r'var media_id = "(\d+)";', self.page ).group(1)
        d = datetime.now()
        datestring = d.strftime("%Y%m%d%H%M%S")
        
        #šílenej hash... dostal jsem se k němu pomocí http://www.showmycode.com/ na 13-flowplayer.nacevi-3.1.5-02-002.swf

        m = hashlib.md5()
        m.update("nova-vod|{}|{}|tajne.heslo".format(self.media_id, datestring ).encode('utf-8'))
        base64FromBA = base64.b64encode(m.digest(), " /".encode('utf-8'))
        
        get = urlencode( [ ('t', datestring),
                           ('c', 'nova-vod|'+self.media_id),
                           ('h', "0"),
                           ('tm', 'nova'),
                           ('s', base64FromBA),
                           ('d', "1") ])
                           
        self.playlist = ElementTree.fromstring( urlopen('http://master-ng.nacevi.cz/cdn.server/PlayerLink.ashx?'+get).read().decode('utf-8') )

    def get_video(self, quality):
        for e in self.playlist.findall('mediaList/media'):
            if e.find('quality').text == quality:
                return e

    def download(self, quality, movie):
        if not quality:
            quality = "mp4"
        
        baseUrl = self.playlist.find('baseUrl').text
        print(baseUrl)
        e = self.get_video(quality)
        
        playpath = e.find('url').text
        
        filename = os.path.basename(playpath)[:-3] + 'flv'

        return ("rtmp", filename , { 'url' : baseUrl,
                                    'playpath' : playpath,
                                    'rtmpdump_args' : '--live'})

