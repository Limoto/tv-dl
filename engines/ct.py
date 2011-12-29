#!/usr/bin/env python3
#
# částečně inspirováno ctsream od petr_p

__author__ = "Jakub Lužný"
__desc__ = "ČT (iVysílání)"
__url__ = r"http://www\.ceskatelevize\.cz/(porady|ivysilani)/.+"

import re,os.path, urllib.request, urllib.parse, json, http.cookiejar, logging
import xml.etree.ElementTree as ElementTree
from urllib.parse import urlparse

log = logging.getLogger()

urlopen = urllib.request.urlopen

def flatten(obj, prefix = ''):
    out = []
#  print(prefix)
    if type(obj) == dict:
        for key in obj:
            out+= flatten(obj[key], prefix+"[{}]".format(key) )

    elif type(obj) == list:
        for i in range(0, len(obj)):
            out+= flatten(obj[i], prefix+'[{}]'.format(i) )

    else:
        out.append( (prefix, obj) )

    return out

class CtEngine:

    def __init__(self, url):
        url = url.replace('/porady/', '/ivysilani/').replace('/video/', '')
        self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))
        self.opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(self.opener)
        
        self.b_page = urlopen(url).read()  # .decode('utf-8')

        data = re.findall(b"callSOAP\((.+?)\);", self.b_page)[0]
        data = data.decode('utf-8')
        data = json.loads(data)
        data = flatten(data['options'], 'options')
        data = urllib.parse.urlencode( data, 'utf-8')
        req = urllib.request.Request('http://www.ceskatelevize.cz/ajax/playlistURL.php', bytes(data, 'utf-8') )

        pl_url = urlopen(req).read().decode('utf-8')

        self.playlist = urlopen(pl_url).read().decode('utf-8')
        self.getMovie()
        self.videos = self.movie.findall('video')
        if len(self.videos) == 0:
            raise ValueError('Není k dispozici žádná kvalita videa.')

    def getMovie(self):
        xml = ElementTree.fromstring(self.playlist) 

        for e in xml.findall('smilRoot/body/switchItem'):
            if not 'AD'  in e.get('id'):
                self.movie = e
                break

    def qualities(self):
        return [( v.get('label'), v.get('label') ) for v in self.videos]
      
    def movies(self):        
        return [ ('0', re.findall(b'<title>(.+?) &mdash;', self.b_page)[0].decode('utf-8')) ]

    def get_video(self, quality):
        for video in self.videos:
            if video.get('label') == quality:
                log.info('Vybraná kvalita: {}'.format(quality))
                return video
                
        raise ValueError('Není k dispozici zadaná kvalita videa.')
                
    def download(self, quality, movie):
        if quality:
            video = self.get_video(quality)
        else:
            video = self.videos[0]
            log.info('Automaticky vybraná kvalita: {}'.format(video.get('label')) )

        base = self.movie.get('base')
        src = video.get('src')
        filename = os.path.basename( src)[:-3] + 'flv'
        app = urlparse(base).path[1:]

        # rtmpdump --live kvůli restartům - viz http://www.abclinuxu.cz/blog/pb/2011/5/televize-9-ctstream-3#18
        return ('rtmp', filename, { 'url': base, 'playpath': src, 'app' : app, 'rtmpdump_args' : '--live'} )
