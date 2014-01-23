#!/usr/bin/env python3
#
# částečně inspirováno ctsream od petr_p

__author__ = "Jakub Lužný"
__desc__ = "ČT (iVysílání)"
__url__ = r"https?://www\.ceskatelevize\.cz/(porady|ivysilani)/.+"

import re,os.path, urllib.request, urllib.parse, json, http.cookiejar, logging
import xml.etree.ElementTree as ElementTree
from urllib.parse import urlparse, unquote

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
    
def srt_time(time):
    time = int(time)
    sec = time / 1000
    msec = time % 1000
    hour = sec / 3600
    sec = sec % 3600
    min = sec / 60
    sec = sec % 60
    return "{:02}:{:02}:{:02},{:03}".format(int(hour), int(min), int(sec), msec)
    
def txt_to_srt(txt):
    subs = re.findall('\s*(\d+); (\d+) (\d+)\n(.+?)\n\n', txt, re.DOTALL)
    srt = ''
    for s in subs:
        srt += "{}\n{} --> {}\n{}\n\n".format(s[0], srt_time(s[1]), srt_time(s[2]), s[3] )
    
    return srt

class CtEngine:

    def __init__(self, url):
        url = url.replace('/porady/', '/ivysilani/').replace('/video/', '')
        self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))
        self.opener.addheaders = [('User-agent', 'Mozilla/5.0'),
        ('x-addr', '127.0.0.1') ]
        urllib.request.install_opener(self.opener)
        
        self.b_page = urlopen(url).read()  # .decode('utf-8')

        data = re.findall(b"callSOAP\((.+?)\);", self.b_page)[0]
        data = data.decode('utf-8')
        data = json.loads(data)
        data = flatten(data['options'], 'options')
        data = urllib.parse.urlencode( data, 'utf-8')
        req = urllib.request.Request('http://www.ceskatelevize.cz/ajax/videoURL.php', bytes(data, 'utf-8') )

        pl_url = unquote( urlopen(req).read().decode('utf-8') )
        
        self.playlist = urlopen(pl_url).read().decode('utf-8')
        self.getMovie()
        self.videos = self.movie.findall('video')
        
        # setridime podle kvality: z popisku nechame jenom cislo
        # kvuli audio-description verzi (label AD) pridame 0, abychom to mohli tridit jako cisla
        self.videos = sorted(self.videos, key=lambda k: int(re.sub(r"\D", "", k.get('label')+"0")), reverse=True)
        
        if len(self.videos) == 0:
            raise ValueError('Není k dispozici žádná kvalita videa.')
        
    def getMovie(self):
        xml = ElementTree.fromstring(self.playlist) 

        for e in xml.findall('smilRoot/body/switchItem'):
            if not 'AD'  in e.get('id'):
                self.movie = e
                break
        
        self.subtitles = None
        for e in xml.findall('metaDataRoot/Playlist/PlaylistItem'):
            if e.get('id') == self.movie.get('id'):
                s = e.find('SubtitlesURL')
                if s is not None:
                    self.subtitles = s.text

    def qualities(self):
        return [( v.get('label'), v.get('label') ) for v in self.videos] + ([('srt', 'Titulky')] if self.subtitles is not None else [] )
      
    def movies(self):        
        return [ ('0', re.findall(b'<title>(.+?) &mdash;', self.b_page)[0].decode('utf-8')) ]

    def get_video(self, quality):
        for video in self.videos:
            if video.get('label') == quality:
                log.info('Vybraná kvalita: {}'.format(quality))
                return video
                
        raise ValueError('Není k dispozici zadaná kvalita videa.')
                
    def download(self, quality, movie):
        if quality == 'srt':
            return self.download_srt()
        if quality:
            video = self.get_video(quality)
        else:
            video = self.videos[0]
            log.info('Automaticky vybraná kvalita: {}'.format(video.get('label')) )

        base = self.movie.get('base')
        src = video.get('src')
        filename = os.path.basename( src)[:-3] + 'flv'
        parsedurl = urlparse(base)
        app = parsedurl.path[1:] + '?' + parsedurl.query

        # rtmpdump --live kvůli restartům - viz http://www.abclinuxu.cz/blog/pb/2011/5/televize-9-ctstream-3#18
        return ('rtmp', filename, { 'url': base, 'playpath': src, 'app' : app, 'rtmpdump_args' : '--live'} )
        
    def download_srt(self):
        if self.subtitles is None:
            raise ValueError('Titulky nejsou k dispozici.')
        
        txt = urllib.request.urlopen(self.subtitles).read().decode('utf8')
        srt = txt_to_srt(txt)
        return ('text', 'subtitles.srt', srt.encode('cp1250') )
        
