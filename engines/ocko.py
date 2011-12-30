#!/usr/bin/env python3
#
__author__ = "halfman"
__desc__ = "Óčko (archiv pořadů)"
__url__ = r"(http://ocko\.stream\.cz/.*|http://www\.stream\.cz/ocko/.*)"

import re
from urllib.request import urlopen
from os.path import basename

class OckoEngine:

    def __init__(self, url):
        self.page = urlopen(url).read().decode('utf-8')

    def qualities(self):
        q = []

        if re.search("cdnHD=(\d+)", self.page):
            q.append(('hd', 'HD'))

        if re.search("cdnHQ=(\d+)", self.page):
            q.append(('high', 'Vysoká'))

        q.append(('low', 'Nízká'))

        return q

    def movies(self):
        return [ ('0', re.findall(r'<title>(.+?) - Autor: OckoTV,', self.page)[0])]

    def download(self, quality, movie):
        if not quality:
            quality = self.qualities()[0][0]

        if quality == "low":
            cdnId = re.findall(r'cdnLQ=(\d+)', self.page)[0]
        elif quality == "high":
            cdnId = re.findall(r'cdnHQ=(\d+)', self.page)[0]
        elif quality == "hd":
            cdnId = re.findall(r'cdnHD=(\d+)', self.page)[0]

        url = urlopen("http://cdn-dispatcher.stream.cz/?id="+cdnId).geturl()
        filename =  basename(url).split('?')[0]

        return ('http', filename, { 'url' : url } )
