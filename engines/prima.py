#!/usr/bin/env python3
#
__author__ = "Jakub Lužný"
__desc__ = "TV Prima Videoarchiv"
__url__ = r"https?://play\.iprima\.cz/.*"

import re,os.path,random,math,logging
import xml.etree.ElementTree as ElementTree
from urllib.request import urlopen, Request
from os.path import basename

log = logging.getLogger()

class PrimaEngine:

    def __init__(self, url):
        self.url = url
        self.page = urlopen(url).read().decode('utf-8')
        
        if "http://flash.stream.cz/swf/streamPlayer_558.swf" in self.page:
            self.protocol = "cdn"
        else:
            self.protocol = "rtmp"

    def movies(self):        
        return [ ('0', re.findall(r'<meta property="og:title" content="(.+?)" />', self.page)[0]) ]
  
    def qualities(self):
        q = [('low', 'Nízká')]
        if self.protocol == "rtmp":
            q.append( ('high', 'Vysoká') )
        return q

    def download(self, quality, movie):
        if self.protocol == "rtmp":
            if quality and quality not in ['low', 'high']:
                raise ValueError('Není k dispozici zadaná kvalita videa.')
            
            if not quality:
                quality = 'high'
                log.info('Automaticky vybraná kvalita: {}'.format(quality))
                
            return self.download_rtmp(quality)
        elif self.protocol == "cdn":
            if quality and quality != 'low':
                raise ValueError('Není k dispozici zadaná kvalita videa.')
            
            if not quality:
                log.info('Automaticky vybraná kvalita: low')
            return self.download_cdn()
            
    def download_rtmp(self, quality):
        
        hq = re.findall( r"'hq_id':'(.+?)'", self.page)[0]
        lq = re.findall( r"'lq_id':'(.+?)'", self.page)[0]
        
        playpath = ""
        if quality == "low":
            playpath = lq
        else:
            playpath = hq
            
        playerUrl = 'http://embed.livebox.cz/iprimaplay/player-embed-v2.js?__tok{}__={}'.format(
                         math.floor(random.random()*1073741824),
                         math.floor(random.random()*1073741824))
        
        req = Request(playerUrl, None, {'Referer' : self.url} )
        player = urlopen(req).read().decode('utf-8')
        
        baseUrl = ''.join( re.findall( r"embed\['stream'\] = '(.+?)'.+'(\?auth=)'.+'(.+?)';", player)[1] )

        return ("rtmp", playpath[:-3]+'flv' , { 'url' : baseUrl+'/'+playpath,
                                     'rtmpdump_args' : '--live'})
    
    def download_cdn(self):
        cdnId = re.findall(r"cdnID=(\d+)", self.page)[0]
        #přesměrování
        url = urlopen("http://cdn-dispatcher.stream.cz/?id="+cdnId).geturl()
        filename =  basename(url).split('?')[0]
        
        return ('http', filename, { 'url' : url } )
