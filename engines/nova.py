#!/usr/bin/env python3
#
# založeno na původním nova-dl
__author__ = "Jakub Lužný"
__desc__ = "Nova (VOYO)"
__url__ = r"https?://voyo\.nova\.cz/.+"

import re,os.path, hashlib, base64
import xml.etree.ElementTree as ElementTree
from urllib.request import urlopen
from urllib.parse import urlencode
from datetime import datetime
import logging

log = logging.getLogger()

class NovaEngine:
    
    quality_names = {'hq' : 'Vysoká',
                     'lq' : 'Nízká' }
    
    def __init__(self, url):
        self.page = urlopen(url).read().decode('utf-8')
        self.get_playlist()
        
        self.medias = [(e.find('quality').text, e) for e in self.playlist.findall('mediaList/media')]
        log.debug('Kvality: {}'.format(', '.join(q for q, e in self.medias)))        
        if len(self.medias) == 0:
            raise ValueError('Není k dispozici žádná kvalita videa.')
        
    def qualities(self):
        q = []
        
        for e in self.medias:
            name = e[0]            
            desc = self.quality_names.get(name, name)
            q.append( (name, desc) )
        
        return q

    def movies(self):        
        return [ ('0', re.findall(r'<title>(.+?) - Voyo.cz', self.page)[0]) ]

    def get_playlist(self):        
        self.media_id = re.search(r'mainVideo = new mediaData\(\d+, \d+, (\d+),', self.page ).group(1)
        log.debug('Nalezeno media ID: {}'.format(self.media_id) )
        d = datetime.now()
        #datestring = d.strftime("%Y%m%d%H%M%S")
        datestring = urlopen("http://tn.nova.cz/lbin/time.php").read().decode('utf-8')[0:14]
        
        #šílenej hash... dostal jsem se k němu pomocí http://www.showmycode.com/ na 13-flowplayer.nacevi-3.1.5-02-002.swf

        m = hashlib.md5()
        m.update("nova-vod|{}|{}|chttvg.jkfrwm57".format(self.media_id, datestring ).encode('utf-8'))
        base64FromBA = base64.b64encode(m.digest() ) #, " /".encode('utf-8'))
        
        get = urlencode( [ ('t', datestring),
                           ('c', 'nova-vod|'+self.media_id),
                           ('h', "0"),
                           ('tm', 'nova'),
                           ('s', base64FromBA),
                           ('d', "1") ])
                           
        playlist_url = 'http://master-ng.nacevi.cz/cdn.server/PlayerLink.ashx?'+get
        
        log.debug("Získávám playlist z URL: "+playlist_url)
        playlist = urlopen(playlist_url).read().decode('utf-8')
        self.playlist = ElementTree.fromstring( playlist )
      
    def get_video(self, quality):
        if quality:
            try:
                e = dict(self.medias)[quality]
                log.info('Vybraná kvalita: {}'.format(quality))
                return e
            except:
                raise ValueError('Není k dispozici zadaná kvalita videa.')
         
        else:
            quality, e = self.medias[0]
            log.info('Automaticky vybraná kvalita: {}'.format(quality))

            return e

    def download(self, quality, movie):
        
        baseUrl = self.playlist.find('baseUrl').text
        log.debug('Base URL: {}'.format(baseUrl))
        e = self.get_video(quality)
        
        playpath = e.find('url').text
        
        filename = os.path.basename(playpath)[:-3] + 'flv'

        return ("rtmp", filename , { 'url' : baseUrl,
                                    'playpath' : playpath,
                                    'rtmpdump_args' : '--live'})

