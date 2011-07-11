#!/usr/bin/env python3
#
# částečně inspirováno ctsream od petr_p

__author__ = "Jakub Lužný"
__desc__ = "ČT (iVysílání)"
__url__ = r"http://www\.ceskatelevize\.cz/(porady|ivysilani)/.+"

import re,os.path, urllib.request, urllib.parse, json, http.cookiejar
from xml.dom.minidom import parseString as xml_parseString
from urllib.parse import urlparse

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
        url = url.replace('/porady/', '/ivysilani/')
        self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))
        self.opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(self.opener)
        self.page = urlopen(url).read().decode('utf-8')

        data = re.findall(r"callSOAP\((.+?)\);", self.page)[0]
        data = json.loads(data)
        data = flatten(data['options'], 'options')
        data = urllib.parse.urlencode( data, 'utf-8')
        req = urllib.request.Request('http://www.ceskatelevize.cz/ajax/playlistURL.php', bytes(data, 'utf-8') )
#    req.add_header('Referer', url)


        pl_url = urlopen(req).read().decode('utf-8')
#    print(pl_url)

        self.playlist = urlopen(pl_url).read().decode('utf-8')
#    print(self.playlist)
        self.getMovie()
#    print(self.movie.getAttribute('id'))

    def getMovie(self):
        xml = xml = xml_parseString(self.playlist)

        for e in xml.getElementsByTagName('switchItem'):
            if not 'AD'  in e.getAttribute('id'):
                self.movie = e
                break

    def qualities(self):
        qualities = []

        for video in self.movie.getElementsByTagName('video'):
            q = video.getAttribute('label')
            qualities.append( (q,q) )

        return qualities
        
    def movies(self):        
        return [ ('0', re.findall(r'<title>(.+?) &mdash;', self.page)[0]) ]

    def get_video(self, quality):
        videos = self.movie.getElementsByTagName('video')
        for video in videos:
            if video.getAttribute('label') == quality:
                return video

        return videos[0]
    def download(self, quality, movie):
        video = self.get_video(quality)
#    print(video.getAttribute('label'))

        base = self.movie.getAttribute('base')
        src = video.getAttribute('src')
        filename = os.path.basename( src)
        app = urlparse(base).path[1:]

        # rtmpdump --live kvůli restartům - viz http://www.abclinuxu.cz/blog/pb/2011/5/televize-9-ctstream-3#18
        return ('rtmp', filename, { 'url': base, 'playpath': src, 'app' : app, 'rtmpdump_args' : '--live'} )
