#!/usr/bin/env python3
#
__author__ = "Jakub Lužný"
__desc__ = "TV Prima Videoarchiv"
__url__ = r"https?://.*\.iprima\.cz/.*/.*"

import re,os.path,random,math,logging,json
import xml.etree.ElementTree as ElementTree
from urllib.request import urlopen, Request
from os.path import basename

log = logging.getLogger()

class PrimaEngine:

    def __init__(self, url):
        self.url = url
        self.page = urlopen(url).read().decode('utf-8')
        self.q = []
        
        if "http://flash.stream.cz/swf/streamPlayer_558.swf" in self.page:
            self.protocol = "cdn"
            self.q = [('low', 'Nízká')]

        else:
            self.protocol = "rtmp"
            self.parms = json.loads(re.findall(r'var embed_here.+ = (\{.+\});', self.page)[0])
            
            if ( self.parms['hd_id'] ):
                self.q.append( ('hd', 'HD') )
            
            if ( self.parms['hq_id'] ):
                self.q.append( ('high', 'Vysoká') )
                
            if ( self.parms['lq_id'] ):
                self.q.append( ('low', 'Nízká') )

            

    def movies(self):        
        return [ ('0', re.findall(r'<meta property="og:title" content="(.+?)" />', self.page)[0]) ]
  
    def qualities(self):     
        return self.q

    def download(self, quality, movie):
        if self.protocol == "rtmp":
            if quality and quality not in [ i[0] for i in self.q ]:
                raise ValueError('Není k dispozici zadaná kvalita videa.')
            
            if not quality:
                quality = self.q[0][0]
                log.info('Automaticky vybraná kvalita: {}'.format(quality))
                
            return self.download_rtmp(quality)
        
        elif self.protocol == "cdn":
            if quality and quality != 'low':
                raise ValueError('Není k dispozici zadaná kvalita videa.')
            
            if not quality:
                log.info('Automaticky vybraná kvalita: low')
            return self.download_cdn()
            
    def download_rtmp(self, quality):
               
        zoneGEO = self.parms['zoneGEO']
        
        playpath = ""
        if quality == "hd":
            playpath = self.parms['hd_id']
        
        elif quality == "high":
            playpath = self.parms['hq_id']
            
        else:
            playpath = self.parms['lq_id']
            
            
        playerUrl = 'http://embed.livebox.cz/iprimaplay/player-embed-v2.js?__tok{}__={}'.format(
                         math.floor(random.random()*1073741824),
                         math.floor(random.random()*1073741824))
        
        req = Request(playerUrl, None, {'Referer' : self.url} )
        player = urlopen(req).read().decode('utf-8')
        
        baseUrl = ''.join( re.findall( r"embed\['stream'\] = '(.+?)'.+'(\?auth=)'.+'(.+?)';", player)[1] )

        if zoneGEO != 0:
            baseUrl = baseUrl.replace("token", "token_"+str(zoneGEO))

        return ("rtmp", playpath[:-3]+'flv' , { 'url' : baseUrl+'/'+playpath,
                                     'rtmpdump_args' : '--live'})
    
    def download_cdn(self):
        cdnId = re.findall(r"cdnID=(\d+)", self.page)[0]
        #přesměrování
        url = urlopen("http://cdn-dispatcher.stream.cz/?id="+cdnId).geturl()
        filename =  basename(url).split('?')[0]
        
        return ('http', filename, { 'url' : url } )
