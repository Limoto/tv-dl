#!/usr/bin/env python3
#
__author__ = "Jakub Lužný"
__desc__ = "Show Jana Krause"
__url__ = r"http://www\.iprima\.cz/showjanakrause/videoarchiv.*"

import re
from urllib.request import urlopen,Request

class KrausEngine:

    def __init__(self, url):
        self.url = url
        self.page = urlopen(url).read().decode('utf-8')
        self.parse()
        
    def qualities(self):
        return [ ("high", "Vysoká"), ("low", "Nízká") ]
        
    def movies(self):
        list = []
        for i in range(0, len(self.movielist) ):
            list.append( (str(i), self.movielist[i][0] ) )
            
        return list

    def parse(self):
        matches = re.findall(r'''<tr><td><strong>(.*?)</strong></td> <td\>\&nbsp\;\<\/td\>\ \<td\>\&nbsp\;\<\/td\>\<\/tr\>\ \<tr\>\<td\>(.*?)\<\/td\>\ \<td\>\&nbsp\;\<\/td\>\ \<td\>Co\ jste\ v\ televizi\ nevid\ěli\:\<strong\>\ Vyst\ři\žen\é\ sc\ény\ z\ nat\á\čen\í\<\/strong\>\ aktu\áln\ího\ d\ílu\ se\ zaj\ímav\ými\ okam\žiky\,\ kter\é\ jinde\ neuvid\íte\ \.\.\<br\ \/\>\<\/td\>\<\/tr\>\ \<tr\>\<td\>\<p\ id\=\"embed\_here\_\d+\"\ style\=\"border\:\ 1px\ dashed\ red\;\ padding\:\ 1em\"\>Pokud\ se\ V\ám\ zobrazila\ tato\ informace\,\ m\áte\ s\ nejv\ět\š\í\ pravd\ěpodobnost\í\ zak\ázan\ý\ JavaScript\ ve\ Va\šem\ prohl\í\že\či\.\ JavaScript\ tak\é\ nesm\í\ b\ýt\ blokov\án\ n\ějak\ým\ jin\ým\ roz\š\í\řen\ím\ \(nap\ř\.\ NoScript\ apod\.\)\.\ Podrobn\ěj\š\í\ informace\ \<a\ href\=\"\/showjanakrause\/aktuality\/reseni\-problemu\-s\-videoarchivem\"\>nalznete\ zde\<\/a\>\.\<\/p\>\ \<p\>\<script\ src\=\"http\:\/\/embed\.livebox\.cz\/iprima\/player\.js\"\ type\=\"text\/javascript\"\>\<\/script\>\ \<script\ type\=\"text\/javascript\"\>\/\/\ \<\!\[CDATA\[\
LiveboxPlayer\.init\(\'embed\_here\_\d+\'\,\ \'295\'\,\'183\'\,\ \'(.*?)\'\,\ \'(.*?)\'\,\'(.*?)\'\,\'(.*?)\'\)\;\
\/\/\ \]\]\>\<\/\!\[cdata\[\>\<\/script\>\<\/p\>\<\/td\>''', self.page)

        self.movielist = []
        for m in matches:
            mov = m[0], m[2], m[3]
            self.movielist.append(mov)

    def download(self, quality, movie):
        movie = int(movie)
        req = Request('http://embed.livebox.cz/iprima/player.js', headers={'Referer' : self.url})
        js = urlopen(req).read().decode('utf-8')

        rtmp = re.findall("stream: '(.+?)',", js)[0]
        
        filename = self.movielist[movie][2] if quality == 'low' else self.movielist[movie][1]
        
        return ('rtmp', filename, {'url' : rtmp+'/'+filename, 'rtmpdump_args' : '--live'} )
