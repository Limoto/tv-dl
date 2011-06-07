#!/usr/bin/env python
#
# založeno na původním nova-dl
__author__ = "Jakub Lužný"
__desc__ = "Nova (VOYO)"
__url__ = r"http://voyo\.nova\.cz/.+"

import re,os.path
from xml.dom.minidom import parseString as xml_parseString
from urllib.request import urlopen

class NovaEngine:

    def __init__(self, url):
        self.page = str( urlopen(url).read() )

    def qualities(self):
        return [ ("high", "Vysoká"), ("low", "Nízká") ]

    def get_lists(self):

        self.media_id = re.search(r'var media_id = "(\d+)";', self.page ).group(1)
        self.site_id = re.search(r'var site_id = (\d+);', self.page ).group(1)

        serverlist = urlopen("http://tn.nova.cz/bin/player/config.php?media_id=%s&site_id=%s" %(self.media_id, self.site_id) ).read()
        playlist = urlopen("http://tn.nova.cz/bin/player/serve.php?media_id=%s&site_id=%s" %(self.media_id, self.site_id) ).read()

        self.serverlist = xml_parseString(serverlist)
        self.playlist = xml_parseString(playlist)

    def get_server(self, id):
        for server in self.serverlist.getElementsByTagName('flvserver'):
            if server.getAttribute('id') == id:
                return ( server.getAttribute('url'), server.getAttribute('type') )

        #server nenalezen, použije se primární
        for server in self.serverlist.getElementsByTagName('flvserver'):
            if server.getAttribute('primary') == "true":
                return ( server.getAttribute('url'), server.getAttribute('type') )

    def download(self, quality):
        self.get_lists()
        if self.playlist.documentElement.tagName == "error":
            return ( "error", self.playlist.getElementsByTagName('message')[0].lastChild.wholeText.strip() )

        stream = self.playlist.getElementsByTagName('item')[0].getAttribute('src')
        server_id = self.playlist.getElementsByTagName('item')[0].getAttribute('server')

        url, type = self.get_server(server_id)

        # RTMP
        if type == 'stream':
            if quality == 'low':
                url += '?slist=' + stream
            else:
                url += '?slist=' + 'mp4:' + stream

            filename = os.path.basename(stream) + '.flv'

            return ("rtmp", filename, { 'url' : url} )

        # HTTP
        elif type == 'progressive':
            return ( "error", "HTTP downloady nejsou podporovány")
