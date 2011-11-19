#!/usr/bin/env python3
#
__author__ = "Jakub Lužný"
__desc__ = "Dummy"
__url__ = r"http://www\.dummy\.net/.*"

import re
from urllib.request import urlopen

class DummyEngine:

    def __init__(self, url):
        self.page = urlopen(url).read().decode('utf-8')
        
    def qualities(self):
        return [ ('high', 'Vysoká'), ('low', 'Nízká') ]
        
    def movies(self):
        return [ ('0', 'Jedno video'), ('1', 'Druhý video') ]

    def download(self, quality, movie):
        return ('rtmp', 'output.flv', {'url' : 'rtmp://server.net:port/appname/playpath',
                                       'playpath' : 'opravdu/divnej/playpath',
                                       'app' : 'opravdu/divná/aplikace',
                                       'rtmpdump_args' : '--live',
                                       'token' : 'bezpečnostní_kód'} )
        
        return ('http', 'output.flv', {'url' : 'http://televize.tv/archiv/porad.flv' } )
        return ('error', 'Slunci došel vodík')
