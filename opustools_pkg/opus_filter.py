import os
import argparse
import gzip
import math
import difflib
import string
import subprocess
import math

from opustools_pkg import OpusRead

import varikn
from bs4 import BeautifulSoup as bs
#import pycld2
#from mosestokenizer import MosesTokenizer
#import eflomal
from langid.langid import LanguageIdentifier, model

identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)

class OpusGetSents(OpusRead):

    def __init__(self, arguments):
        super().__init__(arguments)
        self.sents = []

    def sendPairOutput(self, wpair):
        self.sents.append(wpair)

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
fromto = sorted([args.s, args.t])

try:
    os.mkdir('filter_files')
except FileExistsError:
    pass

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
    #try:
    #    clddetails = pycld2.detect(sentence)
    #except Exception as e:
    #    clddetails = (0, 0, ((0, 'un', 0.0), 0))
    try:
        lidetails = identifier.classify(sentence)
    except Exception as e:
        lidetails = ('un', 0.0)

    #cldlan = clddetails[2][0][1]
    #cldconf = str(round(clddetails[2][0][2]/100, 2))
    lilan, liconf = [str(round(x,2)) if type(x) == float
            else x for x in lidetails]

    #if cldlan != lan:
    #    cldconf = 0.0
    if lilan != lan:
        liconf = 0.0

    #return lilan, liconf, cldlan, cldconf
    return lilan, liconf

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

get_sents = OpusGetSents('-d {0} -s {1} -t {2} -r {3} -p {4} -wm moses '
    '-w filter_files/temp filter_files/temp -ln'.format(
        args.d, args.s, args.t, args.r, args.p).split())

get_sents.printPairs()

source_file = open('filter_files/sents.{}'.format(fromto[0]), 'w')
target_file = open('filter_files/sents.{}'.format(fromto[1]), 'w')
score_file = open('filter_files/scores.{0}-{1}'.format(fromto[0], fromto[1])
                 , 'w')
clean_file = open('filter_files/clean.{0}-{1}'.format(fromto[0], fromto[1])
                 , 'w')

#s_tokenizer = MosesTokenizer(fromtto[0])
#t_tokenizer = MosesTokenizer(fromtto[1])

for s in get_sents.sents:
    ssent, tsent = s[0][:-1], s[1][:-1]
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
        slang[1], tlang[1], schars, tchars,
        terPun, noZeNu))

source_file.close()
target_file.close()
score_file.close()
clean_file.close()

eflomal_path = '/homeappl/home/miaulamo/appl_taito/eflomal/'
subprocess.run('{0}align.py -i filter_files/clean.{1}-{2} -f '
        'filter_files/{1}-{2}.fwd -r filter_files/{1}-{2}.rev '
        '--model 3'.format(
            eflomal_path, fromto[0], fromto[1]).split())
subprocess.run('{0}makepriors.py -i filter_files/clean.{1}-{2} -f ' 
        'filter_files/{1}-{2}.fwd -r filter_files/{1}-{2}.rev --priors '
        'filter_files/{1}-{2}.priors'.format(
            eflomal_path, fromto[0], fromto[1]).split())
subprocess.run('{0}align.py -s filter_files/sents.{1} -t '
        'filter_files/sents.{2} -F filter_files/{1}-{2}_score.fwd -R '
        'filter_files/{1}-{2}_score.rev --model 3 -M 3 --priors '
        'filter_files/{1}-{2}.priors'.format(
            eflomal_path, fromto[0], fromto[1]).split())

subprocess.run('subword-nmt learn-bpe -s 37000 < filter_files/sents.{0} > '
    'filter_files/{0}.bpe'.format(fromto[0]), shell=True)
subprocess.run('subword-nmt apply-bpe -c filter_files/{0}.bpe < filter_files/sents.{0} > '
    'filter_files/sents.bpe.{0}'.format(fromto[0]), shell=True)

subprocess.run('subword-nmt learn-bpe -s 37000 < filter_files/sents.{0} > '
    'filter_files/{0}.bpe'.format(fromto[1]), shell=True)
subprocess.run('subword-nmt apply-bpe -c filter_files/{0}.bpe < filter_files/sents.{0} > '
    'filter_files/sents.bpe.{0}'.format(fromto[1]), shell=True)

def segment(lang):
    with open('filter_files/sents.bpe.{}'.format(lang)) as infile:
        with open('filter_files/sents.seg.{}'.format(lang), 'w') as outfile:
            for line in infile:
                newli = ['<s>', '<w>']
                for w in line.split():
                    newli.append(w)
                    if w[-2:] != '@@':
                        newli.append('<w>')
                newli.extend(['</s>', '\n'])
                outfile.write(' '.join(newli))

def train_lm(lang):
    vg = varikn.VarigramTrainer(False)
    vg.set_datacost_scale2(0.002)
    vg.set_max_order(20)
    vg.initialize('filter_files/sents.seg.{}'.format(lang),
        0, 0, -1, '', '<s>', False, '')
    vg.grow(1)
    vg.write_file('filter_files/lm.{}'.format(lang), False)

def calculate_xent(lang):
    lm = varikn.Perplexity(
        'filter_files/lm.{}'.format(lang), 1, '', '', '', '<UNK>', 0, True)    
    with open('filter_files/sents.bpe.{}'.format(lang)) as infile:
        with open('filter_files/xent.{}'.format(lang), 'w') as xentfile:
            for line in infile:
                lpsum = 0.0
                tokens = line.strip().split()
                for token in tokens:
                    lpsum += lm.word_logprob(token)
                xent = -lpsum / lm.processed_words() / math.log10(2)
                lm.clear_history()
                lm.init_variables()
                xentfile.write('{}\n'.format(str(xent)))

segment(fromto[0])
segment(fromto[1])

train_lm(fromto[0])
train_lm(fromto[1])

calculate_xent(fromto[0])
calculate_xent(fromto[1])

subprocess.run('clean-corpus-n.perl filter_files/sents {0} {1} '
    'filter_files/clean 1 50'.format(
        fromto[0], fromto[1]).split())

with open('filter_files/sents.{}'.format(fromto[0]), 'r') as pairs_file:
    with open('filter_files/clean.{}'.format(fromto[0]), 'r') as clean_file:
        with open('filter_files/clean_score.{0}-{1}'.format(
                fromto[0], fromto[1]), 'w') as output_file:
            for cline in clean_file:
                while True:
                    pline = pairs_file.readline()
                    if pline == cline:
                        output_file.write('1\n')
                        break
                    else:
                        output_file.write('0\n')

print('\n\nFilter scores are in "filter_files" directory in the following '
    'files:\n\n'
    'scores.{0}-{1}:\n'
    '\tlangid_src\n'
    '\tlangid_trg\n'
    '\tcharacter_score_src\n'
    '\tcharacter_score_trg\n'
    '\tterminal_punctiation\n'
    '\tnon_zero_numerals\n\n'
    '{0}-{1}_score.fwd, '
    '{0}-{1}_score.rev:\n'
    '\tWord alignment\n\n'
    'xent.{0}, '
    'xent.{1}:\n'
    '\tCross entropies\n\n'
    'clean_score.{0}-{1}:\n'
    '\tclean-corpus-n.perl\n'.format(fromto[0], fromto[1]))

