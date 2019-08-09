import argparse
import gzip

from opustools_pkg.parse.alignment_parser import AlignmentParser

import pycld2
from langid.langid import LanguageIdentifier, model
identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)

parser = argparse.ArgumentParser(prog='opus_filter',
    description='Filter OPUS bitexts')

parser.add_argument('-d', help='Corpus name', metavar='corpus_name',
    required=True)
parser.add_argument('-s', help='Source language', metavar='langid',
    required=True)
parser.add_argument('-t', help='Target language', metavar='langid',
    required=True)
parser.add_argument('-r', help='Release (default=latest)',
    metavar='version',
    default='latest')
parser.add_argument('-p',
    help='Pre-process-type (raw, xml or parsed, default=xml)',
    default='xml', choices=['raw', 'xml', 'parsed'])

args = parser.parse_args()

args.src_cld2, args.trg_cld2, args.src_langid, args.trg_langid = (None, None,
                                                                None, None)
args.ln = True
args.S, args.T = 'all', 'all'
args.wm = 'moses'
args.pn = False
args.sz, args.tz = None, None
args.f = False
args.pa = False
args.sa, args.ta = '', ''
args.ca = '\t'
args.a = 'any'

fromto = sorted([args.s, args.t])
fromto_copy = [args.s, args.t]
switch_langs = fromto_copy != fromto

root_dir = '/proj/nlpl/data/OPUS/'

alignment = (
    root_dir+args.d+'/'+args.r+'/xml/'+fromto[0]+'-'+fromto[1]+'.xml.gz')
source = (root_dir+args.d+'/'+args.r+'/'+args.p+'/'+fromto[0]+'.zip')
target = (root_dir+args.d+'/'+args.r+'/'+args.p+'/'+fromto[1]+'.zip')

alignment_parser = AlignmentParser(
    source, target, args, '', '', '', fromto, False)

gzipAlign = gzip.open(alignment)

def detectLanguage(sentence, sid, suppress):
    try:
        clddetails = pycld2.detect(sentence)
    except Exception as e:
        if not suppress:
            print('Sentence id <{0}>: {1}'.format(sid, e))
        clddetails = (0, 0, ((0, 'un', 0.0), 0))
    try:
        lidetails = identifier.classify(sentence)
    except Exception as e:
        if not suppress:
            print('Sentence id <{0}>: {1}'.format(sid, e))
        lidetails = ('un', 0.0)

    cldlan = clddetails[2][0][1]
    cldconf = str(round(clddetails[2][0][2]/100, 2))
    lilan, liconf = [str(round(x,2)) if type(x) == float
            else x for x in lidetails]

    return cldlan, cldconf, lilan, liconf

for line in gzipAlign:
    alignment_parser.parseLine(line)
    pair = alignment_parser.readPair()
    if pair != -1:
        ssent = pair[0]
        tsent = pair[1]
        slang = detectLanguage(ssent, '', False)
        tlang = detectLanguage(tsent, '', False)
        print(ssent, slang)
        print(tsent, tlang, end='\n\n')


