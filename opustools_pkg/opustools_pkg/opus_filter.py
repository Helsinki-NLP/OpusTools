import argparse
import gzip
import math
import difflib
import string
import subprocess

from opustools_pkg.parse.alignment_parser import AlignmentParser

from bs4 import BeautifulSoup as bs
import pycld2
#from mosestokenizer import MosesTokenizer
#import eflomal
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

root_dir = '/proj/nlpl/data/OPUS/'

alignment = (
    root_dir+args.d+'/'+args.r+'/xml/'+fromto[0]+'-'+fromto[1]+'.xml.gz')
source = (root_dir+args.d+'/'+args.r+'/'+args.p+'/'+fromto[0]+'.zip')
target = (root_dir+args.d+'/'+args.r+'/'+args.p+'/'+fromto[1]+'.zip')

def largeRatio(len1, len2):
    lens = sorted([len1, len2])
    return lens[1]/lens[0] > 3

def longSentence(length):
    return length > 100

def longWord(sent):
    for w in sent.split():
        if len(w) > 40:
            return True
    return False

def detectHtml(sent):
    return bool(bs(sent, 'html.parser').find())

def charactersOutside(line, script):
    for c in line:
        if c not in string.whitespace and c not in string.punctuation:
            try:
                c.encode(script)
            except UnicodeEncodeError:
                return True
    return False

def cleanPair(sent1, sent2, script1, script2):
    len1, len2 = len(sent1.split()), len(sent2.split())
    return (not largeRatio(len1, len2) and
        not longSentence(len1) and not longSentence(len2) and
        not longWord(sent1) and not longWord(sent2) and
        not detectHtml(sent1) and not detectHtml(sent2) and
        not charactersOutside(sent1, script1) and
        not charactersOutside(sent1, script2))


def detectLanguage(sentence, lan):
    try:
        clddetails = pycld2.detect(sentence)
    except Exception as e:
        clddetails = (0, 0, ((0, 'un', 0.0), 0))
    try:
        lidetails = identifier.classify(sentence)
    except Exception as e:
        lidetails = ('un', 0.0)

    cldlan = clddetails[2][0][1]
    cldconf = str(round(clddetails[2][0][2]/100, 2))
    lilan, liconf = [str(round(x,2)) if type(x) == float
            else x for x in lidetails]

    if cldlan != lan:
        cldconf = 0.0
    if lilan != lan:
        liconf = 0.0

    return cldlan, cldconf, lilan, liconf

def getTPunct(line):
    pun = len([c for c in line if c in ['.', '?', '!']])
    return pun

def terminalPunctuation(sline, tline):
    spun = getTPunct(sline)
    tpun = getTPunct(tline)
    score = abs(spun-tpun)
    if spun > 1:
        score += spun - 1
    if tpun > 1:
        score += tpun - 1
    score = -math.log(score + 1)
    return score

def getNZN(line):
    nums = [int(c) for c in line if c in string.digits and c != '0']
    return nums

def nonZeroNumerals(sline, tline):
    snums = getNZN(sline)
    tnums = getNZN(tline)

    seq = difflib.SequenceMatcher(None, snums, tnums)

    return seq.ratio()

def characterScore(line, script):
    total = 0
    invalid = 0
    for c in line:
        if c not in string.whitespace and c not in string.punctuation:
            total += 1
            try:
                c.encode(script)
            except UnicodeEncodeError:
                invalid += 1 
    if total == 0:
        return 1.0
    proper = total-invalid
    return proper/total

alignment_parser = AlignmentParser(
    source, target, args, '', '', '', fromto, False)

source_file = open('sents.{}'.format(fromto[0]), 'w')
target_file = open('sents.{}'.format(fromto[1]), 'w')
score_file = open('scores.{0}-{1}'.format(fromto[0], fromto[1]), 'w')
clean_file = open('clean.{0}-{1}'.format(fromto[0], fromto[1]), 'w')

#s_tokenizer = MosesTokenizer(fromtto[0])
#t_tokenizer = MosesTokenizer(fromtto[1])

with gzip.open(alignment) as gzipAlign:
    for line in gzipAlign:
        alignment_parser.parseLine(line)
        pair = alignment_parser.readPair()
        if pair != -1:
            ssent = pair[0]
            tsent = pair[1]
            if cleanPair(ssent, tsent, 'latin-1', 'latin-1'):
                clean_file.write('{0} ||| {1}\n'.format(ssent, tsent))
            source_file.write(ssent+'\n')
            target_file.write(tsent+'\n')
            slang = detectLanguage(ssent, fromto[0])
            tlang = detectLanguage(tsent, fromto[1])
            schars = characterScore(ssent, 'latin-1')
            tchars = characterScore(tsent, 'latin-1')
            terPun = terminalPunctuation(ssent, tsent)
            noZeNu = nonZeroNumerals(ssent, tsent)
            score_file.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\n'.format(
                slang[3], tlang[3], schars, tchars,
                terPun, noZeNu))

source_file.close()
target_file.close()
score_file.close()
clean_file.close()

eflomal_path = '/homeappl/home/miaulamo/appl_taito/eflomal/'
subprocess.run('{0}align.py -i clean.{1}-{2} -f {1}-{2}.fwd -r '
    '{1}-{2}.rev --model 3'.format(
        eflomal_path, fromto[0], fromto[1]).split())
subprocess.run('{0}makepriors.py -i clean.{1}-{2} -f {1}-{2}.fwd -r '
    '{1}-{2}.rev --priors {1}-{2}.priors'.format(
        eflomal_path, fromto[0], fromto[1]).split())
subprocess.run('{0}align.py -s sents.{1} -t sents.{2} -F {1}-{2}_score.fwd -R '
    '{1}-{2}_score.rev --model 3 -M 3 --priors {1}-{2}.priors'.format(
        eflomal_path, fromto[0], fromto[1]).split())

subprocess.run('subword-nmt learn-bpe -s 37000 < sents.{0} > '
    '{0}.bpe'.format(fromto[0]), shell=True)
subprocess.run('subword-nmt apply-bpe -c {0}.bpe < sents.{0} > '
    'sents.seg.{0}'.format(fromto[0]), shell=True)

subprocess.run('subword-nmt learn-bpe -s 37000 < sents.{0} > '
    '{0}.bpe'.format(fromto[1]), shell=True)
subprocess.run('subword-nmt apply-bpe -c {0}.bpe < sents.{0} > '
    'sents.seg.{0}'.format(fromto[1]), shell=True)
