#!/usr/bin/env python3

import argparse,os,sys,re

DATADIR = os.path.dirname( os.path.realpath( os.path.abspath(__file__) ) )

sys.path.append(DATADIR)

parser = argparse.ArgumentParser(description='Stahuje televizní pořady.')
parser.add_argument('URL', action="store")
parser.add_argument('-g', '--get-url', action="store_true", help="pouze vypíše URL a skončí")
parser.add_argument('-q', '--quality', action="store", help="nastavuje kvalitu (list pro vypsání možností)")
parser.add_argument('-o', '--output', action="store", help="nastavuje výstupní soubor")


args = parser.parse_args()
engines = []
def import_engines():
    files = os.listdir(DATADIR + '/engines')
    for file in files:
        if file[-3:] == '.py' and file[0] != '_':
            m = __import__("engines.{}".format(file[:-3]) )
            e = getattr(m, file[:-3])
            engines.append( (e.__desc__, e.__url__, getattr(e, file[:-3].capitalize()+'Engine' ) ) )

def get_engine(url):
    for e in engines:
        if re.match(e[1], url):
            return e

def main():
    import_engines()
    e = get_engine(args.URL)[2](args.URL)

    if args.quality == "list":
        for q in e.qualities():
            print(q[0]+'\t'+q[1])
        return

    d = e.download(args.quality)

    if args.get_url:
        url = d[2]['url']

        if 'playpath' in d[2]:
            url += ' playpath={}'.format(d[2]['playpath'])
        
        if 'app' in d[2]:
            url += ' app={}'.format(d[2]['app'])

        print(url)
        return
    
    outf = args.output if args.output else d[1]
    download(d, outf)

def download(d, outf):
    if d[0] == 'rtmp':
        args = ''
        parms = d[2]
        if 'playpath' in parms:
            args += ' -y "{}"'.format(parms['playpath'])
            
        if 'app' in parms:
            args += ' -a "{}"'.format(parms['app'])

        if 'rtmpdump_args' in parms:
            args += ' '+parms['rtmpdump_args']

        os.system('rtmpdump -r "{}" -o "{}" {}'.format(parms['url'], outf, args) )


main()
