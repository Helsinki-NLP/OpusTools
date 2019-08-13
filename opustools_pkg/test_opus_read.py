import os
import unittest
from unittest import mock
import io
import sys
import xml.parsers.expat
import gzip
import shutil
import zipfile

from opustools_pkg import OpusRead, OpusCat, OpusGet

def pairPrinterToVariable(arguments):
    old_stdout = sys.stdout
    printout = io.StringIO()
    sys.stdout = printout
    oprinter = OpusRead(arguments)
    oprinter.printPairs()
    oprinter.par.closeFiles()
    sys.stdout = old_stdout
    return printout.getvalue()

class TestOpusRead(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        os.mkdir('test_files')

        os.mkdir('RF')
        os.mkdir('RF/xml')
        os.mkdir('RF/xml/en')
        with open('RF/xml/en/1996.xml', 'w') as f:
            f.write('<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<text>'
            '<head>\n<meta id="1"> \n <w id="w1.1">The</w> \n <w id="'
            'w1.2">Hound</w> \n <w id="w1.3">of</w> \n <w id="w1.4">the'
            '</w> \n <w id="w1.5">Baskervilles</w>   \n <w id="w1.6">by'
            '</w> \n <w id="w1.7">Sir</w> \n <w id="w1.8">Arthur</w> \n '
            '<w id="w1.9">Conan</w> \n <w id="w1.10">Doyle</w>   \n <w '
            'id="w1.11">Aligned</w> \n <w id="w1.12">by</w>\n <w id="w1.'
            '13">:</w> \n <w id="w1.14">András</w> \n <w id="w1.15">'
            'Farkas</w> \n <w id="w1.16">(</w>\n <w id="w1.17">fully</w> '
            '\n <w id="w1.18">reviewed</w>\n <w id="w1.19">)</w> \n</'
            'meta></head><body>\n<s cld2="en" cld2conf="0.97" id="s1" '
            'langid="en" langidconf="0.99">\n <chunk id="c1-1" type="NP'
            '">\n  <w hun="NN" id="w1.1" lem="source" pos="NN" tree="NN'
            '">Source</w>\n </chunk>\n <w hun=":" id="w1.2" lem=":" pos'
            '=":" tree=":">:</w>\n <chunk id="c1-3" type="NP">\n  <w '
            'hun="NNP" id="w1.3" pos="NNP" tree="NN">manybooks.'
            'netAudiobook</w>\n  <w hun="JJ" id="w1.4" lem="available" '
            'pos="NN" tree="JJ">available</w>\n </chunk>\n <chunk id="'
            'c1-4" type="ADVP">\n  <w hun="RB" id="w1.5" lem="here" '
            'pos="RB" tree="RB">here</w>\n </chunk>\n</s>\n\n\n\n<s '
            'cld2="un" cld2conf="0.0" id="s4" langid="en" langidconf'
            '="0.17">\n <chunk id="c4-1" type="NP">\n  <w hun="NNP" '
            'id="w4.1" lem="Chapter" pos="NNP" tree="NP">Chapter</w>\n  '
            '<w hun="CD" id="w4.2" lem="1" pos="CD" tree="CD">1</w>\n  '
            '<w hun="NNP" id="w4.3" lem="Mr." pos="NNP" tree="NP">Mr.</'
            'w>\n  <w hun="NNP" id="w4.4" lem="Sherlock" pos="NNP" tree'
            '="NP">Sherlock</w>\n  <w hun="NNP" id="w4.5" lem="Holmes" '
            'pos="NNP" tree="NP">Holmes</w>\n </chunk>\n</s><p id="p5'
            '">\n<s cld2="en" cld2conf="0.99" id="s5.0" langid="en" '
            'langidconf="1.0">\n <chunk id="c5.0-1" type="NP">\n  <w hun'
            '="NNP" id="w5.0.1" lem="Mr." pos="NNP" tree="NP">Mr.</w>\n  '
            '<w hun="NNP" id="w5.0.2" lem="Sherlock" pos="NNP" tree="NP">'
            'Sherlock</w>\n  <w hun="NNP" id="w5.0.3" lem="Holmes" pos="'
            'NNP" tree="NP">Holmes</w>\n</chunk>\n</s>\n\n\n<s cld2="un" '
            'cld2conf="0.0" id="s8.1" langid="en" langidconf="0.17">\n '
            '<chunk id="c8.1-1" type="NP">\n  <w hun="PRP" id="w8.1.1" '
            'lem="I" pos="PRP" tree="PP">I</w>\n </chunk>\n <chunk id="c8'
            '.1-2" type="VP">\n  <w hun="VBP" id="w8.1.2" lem="believe" '
            'pos="VBP" tree="VVP">believe</w>\n </chunk>\n</s></p>\n\n<p '
            'id="p167">\n<s cld2="un" cld2conf="0.0" id="s167.0" langid="'
            'de" langidconf="0.47">\n <chunk id="c167.0-1" type="NP">\n  '
            '<w hun="JJ" id="w167.0.1" lem="&quot;" pos="NN" tree="``">"</'
            'w>\n  <w hun="NN" id="w167.0.2" lem="excellent" pos="NNP" '
            'tree="JJ">Excellent</w>\n </chunk>\n <w hun="." id="w167.0.'
            '3" lem="!" pos="." tree="SENT">!</w>\n</s>\n \n\n\n</p>\n '
            '</body>\n</text>\n')

        with zipfile.ZipFile('RF_v1_xml_en.zip', 'w') as zf:
            zf.write('RF/xml/en/1996.xml')

        os.mkdir('RF/xml/sv')
        with open('RF/xml/sv/1996.xml', 'w') as f:
            f.write('<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<text'
            '>\n <head>\n  <meta> The Hound of the Baskervilles \n by '
            'Sir Arthur Conan Doyle \n Aligned by: András Farkas (fully '
            'reviewed) \n </meta>\n </head>\n <body>\n<s cld2="en" '
            'cld2conf="0.96" id="s1" langid="de" langidconf="0.66">\n '
            '<w id="w1.1">Source</w>\n <w id="w1.2">:</w> \n <w id="w1.'
            '3">Project</w> \n <w id="w1.4">Gutenberg</w>\n</s>\n\n<s '
            'cld2="ia" cld2conf="0.95" id="s4" langid="et" langidconf'
            '="0.42">\n <w id="w4.1">Herra</w> \n <w id="w4.2">Sherlock'
            '</w> \n <w id="w4.3">Holmes</w>\n <w id="w4.4">.</w>\n</s'
            '><p id="p5">\n<s cld2="fi" cld2conf="0.99" id="s5.0" langid'
            '="fi" langidconf="1.0">\n <w id="w5.0.1">Herra</w> \n <w '
            'id="w5.0.2">Sherlock</w> \n <w id="w5.0.3">Holmes</w>\n</'
            's>\n   \n<s cld2="fi" cld2conf="0.97" id="s8.1" langid="fi" '
            'langidconf="1.0">\n <w id="w8.1.1">Luulenpa</w> \n <w id="'
            'w8.1.2">että</w> \n <w id="w8.1.3">sinulla</w> \n</s></p>\n'
            '<p id="p167">\n<s cld2="un" cld2conf="0.0" id="s167.0" '
            'langid="fi" langidconf="0.38">\n <w id="w167.0.1">"</w>\n '
            '<w id="w167.0.2">Erinomaista</w>\n <w id="w167.0.3">.</w>\n'
            '</s></p>\n </body>\n</text>\n')

        with zipfile.ZipFile('RF_v1_xml_sv.zip', 'w') as zf:
            zf.write('RF/xml/sv/1996.xml')

        shutil.copyfile('RF_v1_xml_en.zip', 'en.zip')
        shutil.copyfile('RF_v1_xml_sv.zip', 'sv.zip')

        with open('books_alignment.xml', 'w') as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE '
            'cesAlign PUBLIC "-//CES//DTD XML cesAlign//EN" "">\n<cesAlign '
            'version="1.0">\n<linkGrp targType="s" fromDoc="en/'
            '1996.xml.gz" '
            'toDoc="sv/1996.xml.gz" '
            '>\n<link xtargets="s1;s1" id="SL1"/>\n<link xtargets="s4;s4" '
            'id="SL4"/>\n<link xtargets="s5.0;s5.0" id="SL5.0"/>\n<link '
            'xtargets="s8.1;s8.1" id="SL8.1"/>\n<link xtargets="s167.0'
            ';s167.0" id="SL167.0"/>\n  </linkGrp>\n</cesAlign>\n')

        self.opr = OpusRead('-d RF -s en -t sv'.split())
        self.opr.par.initializeSentenceParsers(
            {'fromDoc': 'en/1996.xml.gz', 'toDoc': 'sv/1996.xml.gz'})
        self.fastopr = OpusRead('-d RF -s en -t sv -f'.split())
        self.fastopr.par.initializeSentenceParsers(
            {'fromDoc': 'en/1996.xml.gz', 'toDoc': 'sv/1996.xml.gz'})

        self.maxDiff= None
    @classmethod
    def tearDownClass(self):
        self.opr.par.sPar.document.close()
        self.opr.par.tPar.document.close()
        self.opr.par.closeFiles()
        self.fastopr.par.sPar.document.close()
        self.fastopr.par.tPar.document.close()
        self.fastopr.par.closeFiles()
        shutil.rmtree('test_files')
        shutil.rmtree('RF')
        os.remove('books_alignment.xml')
        os.remove('RF_v1_xml_en.zip')
        os.remove('RF_v1_xml_sv.zip')
        os.remove('en.zip')
        os.remove('sv.zip')

    def tearDown(self):
        self.opr.par.args.wm='normal'
        self.opr.par.slim=['all']
        self.opr.par.tlim=['all']
        self.opr.par.args.a = 'any'
        self.opr.par.nonAlignments = self.opr.par.args.ln
        self.opr.par.args.m = 'all'
        self.opr.par.alignParser = xml.parsers.expat.ParserCreate()
        self.opr.par.alignParser.StartElementHandler = \
            self.opr.par.start_element
        self.opr.par.sPar.wmode = 'normal'
        self.opr.par.sPar.pre = 'xml'
        self.opr.par.tPar.wmode = 'normal'
        self.opr.par.tPar.pre = 'xml'
        self.opr.par.sPar.annotations = False
        self.opr.par.tPar.annotations = False
        self.opr.par.args.cm = '\t'
        self.fastopr.par.args.wm='normal'
        self.fastopr.par.slim=['all']
        self.fastopr.par.tlim=['all']
        self.fastopr.par.args.a = 'any'
        self.fastopr.par.nonAlignments = self.fastopr.par.args.ln
        self.fastopr.par.args.m = 'all'
        self.fastopr.par.alignParser = xml.parsers.expat.ParserCreate()
        self.fastopr.par.alignParser.StartElementHandler = \
            self.fastopr.par.start_element
        self.fastopr.par.sPar.wmode = 'normal'
        self.fastopr.par.sPar.pre = 'xml'
        self.fastopr.par.tPar.wmode = 'normal'
        self.fastopr.par.tPar.pre = 'xml'
        self.fastopr.par.sPar.annotations = False
        self.fastopr.par.tPar.annotations = False

    def test_ExhaustiveSentenceParser_initializing(self):
        self.assertEqual(len(self.opr.par.sPar.sentences), 29)
        self.assertEqual(len(self.opr.par.tPar.sentences), 68)

    def test_ExhaustiveSentenceParser_getSentence(self):
        self.assertEqual(self.opr.par.sPar.getSentence('s3.1')[0],
            '( Unofficial translation )')
        self.assertEqual(self.opr.par.tPar.getSentence('s3.1')[0],
            'Fru talman , ärade ledamöter av Sveriges riksdag !')

        self.assertEqual(self.opr.par.sPar.getSentence('s8.1')[0],
            ("The Government 's policy to combat unemployment will re"
            "st on four corner- stones :"))
        self.assertEqual(self.opr.par.tPar.getSentence('s8.1')[0],
            'Goda statsfinanser är grunden för alla politiska ambitioner .')

        self.assertEqual(self.opr.par.sPar.getSentence('s10.1')[0],
            'Sound public finances are the basis for all political a'
            'mbitions .')
        self.assertEqual(self.opr.par.tPar.getSentence('s10.1')[0],
            'Den andra hörnstenen är goda villkor för företag och fö'
            'retagande .')

    def test_ExhaustiveSentenceParser_readSentence_format(self):
        self.assertEqual(self.opr.par.sPar.readSentence(['s3.1'])[0],
            '(src)="s3.1">( Unofficial translation )')
        self.assertEqual(self.opr.par.tPar.readSentence(['s3.1'])[0],
            '(trg)="s3.1">Fru talman , ärade ledamöter av Sveriges riksdag !')
        self.assertEqual(self.opr.par.sPar.readSentence(['s3.1', 's10.1'])[0],
            '(src)="s3.1">( Unofficial translation )\n'
            '(src)="s10.1">Sound public finances are the basis for all'
            ' political ambitions .')

    def test_ExhaustiveSentenceParser_readSentence_moses(self):
        self.opr.par.sPar.wmode = 'moses'
        self.assertEqual(self.opr.par.sPar.readSentence(['s3.1'])[0],
            '( Unofficial translation )')

    def test_ExhaustiveSentenceParser_readSentence_tmx(self):
        self.opr.par.sPar.wmode = 'tmx'
        self.assertEqual(self.opr.par.sPar.readSentence(['s3.1'])[0],
            '\t\t<tu>\n\t\t\t<tuv xml:lang="en"><seg>( Unofficial tr'
            'anslation )</seg></tuv>')
        self.opr.par.tPar.wmode = 'tmx'
        self.assertEqual(self.opr.par.tPar.readSentence(['s5.1', 's5.2'])[0],
            '\t\t\t<tuv xml:lang="sv"><seg>Fundamenten för ett gott '
            'samhälle undergrävs av dagens höga arbetslöshet . Såväl '
            'samhällsekonomi som moral och vilja försvagas .</seg></t'
            'uv>\n\t\t</tu>')

    def test_ExhaustiveSentenceParser_readSentence_empty(self):
        self.assertEqual(self.opr.par.sPar.readSentence([''])[0], '')

    def test_SentenceParser_readSentence_format(self):
        self.assertEqual(self.fastopr.par.sPar.readSentence(['s3.1'])[0],
            '(src)="s3.1">( Unofficial translation )')
        self.assertEqual(self.fastopr.par.tPar.readSentence(['s3.1'])[0],
            '(trg)="s3.1">Fru talman , ärade ledamöter av Sveriges riksdag !')
        self.assertEqual(self.fastopr.par.sPar.readSentence(
            ['s8.1', 's10.1'])[0],
            """(src)="s8.1">The Government 's policy to combat unemp"""
            """loyment will rest on four corner- stones :\n(src)="s10"""
            """.1">Sound public finances are the basis for all politi"""
            """cal ambitions .""")

    def test_SentenceParser_readSentence_moses(self):
        self.fastopr.par.sPar.wmode = 'moses'
        self.assertEqual(self.fastopr.par.sPar.readSentence(['s13.1'])[0],
            'Sweden is a good country for enterprise .')

    def test_SentenceParser_readSentence_tmx(self):
        self.fastopr.par.sPar.wmode = 'tmx'
        self.assertEqual(self.fastopr.par.sPar.readSentence(['s15.1'])[0],
            '\t\t<tu>\n\t\t\t<tuv xml:lang="en"><seg>The local and r'
            'egional role of economic policy will be emphasized .</se'
            'g></tuv>')
        self.fastopr.par.tPar.wmode = 'tmx'
        self.assertEqual(self.fastopr.par.tPar.readSentence(
            ['s11.1', 's11.2'])[0],
            '\t\t\t<tuv xml:lang="sv"><seg>Sverige är ett bra land f'
            'ör företagsamhet . Här finns en flexibel ekonomi , ett k'
            'onstruktivt samarbetsklimat och en kunnig och välutbilda'
            'd arbetskraft .</seg></tuv>\n\t\t</tu>')

    def test_SentenceParser_readSentence_empty(self):
        self.assertEqual(self.fastopr.par.sPar.readSentence([''])[0], '')

    def test_AlignmentParser_readPair_returns_1_if_tag_is_not_link_and_write_mode_is_links(self):
        opr = OpusRead('-d RF -s en -t sv -wm links'.split())
        opr.par.initializeSentenceParsers(
            {'fromDoc': 'en/1996.xml.gz', 'toDoc': 'sv/1996.xml.gz'})
        opr.par.parseLine('<s>')
        ret = opr.par.readPair()
        self.assertEqual(ret, 1)
        opr.par.closeFiles()

    def test_AlignmentParser_readPair_returns_minus_1_if_tag_is_not_link_and_write_mode_id_not_links(self):
        self.opr.par.parseLine('<s>')
        ret = self.opr.par.readPair()
        self.assertEqual(ret, -1)

    def test_AlignmentParser_readPair_returns_minus_1_if_number_of_sentences_is_outside_limit(self):
        self.opr.par.slim = ['0']
        self.opr.par.parseLine('<s>')
        self.opr.par.parseLine('<link xtargets="s1;s1" id="SL1"/>')
        ret = self.opr.par.readPair()
        self.assertEqual(ret, -1)

        self.opr.par.slim = ['1']
        self.opr.par.parseLine('<link xtargets="s1;s1" id="SL1"/>')
        ret = self.opr.par.readPair()
        self.assertEqual(type(ret[0]), str)

        self.opr.par.tlim = ['3', '4']
        self.opr.par.parseLine('<link xtargets="s1;s1 s2" id="SL1"/>')
        ret = self.opr.par.readPair()
        self.assertEqual(ret, -1)

        self.opr.par.parseLine('<link xtargets="s1;s1 s2 s3" id="SL1"/>')
        ret = self.opr.par.readPair()
        self.assertEqual(type(ret[0]), str)

        self.opr.par.parseLine('<link xtargets="s1;s1 s2 s3 s4" id="SL1"/>')
        ret = self.opr.par.readPair()
        self.assertEqual(type(ret[0]), str)

        self.opr.par.parseLine('<link xtargets="s1 s2;s1 s2 s3 s4" id="SL1"/>')
        ret = self.opr.par.readPair()
        self.assertEqual(ret, -1)

        self.opr.par.parseLine('<link xtargets=";s1 s2 s3 s4" id="SL1"/>')
        ret = self.opr.par.readPair()
        self.assertEqual(ret, -1)

        self.opr.par.parseLine('<link xtargets="s1;s1 s2 s3 s4 s5" id="SL1"/>')
        ret = self.opr.par.readPair()
        self.assertEqual(ret, -1)

    def test_AlignmentParser_readPair_returns_minus_1_if_attribute_values_is_not_over_threshold(self):
        self.opr.par.args.a = 'certainty'
        self.opr.par.args.tr = 0.6
        self.opr.par.parseLine('<s>')
        self.opr.par.parseLine(
            '<link xtargets="s1;s1" id="SL1" certainty="0.5"/> ')
        ret = self.opr.par.readPair()
        self.assertEqual(ret, -1)
        self.opr.par.parseLine(
            '<link xtargets="s1;s1" id="SL1" certainty="0.7"/> ')
        ret = self.opr.par.readPair()
        self.assertEqual(type(ret[0]), str)

    def test_AlignmentParser_readPair_returns_minus_1_if_nonAlignments_is_on_and_source_or_target_is_empty(self):
        self.opr.par.parseLine('<s>')
        self.opr.par.parseLine('<link xtargets="s1;" id="SL1"/> ')
        ret = self.opr.par.readPair()
        self.assertEqual(type(ret[0]), str)
        self.opr.par.nonAlignments = True
        self.opr.par.parseLine('<link xtargets="s1;" id="SL1"/> ')
        ret = self.opr.par.readPair()
        self.assertEqual(ret, -1)

    def test_AlignmentParser_readPair_returns_1_if_alignment_is_valid_and_write_mode_is_links(self):
        self.opr.par.args.wm = 'links'
        self.opr.par.parseLine('<s>')
        self.opr.par.parseLine('<link xtargets="s1;s1" id="SL1"/> ')
        ret = self.opr.par.readPair()
        self.assertEqual(ret, 1)

    def test_PairPrinter_printPair_normal(self):
        sPair = ('(src)="s4">Chapter 1 Mr. Sherlock Holmes',
                '(trg)="s4">Herra Sherlock Holmes .')
        self.assertEqual(self.opr.printPair(sPair),
            '(src)="s4">Chapter 1 Mr. Sherlock Holmes\n(trg)="s4">Herra '
            'Sherlock Holmes .\n================================')

    def test_PairPrinter_printPair_tmx(self):
        self.opr.par.args.wm = 'tmx'
        sPair = ('\t\t<tu>\n\t\t\t<tuv xml:lang="en"><seg>Chapter 1 Mr. '
                'Sherlock Holmes</seg></tuv>', '\t\t\t<tuv xml:lang="fi">'
                '<seg>Herra Sherlock Holmes .</seg></tuv>\n\t\t</tu>')
        self.assertEqual(self.opr.printPair(sPair),
            '\t\t<tu>\n\t\t\t<tuv xml:lang="en"><seg>Chapter 1 Mr. Sherlock'
            ' Holmes</seg></tuv>\n\t\t\t<tuv xml:lang="fi"><seg>Herra '
            'Sherlock Holmes .</seg></tuv>\n\t\t</tu>')

    def test_PairPrinter_printPair_moses(self):
        self.opr.par.args.wm = 'moses'
        sPair = ('Chapter 1 Mr. Sherlock Holmes', 'Herra Sherlock Holmes .')
        self.assertEqual(self.opr.printPair(sPair),
            """Chapter 1 Mr. Sherlock Holmes\tHerra Sherlock Holmes .""")

    def test_PairPrinter_printPair_moses_change_delimiter(self):
        self.opr.par.args.wm = 'moses'
        self.opr.args.cm = '@'
        sPair = ('Chapter 1 Mr. Sherlock Holmes', 'Herra Sherlock Holmes .')
        self.assertEqual(self.opr.printPair(sPair),
            """Chapter 1 Mr. Sherlock Holmes@Herra Sherlock Holmes .""")

    def test_PairPrinter_printPair_links(self):
        self.opr.par.args.wm = 'links'
        sPair = '<link xtargets="s4;s4" id="SL4"/>'
        self.assertEqual(self.opr.printPair(sPair),
            '<link xtargets="s4;s4" id="SL4"/>')

    def test_PairPrinter_printPair_empty(self):
        sPair = ('(src)="3">Director PARK Jae-sik', '')
        self.assertEqual(self.opr.printPair(sPair),
            '(src)="3">Director PARK Jae-sik\n\n'
            '================================')

    def test_PairPrinter_writePair_normal(self):
        sPair = ('(src)="s4">Chapter 1 Mr. Sherlock Holmes',
                '(trg)="s4">Herra Sherlock Holmes .')
        self.assertEqual(self.opr.writePair(sPair),
            ('(src)="s4">Chapter 1 Mr. Sherlock Holmes\n(trg)="s4">Herra '
            'Sherlock Holmes .\n================================\n', ''))

    def test_PairPrinter_writePair_tmx(self):
        self.opr.par.args.wm = 'tmx'
        sPair = ('\t\t<tu>\n\t\t\t<tuv xml:lang="en"><seg>Chapter 1 Mr. '
                'Sherlock Holmes</seg></tuv>',
                '\t\t\t<tuv xml:lang="fi"><seg>Herra Sherlock Holmes .'
                '</seg></tuv>\n\t\t</tu>')
        self.assertEqual(self.opr.writePair(sPair),
            ('\t\t<tu>\n\t\t\t<tuv xml:lang="en"><seg>Chapter 1 Mr. Sherlock'
            ' Holmes</seg></tuv>\n\t\t\t<tuv xml:lang="fi"><seg>Herra '
            'Sherlock Holmes .</seg></tuv>\n\t\t</tu>\n', ''))

    def test_PairPrinter_writePair_moses(self):
        self.opr.par.args.wm = 'moses'
        self.opr.par.args.w = 'test_files/test.src'
        sPair = ('Chapter 1 Mr. Sherlock Holmes', 'Herra Sherlock Holmes .')
        self.assertEqual(self.opr.writePair(sPair),
            ('Chapter 1 Mr. Sherlock Holmes\nHerra Sherlock Holmes .\n', ''))

    def test_PairPrinter_writePair_links(self):
        self.opr.par.args.wm = 'links'
        sPair = '<link xtargets="s4;s4" id="SL4"/>'
        self.assertEqual(self.opr.writePair(sPair),
            ('<link xtargets="s4;s4" id="SL4"/>\n', ''))

    def test_PairPrinter_writePair_empty(self):
        sPair = ('(src)="3">Director PARK Jae-sik', '')
        self.assertEqual(self.opr.writePair(sPair),
            ('(src)="3">Director PARK Jae-sik\n\n'
            '================================\n', ''))


    def test_switch_labels_when_languages_are_in_unalphabetical_order(self):
        opr = OpusRead('-d RF -s sv -t en'.split())
        opr.par.initializeSentenceParsers(
            {'fromDoc': 'en/1996.xml.gz', 'toDoc': 'sv/1996.xml.gz'})
        self.assertEqual(opr.par.sPar.readSentence(['s3.1'])[0],
            '(trg)="s3.1">( Unofficial translation )')
        self.assertEqual(opr.par.tPar.readSentence(['s3.1'])[0],
            '(src)="s3.1">Fru talman , ärade ledamöter av Sveriges riksdag !')

        opr.par.closeFiles()
        fastopr = OpusRead('-d RF -s sv -t en -f'.split())
        fastopr.par.initializeSentenceParsers(
            {'fromDoc': 'en/1996.xml.gz', 'toDoc': 'sv/1996.xml.gz'})
        self.assertEqual(fastopr.par.sPar.readSentence(['s3.1'])[0],
            '(trg)="s3.1">( Unofficial translation )')
        self.assertEqual(fastopr.par.tPar.readSentence(['s3.1'])[0],
            '(src)="s3.1">Fru talman , ärade ledamöter av Sveriges riksdag !')
        fastopr.par.closeFiles()

    def test_ExhaustiveSentenceParser_readSentence_annotations(self):
        opr = OpusRead('-d RF -s en -t sv -pa'.split())
        opr.par.initializeSentenceParsers(
            {'fromDoc': 'en/1996.xml.gz', 'toDoc': 'sv/1996.xml.gz'})
        self.assertEqual(opr.par.sPar.readSentence(['s3.1'])[0],
            '(src)="s3.1">(|(|( Unofficial|NNP|unofficial translatio'
            'n|NN|translation )|)|)')
        opr.par.closeFiles()
        opr = OpusRead('-d RF -s en -t sv -pa -ca @'.split())
        opr.par.initializeSentenceParsers(
            {'fromDoc': 'en/1996.xml.gz', 'toDoc': 'sv/1996.xml.gz'})
        self.assertEqual(opr.par.sPar.readSentence(['s3.1'])[0],
            '(src)="s3.1">(@(@( Unofficial@NNP@unofficial translatio'
            'n@NN@translation )@)@)')
        opr.par.closeFiles()

    def test_ExhaustiveSentenceParser_readSentence_raw(self):
        opr = OpusRead('-d RF -s en -t sv -p raw'.split())
        opr.par.initializeSentenceParsers(
            {'fromDoc': 'en/1996.xml.gz', 'toDoc': 'sv/1996.xml.gz'})
        self.assertEqual(opr.par.sPar.readSentence(['s3.1'])[0],
            '(src)="s3.1">(Unofficial translation)')
        opr.par.closeFiles()

    def test_SentenceParser_readSentence_annotations(self):
        opr = OpusRead('-d RF -s en -t sv -pa -f'.split())
        opr.par.initializeSentenceParsers(
            {'fromDoc': 'en/1996.xml.gz', 'toDoc': 'sv/1996.xml.gz'})
        self.assertEqual(opr.par.sPar.readSentence(['s3.1'])[0],
            '(src)="s3.1">(|(|( Unofficial|NNP|unofficial translatio'
            'n|NN|translation )|)|)')
        opr.par.closeFiles()

    def test_SentenceParser_readSentence_annotations_change_delimiter(self):
        opr = OpusRead('-d RF -s en -t sv -pa -f -ca @'.split())
        opr.par.initializeSentenceParsers(
            {'fromDoc': 'en/1996.xml.gz', 'toDoc': 'sv/1996.xml.gz'})
        self.assertEqual(opr.par.sPar.readSentence(['s3.1'])[0],
            '(src)="s3.1">(@(@( Unofficial@NNP@unofficial translatio'
            'n@NN@translation )@)@)')
        opr.par.closeFiles()

    def test_SentenceParser_readSentence_raw(self):
        opr = OpusRead('-d RF -s en -t sv -p raw -f'.split())
        opr.par.initializeSentenceParsers(
            {'fromDoc': 'en/1996.xml.gz', 'toDoc': 'sv/1996.xml.gz'})
        self.assertEqual(opr.par.sPar.readSentence(['s3.1'])[0],
            '(src)="s3.1">(Unofficial translation)')
        opr.par.closeFiles()

    def test_AlignmentParser_readPair_sentence_limits(self):
        opr = OpusRead('-d RF -s en -t sv -T 0'.split())
        opr.par.initializeSentenceParsers(
            {'fromDoc': 'en/1996.xml.gz', 'toDoc': 'sv/1996.xml.gz'})

        opr.par.parseLine('<s>')
        opr.par.parseLine('<link xtargets="s1;s1" id="SL1"/>')
        ret = opr.par.readPair()
        self.assertEqual(ret, -1)

        opr.par.closeFiles()

        opr = OpusRead('-d RF -s en -t sv -T 1'.split())
        opr.par.initializeSentenceParsers(
            {'fromDoc': 'en/1996.xml.gz', 'toDoc': 'sv/1996.xml.gz'})

        opr.par.parseLine('<s>')
        opr.par.parseLine('<link xtargets="s1;s1" id="SL1"/>')
        ret = opr.par.readPair()
        self.assertEqual(type(ret[0]), str)

        opr.par.closeFiles()

        opr = OpusRead('-d RF -s en -t sv -S 3-4 -T 1'.split())
        opr.par.initializeSentenceParsers(
            {'fromDoc': 'en/1996.xml.gz', 'toDoc': 'sv/1996.xml.gz'})

        opr.par.parseLine('<s>')
        opr.par.parseLine('<link xtargets="s1;s1 s2" id="SL1"/>')
        ret = opr.par.readPair()
        self.assertEqual(ret, -1)

        opr.par.parseLine('<link xtargets="s1 s2 s3;s1" id="SL1"/>')
        ret = opr.par.readPair()
        self.assertEqual(type(ret[0]), str)

        opr.par.parseLine('<link xtargets="s1 s2 s3 s4;s1" id="SL1"/>')
        ret = opr.par.readPair()
        self.assertEqual(type(ret[0]), str)

        opr.par.parseLine('<link xtargets="s1 s2 s3 s4;s1 s2" id="SL1"/>')
        ret = opr.par.readPair()
        self.assertEqual(ret, -1)

        opr.par.parseLine('<link xtargets="s1 s2 s3 s4;" id="SL1"/>')
        ret = opr.par.readPair()
        self.assertEqual(ret, -1)

        opr.par.parseLine('<link xtargets="s1 s2 s3 s4 s5;s1" id="SL1"/>')
        ret = opr.par.readPair()
        self.assertEqual(ret, -1)

        opr.par.closeFiles()
        
    def test_AlignmentParser_readPair_sentence_limits_when_languages_in_unalphabetical_order(self):
        opr = OpusRead('-d RF -s sv -t en -T 0'.split())
        opr.par.initializeSentenceParsers(
            {'fromDoc': 'en/1996.xml.gz', 'toDoc': 'sv/1996.xml.gz'})

        opr.par.parseLine('<s>')
        opr.par.parseLine('<link xtargets="s1;s1" id="SL1"/>')
        ret = opr.par.readPair()
        self.assertEqual(ret, -1)

        opr.par.closeFiles()

        opr = OpusRead('-d RF -s sv -t en -T 1'.split())
        opr.par.initializeSentenceParsers(
            {'fromDoc': 'en/1996.xml.gz', 'toDoc': 'sv/1996.xml.gz'})

        opr.par.parseLine('<s>')
        opr.par.parseLine('<link xtargets="s1;s1" id="SL1"/>')
        ret = opr.par.readPair()
        self.assertEqual(type(ret[0]), str)

        opr.par.closeFiles()

        opr = OpusRead('-d RF -s sv -t en -S 3-4 -T 1'.split())
        opr.par.initializeSentenceParsers(
            {'fromDoc': 'en/1996.xml.gz', 'toDoc': 'sv/1996.xml.gz'})

        opr.par.parseLine('<s>')
        opr.par.parseLine('<link xtargets="s1;s1 s2" id="SL1"/>')
        ret = opr.par.readPair()
        self.assertEqual(ret, -1)

        opr.par.parseLine('<link xtargets="s1;s1 s2 s3" id="SL1"/>')
        ret = opr.par.readPair()
        self.assertEqual(type(ret[0]), str)

        opr.par.parseLine('<link xtargets="s1;s1 s2 s3 s4" id="SL1"/>')
        ret = opr.par.readPair()
        self.assertEqual(type(ret[0]), str)

        opr.par.parseLine('<link xtargets="s1 s2;s1 s2 s3 s4" id="SL1"/>')
        ret = opr.par.readPair()
        self.assertEqual(ret, -1)

        opr.par.parseLine('<link xtargets=";s1 s2 s3 s4" id="SL1"/>')
        ret = opr.par.readPair()
        self.assertEqual(ret, -1)

        opr.par.parseLine('<link xtargets="s1;s1 s2 s3 s4 s5" id="SL1"/>')
        ret = opr.par.readPair()
        self.assertEqual(ret, -1)

        opr.par.closeFiles()

    def test_AlignmentParser_previous_document_is_closed_before_next_is_opened(self):
        printer = OpusRead('-d RF -s en -t sv'.split())
        printer.printPairs()
        self.assertEqual(True, True)

    def test_normal_xml_write(self):
        OpusRead('-d RF -s en -t sv -m 1 -w '
            'test_files/test_result'.split()).printPairs()
        with open('test_files/test_result', 'r') as f:
            self.assertEqual(f.read(),
                '\n# en/1988.xml.gz\n'
                '# sv/1988.xml.gz\n\n'
                '================================\n(src)="s1.1">State'
                'ment of Government Policy by the Prime Minister , Mr'
                ' Ingvar Carlsson , at the Opening of the Swedish Parl'
                'iament on Tuesday , 4 October , 1988 .\n(trg)="s1.1"'
                '>REGERINGSFÖRKLARING .\n============================'
                '====\n')

    def test_normal_xml_write_fast(self):
        OpusRead('-d RF -s en -t sv -m 1 -w '
            'test_files/test_result -f'.split()).printPairs()
        with open('test_files/test_result', 'r') as f:
            self.assertEqual(f.read(),
                '\n# en/1988.xml.gz\n'
                '# sv/1988.xml.gz\n\n'
                '================================\n(src)="s1.1">State'
                'ment of Government Policy by the Prime Minister , Mr'
                ' Ingvar Carlsson , at the Opening of the Swedish Parl'
                'iament on Tuesday , 4 October , 1988 .\n(trg)="s1.1"'
                '>REGERINGSFÖRKLARING .\n============================'
                '====\n')

    def test_normal_xml_print(self):
        var = pairPrinterToVariable(
            '-d RF -s en -t sv -m 1'.split())
        self.assertEqual(var,
            '\n# en/1988.xml.gz\n'
            '# sv/1988.xml.gz\n\n'
            '================================\n(src)="s1.1">State'
            'ment of Government Policy by the Prime Minister , Mr'
            ' Ingvar Carlsson , at the Opening of the Swedish Parl'
            'iament on Tuesday , 4 October , 1988 .\n(trg)="s1.1"'
            '>REGERINGSFÖRKLARING .\n============================'
            '====\n')

    def test_normal_xml_print_fast(self):
        var = pairPrinterToVariable(
            '-d RF -s en -t sv -m 1 -f'.split())
        self.assertEqual(var,
            '\n# en/1988.xml.gz\n'
            '# sv/1988.xml.gz\n\n'
            '================================\n(src)="s1.1">State'
            'ment of Government Policy by the Prime Minister , Mr'
            ' Ingvar Carlsson , at the Opening of the Swedish Parl'
            'iament on Tuesday , 4 October , 1988 .\n(trg)="s1.1"'
            '>REGERINGSFÖRKLARING .\n============================'
            '====\n')

    def test_normal_raw_write(self):
        OpusRead('-d RF -s en -t sv -m 1 -w '
            'test_files/test_result -p raw'.split()).printPairs()
        with open('test_files/test_result', 'r') as f:
            self.assertEqual(f.read(),
                '\n# en/1988.xml.gz\n'
                '# sv/1988.xml.gz\n\n'
                '================================\n(src)="s1.1">State'
                'ment of Government Policy by the Prime Minister, Mr'
                ' Ingvar Carlsson, at the Opening of the Swedish Parl'
                'iament on Tuesday, 4 October, 1988.\n(trg)="s1.1"'
                '>REGERINGSFÖRKLARING.\n============================'
                '====\n')

    def test_normal_raw_write_fast(self):
        OpusRead('-d RF -s en -t sv -m 1 -w '
            'test_files/test_result -p raw -f'.split()).printPairs()
        with open('test_files/test_result', 'r') as f:
            self.assertEqual(f.read(),
                '\n# en/1988.xml.gz\n'
                '# sv/1988.xml.gz\n\n'
                '================================\n(src)="s1.1">State'
                'ment of Government Policy by the Prime Minister, Mr'
                ' Ingvar Carlsson, at the Opening of the Swedish Parl'
                'iament on Tuesday, 4 October, 1988.\n(trg)="s1.1"'
                '>REGERINGSFÖRKLARING.\n============================'
                '====\n')

    def test_normal_raw_print(self):
        var = pairPrinterToVariable(
            '-d RF -s en -t sv -m 1 -p raw'.split())
        self.assertEqual(var,
            '\n# en/1988.xml.gz\n'
            '# sv/1988.xml.gz\n\n'
            '================================\n(src)="s1.1">State'
            'ment of Government Policy by the Prime Minister, Mr'
            ' Ingvar Carlsson, at the Opening of the Swedish Parl'
            'iament on Tuesday, 4 October, 1988.\n(trg)="s1.1"'
            '>REGERINGSFÖRKLARING.\n============================'
            '====\n')

    def test_normal_raw_print_fast(self):
        var = pairPrinterToVariable(
            '-d RF -s en -t sv -m 1 -p raw -f'.split())
        self.assertEqual(var,
            '\n# en/1988.xml.gz\n'
            '# sv/1988.xml.gz\n\n'
            '================================\n(src)="s1.1">State'
            'ment of Government Policy by the Prime Minister, Mr'
            ' Ingvar Carlsson, at the Opening of the Swedish Parl'
            'iament on Tuesday, 4 October, 1988.\n(trg)="s1.1"'
            '>REGERINGSFÖRKLARING.\n============================'
            '====\n')

    def test_normal_raw_print_OpenSubtitles(self):
        var = pairPrinterToVariable(
            '-d OpenSubtitles -s eo -t kk -m 1 -p raw'.split())
        self.assertEqual(var,
            '\n# eo/2001/245429/5818397.xml.gz\n'
            '# kk/2001/245429/6899218.xml.gz\n\n'
             '================================\n(src)="1">Filmo de '
             '"Studio Ghibli"\n(trg)="1">ГИБЛИ" '
             'студиясы\n================================\n')

    def test_normal_raw_print_OpenSubtitles_fast(self):
        var = pairPrinterToVariable(
            '-d OpenSubtitles -s eo -t kk -m 1 -p raw -f'.split())
        self.assertEqual(var,
            '\n# eo/2001/245429/5818397.xml.gz\n'
            '# kk/2001/245429/6899218.xml.gz\n\n'
             '================================\n(src)="1">Filmo de '
             '"Studio Ghibli"\n(trg)="1">ГИБЛИ" '
             'студиясы\n================================\n')


    def test_normal_parsed_write(self):
        OpusRead(
            '-d RF -s en -t sv -m 1 -p parsed -pa -sa upos '
            'feats lemma -ta upos feats lemma '
            '-w test_files/test_result '.split()).printPairs()
        with open('test_files/test_result', 'r') as f:
            self.assertEqual(f.read(),
                '\n# en/1988.xml.gz\n# sv/1988.xml.gz\n\n'
                '================================'
                '\n(src)="s1.1">Statement|NOUN|Number=Sing|statement '
                'of|ADP|of Government|NOUN|Number=Sing|government Pol'
                'icy|NOUN|Number=Sing|policy by|ADP|by the|DET|Defini'
                'te=Def|PronType=Art|the Prime|PROPN|Number=Sing|Prim'
                'e Minister|PROPN|Number=Sing|Minister ,|PUNCT|, Mr|P'
                'ROPN|Number=Sing|Mr Ingvar|PROPN|Number=Sing|Ingvar '
                'Carlsson|PROPN|Number=Sing|Carlsson ,|PUNCT|, at|ADP'
                '|at the|DET|Definite=Def|PronType=Art|the Opening|NO'
                'UN|Number=Sing|opening of|ADP|of the|DET|Definite=De'
                'f|PronType=Art|the Swedish|ADJ|Degree=Pos|swedish Pa'
                'rliament|NOUN|Number=Sing|parliament on|ADP|on Tuesd'
                'ay|PROPN|Number=Sing|Tuesday ,|PUNCT|, 4|NUM|NumType'
                '=Card|4 October|PROPN|Number=Sing|October ,|PUNCT|, '
                '1988|NUM|NumType=Card|1988 .|PUNCT|.\n(trg)="s1.1">R'
                'EGERINGSFÖRKLARING|NOUN|Case=Nom|Definite=Ind|Gender'
                '=Neut|Number=Sing|Regeringsförklaring .|PUNCT|.'
                '\n================================\n')

    def test_normal_parsed_write_fast(self):
        OpusRead(
            '-d RF -s en -t sv -m 1 -p parsed -pa -sa upos '
            'feats lemma -ta upos feats lemma '
            '-w test_files/test_result -f'.split()).printPairs()
        with open('test_files/test_result', 'r') as f:
            self.assertEqual(f.read(),
                '\n# en/1988.xml.gz\n# sv/1988.xml.gz\n\n'
                '================================'
                '\n(src)="s1.1">Statement|NOUN|Number=Sing|statement '
                'of|ADP|of Government|NOUN|Number=Sing|government Pol'
                'icy|NOUN|Number=Sing|policy by|ADP|by the|DET|Defini'
                'te=Def|PronType=Art|the Prime|PROPN|Number=Sing|Prim'
                'e Minister|PROPN|Number=Sing|Minister ,|PUNCT|, Mr|P'
                'ROPN|Number=Sing|Mr Ingvar|PROPN|Number=Sing|Ingvar '
                'Carlsson|PROPN|Number=Sing|Carlsson ,|PUNCT|, at|ADP'
                '|at the|DET|Definite=Def|PronType=Art|the Opening|NO'
                'UN|Number=Sing|opening of|ADP|of the|DET|Definite=De'
                'f|PronType=Art|the Swedish|ADJ|Degree=Pos|swedish Pa'
                'rliament|NOUN|Number=Sing|parliament on|ADP|on Tuesd'
                'ay|PROPN|Number=Sing|Tuesday ,|PUNCT|, 4|NUM|NumType'
                '=Card|4 October|PROPN|Number=Sing|October ,|PUNCT|, '
                '1988|NUM|NumType=Card|1988 .|PUNCT|.\n(trg)="s1.1">R'
                'EGERINGSFÖRKLARING|NOUN|Case=Nom|Definite=Ind|Gender'
                '=Neut|Number=Sing|Regeringsförklaring .|PUNCT|.'
                '\n================================\n')

    def test_normal_parsed_print(self):
        var = pairPrinterToVariable(
            '-d RF -s en -t sv -m 1 -p parsed -pa -sa upos '
            'feats lemma -ta upos feats lemma '.split())
        self.assertEqual(var,
            '\n# en/1988.xml.gz\n# sv/1988.xml.gz\n\n'
            '================================'
            '\n(src)="s1.1">Statement|NOUN|Number=Sing|statement '
            'of|ADP|of Government|NOUN|Number=Sing|government Pol'
            'icy|NOUN|Number=Sing|policy by|ADP|by the|DET|Defini'
            'te=Def|PronType=Art|the Prime|PROPN|Number=Sing|Prim'
            'e Minister|PROPN|Number=Sing|Minister ,|PUNCT|, Mr|P'
            'ROPN|Number=Sing|Mr Ingvar|PROPN|Number=Sing|Ingvar '
            'Carlsson|PROPN|Number=Sing|Carlsson ,|PUNCT|, at|ADP'
            '|at the|DET|Definite=Def|PronType=Art|the Opening|NO'
            'UN|Number=Sing|opening of|ADP|of the|DET|Definite=De'
            'f|PronType=Art|the Swedish|ADJ|Degree=Pos|swedish Pa'
            'rliament|NOUN|Number=Sing|parliament on|ADP|on Tuesd'
            'ay|PROPN|Number=Sing|Tuesday ,|PUNCT|, 4|NUM|NumType'
            '=Card|4 October|PROPN|Number=Sing|October ,|PUNCT|, '
            '1988|NUM|NumType=Card|1988 .|PUNCT|.\n(trg)="s1.1">R'
            'EGERINGSFÖRKLARING|NOUN|Case=Nom|Definite=Ind|Gender'
            '=Neut|Number=Sing|Regeringsförklaring .|PUNCT|.'
            '\n================================\n')

    def test_normal_parsed_print_unalphabetical(self):
        var = pairPrinterToVariable(
            '-d RF -s sv -t en -m 1 -p parsed -pa -sa upos '
            'feats lemma -ta upos feats lemma '.split())
        self.assertEqual(var,
            '\n# en/1988.xml.gz\n# sv/1988.xml.gz\n\n'
            '================================'
            '\n(src)="s1.1">REGERINGSFÖRKLARING|NOUN|Case=Nom|Definit'
            'e=Ind|Gender=Neut|Number=Sing|Regeringsförklaring .|PUNC'
            'T|.\n(trg)="s1.1">Statement|NOUN|Number=Sing|statement '
            'of|ADP|of Government|NOUN|Number=Sing|government Pol'
            'icy|NOUN|Number=Sing|policy by|ADP|by the|DET|Defini'
            'te=Def|PronType=Art|the Prime|PROPN|Number=Sing|Prim'
            'e Minister|PROPN|Number=Sing|Minister ,|PUNCT|, Mr|P'
            'ROPN|Number=Sing|Mr Ingvar|PROPN|Number=Sing|Ingvar '
            'Carlsson|PROPN|Number=Sing|Carlsson ,|PUNCT|, at|ADP'
            '|at the|DET|Definite=Def|PronType=Art|the Opening|NO'
            'UN|Number=Sing|opening of|ADP|of the|DET|Definite=De'
            'f|PronType=Art|the Swedish|ADJ|Degree=Pos|swedish Pa'
            'rliament|NOUN|Number=Sing|parliament on|ADP|on Tuesd'
            'ay|PROPN|Number=Sing|Tuesday ,|PUNCT|, 4|NUM|NumType'
            '=Card|4 October|PROPN|Number=Sing|October ,|PUNCT|, '
            '1988|NUM|NumType=Card|1988 .|PUNCT|.'
            '\n================================\n')

    def test_normal_parsed_print_fast(self):
        var = pairPrinterToVariable(
            '-d RF -s en -t sv -m 1 -p parsed -pa -sa upos '
            'feats lemma -ta upos feats lemma -f'.split())
        self.assertEqual(var,
            '\n# en/1988.xml.gz\n# sv/1988.xml.gz\n\n'
            '================================'
            '\n(src)="s1.1">Statement|NOUN|Number=Sing|statement '
            'of|ADP|of Government|NOUN|Number=Sing|government Pol'
            'icy|NOUN|Number=Sing|policy by|ADP|by the|DET|Defini'
            'te=Def|PronType=Art|the Prime|PROPN|Number=Sing|Prim'
            'e Minister|PROPN|Number=Sing|Minister ,|PUNCT|, Mr|P'
            'ROPN|Number=Sing|Mr Ingvar|PROPN|Number=Sing|Ingvar '
            'Carlsson|PROPN|Number=Sing|Carlsson ,|PUNCT|, at|ADP'
            '|at the|DET|Definite=Def|PronType=Art|the Opening|NO'
            'UN|Number=Sing|opening of|ADP|of the|DET|Definite=De'
            'f|PronType=Art|the Swedish|ADJ|Degree=Pos|swedish Pa'
            'rliament|NOUN|Number=Sing|parliament on|ADP|on Tuesd'
            'ay|PROPN|Number=Sing|Tuesday ,|PUNCT|, 4|NUM|NumType'
            '=Card|4 October|PROPN|Number=Sing|October ,|PUNCT|, '
            '1988|NUM|NumType=Card|1988 .|PUNCT|.\n(trg)="s1.1">R'
            'EGERINGSFÖRKLARING|NOUN|Case=Nom|Definite=Ind|Gender'
            '=Neut|Number=Sing|Regeringsförklaring .|PUNCT|.'
            '\n================================\n')

    def test_normal_parsed_print_all_attributes(self):
        var = pairPrinterToVariable(
            '-d RF -s en -t sv -m 1 -p parsed -pa -sa all_attrs '
            '-ta all_attrs'.split())
        self.assertEqual(var,
            '\n# en/1988.xml.gz\n# sv/1988.xml.gz\n\n'
            '================================'
            '\n(src)="s1.1">Statement|root|Number=Sing|0|w1.1.1|state'
            'ment|NOUN|NOUN of|case|w1.1.4|w1.1.2|of|ADP|ADP Governme'
            'nt|compound|Number=Sing|w1.1.4|w1.1.3|government|NOUN|NO'
            'UN Policy|nmod|Number=Sing|w1.1.1|w1.1.4|policy|NOUN|NOU'
            'N by|case|w1.1.8|w1.1.5|by|ADP|ADP the|det|Definite=Def|'
            'PronType=Art|w1.1.8|w1.1.6|the|DET|DET Prime|compound|Nu'
            'mber=Sing|w1.1.8|w1.1.7|Prime|PROPN|PROPN Minister|nmod|'
            'Number=Sing|w1.1.1|w1.1.8|Minister|SpaceAfter=No|PROPN|P'
            'ROPN ,|punct|w1.1.8|w1.1.9|,|PUNCT|PUNCT Mr|compound|Num'
            'ber=Sing|w1.1.12|w1.1.10|Mr|PROPN|PROPN Ingvar|flat|Numb'
            'er=Sing|w1.1.10|w1.1.11|Ingvar|PROPN|PROPN Carlsson|flat'
            '|Number=Sing|w1.1.8|w1.1.12|Carlsson|SpaceAfter=No|PROPN'
            '|PROPN ,|punct|w1.1.1|w1.1.13|,|PUNCT|PUNCT at|case|w1.1'
            '.16|w1.1.14|at|ADP|ADP the|det|Definite=Def|PronType=Art'
            '|w1.1.16|w1.1.15|the|DET|DET Opening|nmod|Number=Sing|w1'
            '.1.1|w1.1.16|opening|NOUN|NOUN of|case|w1.1.20|w1.1.17|o'
            'f|ADP|ADP the|det|Definite=Def|PronType=Art|w1.1.20|w1.1'
            '.18|the|DET|DET Swedish|amod|Degree=Pos|w1.1.20|w1.1.19|'
            'swedish|ADJ|ADJ Parliament|nmod|Number=Sing|w1.1.16|w1.1'
            '.20|parliament|NOUN|NOUN on|case|w1.1.22|w1.1.21|on|ADP|'
            'ADP Tuesday|nmod|Number=Sing|w1.1.16|w1.1.22|Tuesday|Spa'
            'ceAfter=No|PROPN|PROPN ,|punct|w1.1.1|w1.1.23|,|PUNCT|PU'
            'NCT 4|nummod|NumType=Card|w1.1.25|w1.1.24|4|NUM|NUM Octo'
            'ber|appos|Number=Sing|w1.1.1|w1.1.25|October|SpaceAfter='
            'No|PROPN|PROPN ,|punct|w1.1.25|w1.1.26|,|PUNCT|PUNCT 198'
            '8|nummod|NumType=Card|w1.1.25|w1.1.27|1988|SpaceAfter=No'
            '|NUM|NUM .|punct|w1.1.1|w1.1.28|.|SpaceAfter=No|PUNCT|PU'
            'NCT\n(trg)="s1.1">REGERINGSFÖRKLARING|root|Case=Nom|Defini'
            'te=Ind|Gender=Neut|Number=Sing|0|w1.1.1|Regeringsförklar'
            'ing|SpaceAfter=No|NOUN|NOUN .|punct|w1.1.1|w1.1.2|.|Spac'
            'eAfter=No|PUNCT|PUNCT'
            '\n================================\n')

    def test_normal_parsed_print_all_attributes_fast(self):
        var = pairPrinterToVariable(
            '-d RF -s en -t sv -m 1 -p parsed -pa -sa all_attrs '
            '-ta all_attrs -f'.split())
        self.assertEqual(var,
            '\n# en/1988.xml.gz\n# sv/1988.xml.gz\n\n'
            '================================'
            '\n(src)="s1.1">Statement|root|Number=Sing|0|w1.1.1|state'
            'ment|NOUN|NOUN of|case|w1.1.4|w1.1.2|of|ADP|ADP Governme'
            'nt|compound|Number=Sing|w1.1.4|w1.1.3|government|NOUN|NO'
            'UN Policy|nmod|Number=Sing|w1.1.1|w1.1.4|policy|NOUN|NOU'
            'N by|case|w1.1.8|w1.1.5|by|ADP|ADP the|det|Definite=Def|'
            'PronType=Art|w1.1.8|w1.1.6|the|DET|DET Prime|compound|Nu'
            'mber=Sing|w1.1.8|w1.1.7|Prime|PROPN|PROPN Minister|nmod|'
            'Number=Sing|w1.1.1|w1.1.8|Minister|SpaceAfter=No|PROPN|P'
            'ROPN ,|punct|w1.1.8|w1.1.9|,|PUNCT|PUNCT Mr|compound|Num'
            'ber=Sing|w1.1.12|w1.1.10|Mr|PROPN|PROPN Ingvar|flat|Numb'
            'er=Sing|w1.1.10|w1.1.11|Ingvar|PROPN|PROPN Carlsson|flat'
            '|Number=Sing|w1.1.8|w1.1.12|Carlsson|SpaceAfter=No|PROPN'
            '|PROPN ,|punct|w1.1.1|w1.1.13|,|PUNCT|PUNCT at|case|w1.1'
            '.16|w1.1.14|at|ADP|ADP the|det|Definite=Def|PronType=Art'
            '|w1.1.16|w1.1.15|the|DET|DET Opening|nmod|Number=Sing|w1'
            '.1.1|w1.1.16|opening|NOUN|NOUN of|case|w1.1.20|w1.1.17|o'
            'f|ADP|ADP the|det|Definite=Def|PronType=Art|w1.1.20|w1.1'
            '.18|the|DET|DET Swedish|amod|Degree=Pos|w1.1.20|w1.1.19|'
            'swedish|ADJ|ADJ Parliament|nmod|Number=Sing|w1.1.16|w1.1'
            '.20|parliament|NOUN|NOUN on|case|w1.1.22|w1.1.21|on|ADP|'
            'ADP Tuesday|nmod|Number=Sing|w1.1.16|w1.1.22|Tuesday|Spa'
            'ceAfter=No|PROPN|PROPN ,|punct|w1.1.1|w1.1.23|,|PUNCT|PU'
            'NCT 4|nummod|NumType=Card|w1.1.25|w1.1.24|4|NUM|NUM Octo'
            'ber|appos|Number=Sing|w1.1.1|w1.1.25|October|SpaceAfter='
            'No|PROPN|PROPN ,|punct|w1.1.25|w1.1.26|,|PUNCT|PUNCT 198'
            '8|nummod|NumType=Card|w1.1.25|w1.1.27|1988|SpaceAfter=No'
            '|NUM|NUM .|punct|w1.1.1|w1.1.28|.|SpaceAfter=No|PUNCT|PU'
            'NCT\n(trg)="s1.1">REGERINGSFÖRKLARING|root|Case=Nom|Defini'
            'te=Ind|Gender=Neut|Number=Sing|0|w1.1.1|Regeringsförklar'
            'ing|SpaceAfter=No|NOUN|NOUN .|punct|w1.1.1|w1.1.2|.|Spac'
            'eAfter=No|PUNCT|PUNCT'
            '\n================================\n')

    def test_tmx_xml_write(self):
        OpusRead(
            '-d RF -s en -t sv -m 1 -w test_files/test_result '
            '-wm tmx'.split()).printPairs()
        with open('test_files/test_result', 'r') as f:
            self.assertEqual(f.read(),
                '<?xml version="1.0" encoding="utf-8"?>\n<tmx version="1.4.">'
                '\n<header srclang="en"\n\tadminlang="en"\n\tsegtype='
                '"sentence"\n\tdatatype="PlainText" />\n\t<body>\n\t\t<tu>'
                '\n\t\t\t<tuv xml:lang="en"><seg>Statement of Governm'
                'ent Policy by the Prime Minister , Mr Ingvar Carlsso'
                'n , at the Opening of the Swedish Parliament on Tues'
                'day , 4 October , 1988 .'
                '</seg></tuv>\n\t\t\t<tuv xml:lang="sv"><seg>REGERING'
                'SFÖRKLARING .</seg></tuv>\n\t\t</tu>\n\t</body>\n</tmx>')

    def test_tmx_xml_write_unalphabetical(self):
        OpusRead(
            '-d RF -s sv -t en -m 1 -w test_files/test_result '
            '-wm tmx'.split()).printPairs()
        with open('test_files/test_result', 'r') as f:
            self.assertEqual(f.read(),
                '<?xml version="1.0" encoding="utf-8"?>\n<tmx version="1.4.">'
                '\n<header srclang="sv"\n\tadminlang="en"\n\tsegtype='
                '"sentence"\n\tdatatype="PlainText" />\n\t<body>\n\t\t<tu>'
                '\n\t\t\t<tuv xml:lang="sv"><seg>REGERING'
                'SFÖRKLARING .</seg></tuv>\n\t\t\t<tuv xml:lang="en">'
                '<seg>Statement of Governm'
                'ent Policy by the Prime Minister , Mr Ingvar Carlsso'
                'n , at the Opening of the Swedish Parliament on Tues'
                'day , 4 October , 1988 .'
                '</seg></tuv>\n\t\t</tu>\n\t</body>\n</tmx>')

    def test_tmx_xml_write_fast(self):
        OpusRead(
            '-d RF -s en -t sv -m 1 -w test_files/test_result '
            '-wm tmx -f'.split()).printPairs()
        with open('test_files/test_result', 'r') as f:
            self.assertEqual(f.read(),
                '<?xml version="1.0" encoding="utf-8"?>\n<tmx version="1.4.">'
                '\n<header srclang="en"\n\tadminlang="en"\n\tsegtype='
                '"sentence"\n\tdatatype="PlainText" />\n\t<body>\n\t\t<tu>'
                '\n\t\t\t<tuv xml:lang="en"><seg>Statement of Governm'
                'ent Policy by the Prime Minister , Mr Ingvar Carlsso'
                'n , at the Opening of the Swedish Parliament on Tues'
                'day , 4 October , 1988 .'
                '</seg></tuv>\n\t\t\t<tuv xml:lang="sv"><seg>REGERING'
                'SFÖRKLARING .</seg></tuv>\n\t\t</tu>\n\t</body>\n</tmx>')

    def test_tmx_xml_print(self):
        var = pairPrinterToVariable(
            '-d RF -s en -t sv -m 1 -wm tmx'.split())
        self.assertEqual(var,
            '<?xml version="1.0" encoding="utf-8"?>\n<tmx version="1.4.">'
            '\n<header srclang="en"\n\tadminlang="en"\n\tsegtype='
            '"sentence"\n\tdatatype="PlainText" />\n\t<body>\n\t\t<tu>'
            '\n\t\t\t<tuv xml:lang="en"><seg>Statement of Governm'
            'ent Policy by the Prime Minister , Mr Ingvar Carlsso'
            'n , at the Opening of the Swedish Parliament on Tues'
            'day , 4 October , 1988 .'
            '</seg></tuv>\n\t\t\t<tuv xml:lang="sv"><seg>REGERING'
            'SFÖRKLARING .</seg></tuv>\n\t\t</tu>\n\t</body>\n</tmx>\n')

    def test_tmx_xml_print_unalphabetical(self):
        var = pairPrinterToVariable(
            '-d RF -s sv -t en -m 1 -wm tmx'.split())
        self.assertEqual(var,
            '<?xml version="1.0" encoding="utf-8"?>\n<tmx version="1.4.">'
            '\n<header srclang="sv"\n\tadminlang="en"\n\tsegtype='
            '"sentence"\n\tdatatype="PlainText" />\n\t<body>\n\t\t<tu>'
            '\n\t\t\t<tuv xml:lang="sv"><seg>REGERING'
            'SFÖRKLARING .</seg></tuv>\n\t\t\t<tuv xml:lang="en"><seg'
            '>Statement of Governm'
            'ent Policy by the Prime Minister , Mr Ingvar Carlsso'
            'n , at the Opening of the Swedish Parliament on Tues'
            'day , 4 October , 1988 .'
            '</seg></tuv>\n\t\t</tu>\n\t</body>\n</tmx>\n')

    def test_tmx_xml_print_fast(self):
        var = pairPrinterToVariable(
            '-d RF -s en -t sv -m 1 -wm tmx -f'.split())
        self.assertEqual(var,
            '<?xml version="1.0" encoding="utf-8"?>\n<tmx version="1.4.">'
            '\n<header srclang="en"\n\tadminlang="en"\n\tsegtype='
            '"sentence"\n\tdatatype="PlainText" />\n\t<body>\n\t\t<tu>'
            '\n\t\t\t<tuv xml:lang="en"><seg>Statement of Governm'
            'ent Policy by the Prime Minister , Mr Ingvar Carlsso'
            'n , at the Opening of the Swedish Parliament on Tues'
            'day , 4 October , 1988 .'
            '</seg></tuv>\n\t\t\t<tuv xml:lang="sv"><seg>REGERING'
            'SFÖRKLARING .</seg></tuv>\n\t\t</tu>\n\t</body>\n</tmx>\n')

    def test_tmx_raw_write(self):
        OpusRead(
            '-d RF -s en -t sv -m 1 -w test_files/test_result -wm tmx'
            ' -p raw'.split()).printPairs()
        with open('test_files/test_result', 'r') as f:
            self.assertEqual(f.read(),
                '<?xml version="1.0" encoding="utf-8"?>\n<tmx version="1.4.">'
                '\n<header srclang="en"\n\tadminlang="en"\n\tsegtype='
                '"sentence"\n\tdatatype="PlainText" />\n\t<body>\n\t\t<tu>'
                '\n\t\t\t<tuv xml:lang="en"><seg>Statement of Governm'
                'ent Policy by the Prime Minister, Mr Ingvar Carlsso'
                'n, at the Opening of the Swedish Parliament on Tues'
                'day, 4 October, 1988.'
                '</seg></tuv>\n\t\t\t<tuv xml:lang="sv"><seg>REGERING'
                'SFÖRKLARING.</seg></tuv>\n\t\t</tu>\n\t</body>\n</tmx>')

    def test_tmx_raw_write_fast(self):
        OpusRead(
            '-d RF -s en -t sv -m 1 -w test_files/test_result -wm tmx'
            ' -p raw -f'.split()).printPairs()
        with open('test_files/test_result', 'r') as f:
            self.assertEqual(f.read(),
                '<?xml version="1.0" encoding="utf-8"?>\n<tmx version="1.4.">'
                '\n<header srclang="en"\n\tadminlang="en"\n\tsegtype='
                '"sentence"\n\tdatatype="PlainText" />\n\t<body>\n\t\t<tu>'
                '\n\t\t\t<tuv xml:lang="en"><seg>Statement of Governm'
                'ent Policy by the Prime Minister, Mr Ingvar Carlsso'
                'n, at the Opening of the Swedish Parliament on Tues'
                'day, 4 October, 1988.'
                '</seg></tuv>\n\t\t\t<tuv xml:lang="sv"><seg>REGERING'
                'SFÖRKLARING.</seg></tuv>\n\t\t</tu>\n\t</body>\n</tmx>')

    def test_tmx_raw_print(self):
        var = pairPrinterToVariable(
            '-d RF -s en -t sv -m 1 -wm tmx -p raw'.split())
        self.assertEqual(var,
            '<?xml version="1.0" encoding="utf-8"?>\n<tmx version="1.4.">'
            '\n<header srclang="en"\n\tadminlang="en"\n\tsegtype='
            '"sentence"\n\tdatatype="PlainText" />\n\t<body>\n\t\t<tu>'
            '\n\t\t\t<tuv xml:lang="en"><seg>Statement of Governm'
            'ent Policy by the Prime Minister, Mr Ingvar Carlsso'
            'n, at the Opening of the Swedish Parliament on Tues'
            'day, 4 October, 1988.'
            '</seg></tuv>\n\t\t\t<tuv xml:lang="sv"><seg>REGERING'
            'SFÖRKLARING.</seg></tuv>\n\t\t</tu>\n\t</body>\n</tmx>\n')

    def test_tmx_raw_print_fast(self):
        var = pairPrinterToVariable(
            '-d RF -s en -t sv -m 1 -wm tmx -p raw -f'.split())
        self.assertEqual(var,
            '<?xml version="1.0" encoding="utf-8"?>\n<tmx version="1.4.">'
            '\n<header srclang="en"\n\tadminlang="en"\n\tsegtype='
            '"sentence"\n\tdatatype="PlainText" />\n\t<body>\n\t\t<tu>'
            '\n\t\t\t<tuv xml:lang="en"><seg>Statement of Governm'
            'ent Policy by the Prime Minister, Mr Ingvar Carlsso'
            'n, at the Opening of the Swedish Parliament on Tues'
            'day, 4 October, 1988.'
            '</seg></tuv>\n\t\t\t<tuv xml:lang="sv"><seg>REGERING'
            'SFÖRKLARING.</seg></tuv>\n\t\t</tu>\n\t</body>\n</tmx>\n')

    def test_tmx_parsed_write(self):
        OpusRead(
            '-d RF -s en -t sv -m 1 -w test_files/test_result -wm tmx '
            '-p parsed -pa -sa upos feats lemma -ta upos feats '
            'lemma'.split()).printPairs()
        with open('test_files/test_result', 'r') as f:
            self.assertEqual(f.read(),
                '<?xml version="1.0" encoding="utf-8"?>\n<tmx version="1.4.">'
                '\n<header srclang="en"\n\tadminlang="en"\n\tsegtype='
                '"sentence"\n\tdatatype="PlainText" />\n\t<body>\n\t\t<tu>'
                '\n\t\t\t<tuv xml:lang="en"><seg>Statement|NOUN|Numbe'
                'r=Sing|statement of|ADP|of Government|NOUN|Number=Si'
                'ng|government Policy|NOUN|Number=Sing|policy by|ADP|'
                'by the|DET|Definite=Def|PronType=Art|the Prime|PROPN'
                '|Number=Sing|Prime Minister|PROPN|Number=Sing|Minist'
                'er ,|PUNCT|, Mr|PROPN|Number=Sing|Mr Ingvar|PROPN|Nu'
                'mber=Sing|Ingvar Carlsson|PROPN|Number=Sing|Carlsson '
                ',|PUNCT|, at|ADP|at the|DET|Definite=Def|PronType=Ar'
                't|the Opening|NOUN|Number=Sing|opening of|ADP|of the'
                '|DET|Definite=Def|PronType=Art|the Swedish|ADJ|Degre'
                'e=Pos|swedish Parliament|NOUN|Number=Sing|parliament '
                'on|ADP|on Tuesday|PROPN|Number=Sing|Tuesday ,|PUNCT|'
                ', 4|NUM|NumType=Card|4 October|PROPN|Number=Sing|Oct'
                'ober ,|PUNCT|, 1988|NUM|NumType=Card|1988 .|PUNCT|.<'
                '/seg></tuv>\n\t\t\t<tuv xml:lang="sv"><seg>REGERINGS'
                'FÖRKLARING|NOUN|Case=Nom|Definite=Ind|Gender=Neut|Nu'
                'mber=Sing|Regeringsförklaring .|PUNCT|.</seg></tuv>'
                '\n\t\t</tu>\n\t</body>\n</tmx>')

    def test_tmx_parsed_write_fast(self):
        OpusRead(
            '-d RF -s en -t sv -m 1 -w test_files/test_result -wm tmx '
            '-p parsed -pa -sa upos feats lemma -ta upos feats '
            'lemma -f'.split()).printPairs()
        with open('test_files/test_result', 'r') as f:
            self.assertEqual(f.read(),
                '<?xml version="1.0" encoding="utf-8"?>\n<tmx version="1.4.">'
                '\n<header srclang="en"\n\tadminlang="en"\n\tsegtype='
                '"sentence"\n\tdatatype="PlainText" />\n\t<body>\n\t\t<tu>'
                '\n\t\t\t<tuv xml:lang="en"><seg>Statement|NOUN|Numbe'
                'r=Sing|statement of|ADP|of Government|NOUN|Number=Si'
                'ng|government Policy|NOUN|Number=Sing|policy by|ADP|'
                'by the|DET|Definite=Def|PronType=Art|the Prime|PROPN'
                '|Number=Sing|Prime Minister|PROPN|Number=Sing|Minist'
                'er ,|PUNCT|, Mr|PROPN|Number=Sing|Mr Ingvar|PROPN|Nu'
                'mber=Sing|Ingvar Carlsson|PROPN|Number=Sing|Carlsson '
                ',|PUNCT|, at|ADP|at the|DET|Definite=Def|PronType=Ar'
                't|the Opening|NOUN|Number=Sing|opening of|ADP|of the'
                '|DET|Definite=Def|PronType=Art|the Swedish|ADJ|Degre'
                'e=Pos|swedish Parliament|NOUN|Number=Sing|parliament '
                'on|ADP|on Tuesday|PROPN|Number=Sing|Tuesday ,|PUNCT|'
                ', 4|NUM|NumType=Card|4 October|PROPN|Number=Sing|Oct'
                'ober ,|PUNCT|, 1988|NUM|NumType=Card|1988 .|PUNCT|.<'
                '/seg></tuv>\n\t\t\t<tuv xml:lang="sv"><seg>REGERINGS'
                'FÖRKLARING|NOUN|Case=Nom|Definite=Ind|Gender=Neut|Nu'
                'mber=Sing|Regeringsförklaring .|PUNCT|.</seg></tuv>'
                '\n\t\t</tu>\n\t</body>\n</tmx>')

    def test_tmx_parsed_print(self):
        var = pairPrinterToVariable(
            '-d RF -s en -t sv -m 1 -wm tmx -p parsed -pa -sa upos '
            'feats lemma -ta upos feats lemma'.split())
        self.assertEqual(var,
            '<?xml version="1.0" encoding="utf-8"?>\n<tmx version="1.4.">'
            '\n<header srclang="en"\n\tadminlang="en"\n\tsegtype='
            '"sentence"\n\tdatatype="PlainText" />\n\t<body>\n\t\t<tu>'
            '\n\t\t\t<tuv xml:lang="en"><seg>Statement|NOUN|Numbe'
            'r=Sing|statement of|ADP|of Government|NOUN|Number=Si'
            'ng|government Policy|NOUN|Number=Sing|policy by|ADP|'
            'by the|DET|Definite=Def|PronType=Art|the Prime|PROPN'
            '|Number=Sing|Prime Minister|PROPN|Number=Sing|Minist'
            'er ,|PUNCT|, Mr|PROPN|Number=Sing|Mr Ingvar|PROPN|Nu'
            'mber=Sing|Ingvar Carlsson|PROPN|Number=Sing|Carlsson '
            ',|PUNCT|, at|ADP|at the|DET|Definite=Def|PronType=Ar'
            't|the Opening|NOUN|Number=Sing|opening of|ADP|of the'
            '|DET|Definite=Def|PronType=Art|the Swedish|ADJ|Degre'
            'e=Pos|swedish Parliament|NOUN|Number=Sing|parliament '
            'on|ADP|on Tuesday|PROPN|Number=Sing|Tuesday ,|PUNCT|'
            ', 4|NUM|NumType=Card|4 October|PROPN|Number=Sing|Oct'
            'ober ,|PUNCT|, 1988|NUM|NumType=Card|1988 .|PUNCT|.<'
            '/seg></tuv>\n\t\t\t<tuv xml:lang="sv"><seg>REGERINGS'
            'FÖRKLARING|NOUN|Case=Nom|Definite=Ind|Gender=Neut|Nu'
            'mber=Sing|Regeringsförklaring .|PUNCT|.</seg></tuv>'
            '\n\t\t</tu>\n\t</body>\n</tmx>\n')

    def test_tmx_parsed_print_fast(self):
        var = pairPrinterToVariable(
            '-d RF -s en -t sv -m 1 -wm tmx -p parsed -pa -sa upos '
            'feats lemma -ta upos feats lemma -f'.split())
        self.assertEqual(var,
            '<?xml version="1.0" encoding="utf-8"?>\n<tmx version="1.4.">'
            '\n<header srclang="en"\n\tadminlang="en"\n\tsegtype='
            '"sentence"\n\tdatatype="PlainText" />\n\t<body>\n\t\t<tu>'
            '\n\t\t\t<tuv xml:lang="en"><seg>Statement|NOUN|Numbe'
            'r=Sing|statement of|ADP|of Government|NOUN|Number=Si'
            'ng|government Policy|NOUN|Number=Sing|policy by|ADP|'
            'by the|DET|Definite=Def|PronType=Art|the Prime|PROPN'
            '|Number=Sing|Prime Minister|PROPN|Number=Sing|Minist'
            'er ,|PUNCT|, Mr|PROPN|Number=Sing|Mr Ingvar|PROPN|Nu'
            'mber=Sing|Ingvar Carlsson|PROPN|Number=Sing|Carlsson '
            ',|PUNCT|, at|ADP|at the|DET|Definite=Def|PronType=Ar'
            't|the Opening|NOUN|Number=Sing|opening of|ADP|of the'
            '|DET|Definite=Def|PronType=Art|the Swedish|ADJ|Degre'
            'e=Pos|swedish Parliament|NOUN|Number=Sing|parliament '
            'on|ADP|on Tuesday|PROPN|Number=Sing|Tuesday ,|PUNCT|'
            ', 4|NUM|NumType=Card|4 October|PROPN|Number=Sing|Oct'
            'ober ,|PUNCT|, 1988|NUM|NumType=Card|1988 .|PUNCT|.<'
            '/seg></tuv>\n\t\t\t<tuv xml:lang="sv"><seg>REGERINGS'
            'FÖRKLARING|NOUN|Case=Nom|Definite=Ind|Gender=Neut|Nu'
            'mber=Sing|Regeringsförklaring .|PUNCT|.</seg></tuv>'
            '\n\t\t</tu>\n\t</body>\n</tmx>\n')

    def test_moses_xml_write(self):
        OpusRead(
            '-d RF -s en -t sv -m 1 -w test_files/test.src '
            'test_files/test.trg -wm moses'.split()).printPairs()
        with open('test_files/test.src', 'r') as f:
            self.assertEqual(f.read(),
            'Statement of Government Policy by the Prime Minister , '
            'Mr Ingvar Carlsson , at the Opening of the Swedish Parli'
            'ament on Tuesday , 4 October , 1988 .\n')
        with open('test_files/test.trg', 'r') as f:
            self.assertEqual(f.read(), 'REGERINGSFÖRKLARING .\n')

    def test_moses_xml_write_unalphabetical(self):
        OpusRead(
            '-d RF -s sv -t en -m 1 -w test_files/test.src '
            'test_files/test.trg -wm moses'.split()).printPairs()
        with open('test_files/test.trg', 'r') as f:
            self.assertEqual(f.read(),
            'Statement of Government Policy by the Prime Minister , '
            'Mr Ingvar Carlsson , at the Opening of the Swedish Parli'
            'ament on Tuesday , 4 October , 1988 .\n')
        with open('test_files/test.src', 'r') as f:
            self.assertEqual(f.read(), 'REGERINGSFÖRKLARING .\n')

    def test_moses_xml_write_with_file_names(self):
        OpusRead(
            '-d RF -s en -t sv -m 1 -w test_files/test.src '
            'test_files/test.trg -wm moses -pn'.split()).printPairs()
        with open('test_files/test.src', 'r') as f:
            self.assertEqual(f.read(),
            '\n<fromDoc>en/1988.xml.gz</fromDoc>\n\nStatement of Gover'
            'nment Policy by the Prime Minister , '
            'Mr Ingvar Carlsson , at the Opening of the Swedish Parli'
            'ament on Tuesday , 4 October , 1988 .\n')
        with open('test_files/test.trg', 'r') as f:
            self.assertEqual(f.read(),
            '\n<toDoc>sv/1988.xml.gz</toDoc>\n\nREGERINGSFÖRKLARING .\n')

    def test_moses_xml_write_single_file(self):
        OpusRead(
            '-d RF -s en -t sv -m 1 -w test_files/test.src '
            '-wm moses'.split()).printPairs()
        with open('test_files/test.src', 'r') as f:
            self.assertEqual(f.read(),
                'Statement of Government Policy by the Prime Minister , '
                'Mr Ingvar Carlsson , at the Opening of the Swedish Parli'
                'ament on Tuesday , 4 October , 1988 .\tREGERINGSFÖRK'
                'LARING .\n')

    def test_moses_xml_write_single_file_unalphabetical(self):
        OpusRead(
            '-d RF -s sv -t en -m 1 -w test_files/test.src '
            '-wm moses'.split()).printPairs()
        with open('test_files/test.src', 'r') as f:
            self.assertEqual(f.read(),
                'REGERINGSFÖRKLARING .\tStatement of Government Poli'
                'cy by the Prime Minister , Mr Ingvar Carlsson , at t'
                'he Opening of the Swedish Parliament on Tuesday , 4 '
                'October , 1988 .\n')

    def test_moses_xml_write_single_file_with_file_names(self):
        OpusRead(
            '-d RF -s en -t sv -m 1 -w test_files/test.src '
            '-wm moses -pn'.split()).printPairs()
        with open('test_files/test.src', 'r') as f:
            self.assertEqual(f.read(),
                '\n<fromDoc>en/1988.xml.gz</fromDoc>\n<toDoc>sv/1988'
                '.xml.gz</toDoc>\n\nStatement of Government Policy by'
                ' the Prime Minister , Mr Ingvar Carlsson , at the Ope'
                'ning of the Swedish Parliament on Tuesday , 4 Octobe'
                'r , 1988 .\tREGERINGSFÖRKLARING .\n')

    def test_moses_xml_write_single_file_with_file_names_unalphabetical(self):
        OpusRead(
            '-d RF -s sv -t en -m 1 -w test_files/test.src '
            '-wm moses -pn'.split()).printPairs()
        with open('test_files/test.src', 'r') as f:
            self.assertEqual(f.read(),
                '\n<fromDoc>en/1988.xml.gz</fromDoc>\n<toDoc>sv/1988'
                '.xml.gz</toDoc>\n\nREGERINGSFÖRKLARING .\tStatement '
                'of Government Policy by the Prime Minister , Mr Ingv'
                'ar Carlsson , at the Opening of the Swedish Parliame'
                'nt on Tuesday , 4 October , 1988 .\n')

    def test_moses_xml_write_fast(self):
        OpusRead(
            '-d RF -s en -t sv -m 1 -w test_files/test.src '
            'test_files/test.trg -wm moses -f'.split()).printPairs()
        with open('test_files/test.src', 'r') as f:
            self.assertEqual(f.read(),
            'Statement of Government Policy by the Prime Minister , '
            'Mr Ingvar Carlsson , at the Opening of the Swedish Parli'
            'ament on Tuesday , 4 October , 1988 .\n')
        with open('test_files/test.trg', 'r') as f:
            self.assertEqual(f.read(), 'REGERINGSFÖRKLARING .\n')

    def test_moses_xml_print(self):
        var = pairPrinterToVariable('-d RF -s en -t sv -m 1 -wm moses'.split())
        self.assertEqual(var,
            'Statement of Government Policy by the Prime Minister , '
            'Mr Ingvar Carlsson , at the Opening of the Swedish Parli'
            'ament on Tuesday , 4 October , 1988 .\t'
            'REGERINGSFÖRKLARING .\n')

    def test_moses_xml_print_unalphabetical(self):
        var = pairPrinterToVariable('-d RF -s sv -t en -m 1 -wm moses'.split())
        self.assertEqual(var,
            'REGERINGSFÖRKLARING .\tStatement of Government Policy b'
            'y the Prime Minister , Mr Ingvar Carlsson , at the Openi'
            'ng of the Swedish Parliament on Tuesday , 4 October , 1988 .\n')

    def test_moses_xml_print_with_file_names(self):
        var = pairPrinterToVariable(
            '-d RF -s en -t sv -m 1 -wm moses -pn'.split())
        self.assertEqual(var,
            '\n<fromDoc>en/1988.xml.gz</fromDoc>\n<toDoc>sv/1988'
            '.xml.gz</toDoc>\n\nStatement of Government Policy by'
            ' the Prime Minister , Mr Ingvar Carlsson , at the Ope'
            'ning of the Swedish Parliament on Tuesday , 4 Octobe'
            'r , 1988 .\tREGERINGSFÖRKLARING .\n')

    def test_moses_xml_print_fast(self):
        var = pairPrinterToVariable(
            '-d RF -s en -t sv -m 1 -wm moses -f'.split())
        self.assertEqual(var,
            'Statement of Government Policy by the Prime Minister , '
            'Mr Ingvar Carlsson , at the Opening of the Swedish Parli'
            'ament on Tuesday , 4 October , 1988 .\t'
            'REGERINGSFÖRKLARING .\n')

    def test_moses_raw_write(self):
        OpusRead(
            '-d RF -s en -t sv -m 1 -w test_files/test.src '
            'test_files/test.trg -wm moses -p raw'.split()).printPairs()
        with open('test_files/test.src', 'r') as f:
            self.assertEqual(f.read(),
            'Statement of Government Policy by the Prime Minister, '
            'Mr Ingvar Carlsson, at the Opening of the Swedish Parli'
            'ament on Tuesday, 4 October, 1988.\n')
        with open('test_files/test.trg', 'r') as f:
            self.assertEqual(f.read(), 'REGERINGSFÖRKLARING.\n')

    def test_moses_raw_write_fast(self):
        OpusRead(
            '-d RF -s en -t sv -m 1 -w test_files/test.src '
            'test_files/test.trg -wm moses -p raw -f'.split()).printPairs()
        with open('test_files/test.src', 'r') as f:
            self.assertEqual(f.read(),
            'Statement of Government Policy by the Prime Minister, '
            'Mr Ingvar Carlsson, at the Opening of the Swedish Parli'
            'ament on Tuesday, 4 October, 1988.\n')
        with open('test_files/test.trg', 'r') as f:
            self.assertEqual(f.read(), 'REGERINGSFÖRKLARING.\n')

    def test_moses_raw_print(self):
        var = pairPrinterToVariable(
            '-d RF -s en -t sv -m 1 -wm moses -p raw'.split())
        self.assertEqual(var,
            'Statement of Government Policy by the Prime Minister, '
            'Mr Ingvar Carlsson, at the Opening of the Swedish Parli'
            'ament on Tuesday, 4 October, 1988.\t'
            'REGERINGSFÖRKLARING.\n')

    def test_moses_raw_print_fast(self):
        var = pairPrinterToVariable(
            '-d RF -s en -t sv -m 1 -wm moses -p raw -f'.split())
        self.assertEqual(var,
            'Statement of Government Policy by the Prime Minister, '
            'Mr Ingvar Carlsson, at the Opening of the Swedish Parli'
            'ament on Tuesday, 4 October, 1988.\t'
            'REGERINGSFÖRKLARING.\n')

    def test_moses_parsed_write(self):
        OpusRead(
            '-d RF -s en -t sv -m 1 -w test_files/test.src '
            'test_files/test.trg -wm moses -p parsed -pa -sa upos feats '
            'lemma -ta upos feats lemma'.split()).printPairs()
        with open('test_files/test.src', 'r') as f:
            self.assertEqual(f.read(), 'Statement|NOUN|Number=Sing|st'
            'atement of|ADP|of Government|NOUN|Number=Sing|government'
            ' Policy|NOUN|Number=Sing|policy by|ADP|by the|DET|Definit'
            'e=Def|PronType=Art|the Prime|PROPN|Number=Sing|Prime Min'
            'ister|PROPN|Number=Sing|Minister ,|PUNCT|, Mr|PROPN|Numb'
            'er=Sing|Mr Ingvar|PROPN|Number=Sing|Ingvar Carlsson|PROP'
            'N|Number=Sing|Carlsson ,|PUNCT|, at|ADP|at the|DET|Defin'
            'ite=Def|PronType=Art|the Opening|NOUN|Number=Sing|openin'
            'g of|ADP|of the|DET|Definite=Def|PronType=Art|the Swedis'
            'h|ADJ|Degree=Pos|swedish Parliament|NOUN|Number=Sing|par'
            'liament on|ADP|on Tuesday|PROPN|Number=Sing|Tuesday ,|PU'
            'NCT|, 4|NUM|NumType=Card|4 October|PROPN|Number=Sing|Oct'
            'ober ,|PUNCT|, 1988|NUM|NumType=Card|1988 .|PUNCT|.\n')
        with open('test_files/test.trg', 'r') as f:
            self.assertEqual(f.read(),
            'REGERINGSFÖRKLARING|NOUN|Case=Nom|Definite=Ind|Gender=Ne'
            'ut|Number=Sing|Regeringsförklaring .|PUNCT|.\n')

    def test_moses_parsed_write_fast(self):
        OpusRead(
            '-d RF -s en -t sv -m 1 -w test_files/test.src '
            'test_files/test.trg -wm moses -p parsed -pa -sa upos feats '
            'lemma -ta upos feats lemma -f'.split()).printPairs()
        with open('test_files/test.src', 'r') as f:
            self.assertEqual(f.read(), 'Statement|NOUN|Number=Sing|st'
            'atement of|ADP|of Government|NOUN|Number=Sing|government'
            ' Policy|NOUN|Number=Sing|policy by|ADP|by the|DET|Definit'
            'e=Def|PronType=Art|the Prime|PROPN|Number=Sing|Prime Min'
            'ister|PROPN|Number=Sing|Minister ,|PUNCT|, Mr|PROPN|Numb'
            'er=Sing|Mr Ingvar|PROPN|Number=Sing|Ingvar Carlsson|PROP'
            'N|Number=Sing|Carlsson ,|PUNCT|, at|ADP|at the|DET|Defin'
            'ite=Def|PronType=Art|the Opening|NOUN|Number=Sing|openin'
            'g of|ADP|of the|DET|Definite=Def|PronType=Art|the Swedis'
            'h|ADJ|Degree=Pos|swedish Parliament|NOUN|Number=Sing|par'
            'liament on|ADP|on Tuesday|PROPN|Number=Sing|Tuesday ,|PU'
            'NCT|, 4|NUM|NumType=Card|4 October|PROPN|Number=Sing|Oct'
            'ober ,|PUNCT|, 1988|NUM|NumType=Card|1988 .|PUNCT|.\n')
        with open('test_files/test.trg', 'r') as f:
            self.assertEqual(f.read(),
            'REGERINGSFÖRKLARING|NOUN|Case=Nom|Definite=Ind|Gender=Ne'
            'ut|Number=Sing|Regeringsförklaring .|PUNCT|.\n')

    def test_moses_parsed_print(self):
        var = pairPrinterToVariable(
            '-d RF -s en -t sv -m 1 -wm moses -p parsed -pa -sa upos '
            'feats lemma -ta upos feats lemma'.split())
        self.assertEqual(var,
            'Statement|NOUN|Number=Sing|st'
            'atement of|ADP|of Government|NOUN|Number=Sing|government'
            ' Policy|NOUN|Number=Sing|policy by|ADP|by the|DET|Definit'
            'e=Def|PronType=Art|the Prime|PROPN|Number=Sing|Prime Min'
            'ister|PROPN|Number=Sing|Minister ,|PUNCT|, Mr|PROPN|Numb'
            'er=Sing|Mr Ingvar|PROPN|Number=Sing|Ingvar Carlsson|PROP'
            'N|Number=Sing|Carlsson ,|PUNCT|, at|ADP|at the|DET|Defin'
            'ite=Def|PronType=Art|the Opening|NOUN|Number=Sing|openin'
            'g of|ADP|of the|DET|Definite=Def|PronType=Art|the Swedis'
            'h|ADJ|Degree=Pos|swedish Parliament|NOUN|Number=Sing|par'
            'liament on|ADP|on Tuesday|PROPN|Number=Sing|Tuesday ,|PU'
            'NCT|, 4|NUM|NumType=Card|4 October|PROPN|Number=Sing|Oct'
            'ober ,|PUNCT|, 1988|NUM|NumType=Card|1988 .|PUNCT|.\tREG'
            'ERINGSFÖRKLARING|NOUN|Case=Nom|Definite=Ind|Gender=Ne'
            'ut|Number=Sing|Regeringsförklaring .|PUNCT|.\n')

    def test_moses_parsed_print_fast(self):
        var = pairPrinterToVariable(
            '-d RF -s en -t sv -m 1 -wm moses -p parsed -pa -sa upos '
            'feats lemma -ta upos feats lemma -f'.split())
        self.assertEqual(var,
            'Statement|NOUN|Number=Sing|st'
            'atement of|ADP|of Government|NOUN|Number=Sing|government'
            ' Policy|NOUN|Number=Sing|policy by|ADP|by the|DET|Definit'
            'e=Def|PronType=Art|the Prime|PROPN|Number=Sing|Prime Min'
            'ister|PROPN|Number=Sing|Minister ,|PUNCT|, Mr|PROPN|Numb'
            'er=Sing|Mr Ingvar|PROPN|Number=Sing|Ingvar Carlsson|PROP'
            'N|Number=Sing|Carlsson ,|PUNCT|, at|ADP|at the|DET|Defin'
            'ite=Def|PronType=Art|the Opening|NOUN|Number=Sing|openin'
            'g of|ADP|of the|DET|Definite=Def|PronType=Art|the Swedis'
            'h|ADJ|Degree=Pos|swedish Parliament|NOUN|Number=Sing|par'
            'liament on|ADP|on Tuesday|PROPN|Number=Sing|Tuesday ,|PU'
            'NCT|, 4|NUM|NumType=Card|4 October|PROPN|Number=Sing|Oct'
            'ober ,|PUNCT|, 1988|NUM|NumType=Card|1988 .|PUNCT|.\tREG'
            'ERINGSFÖRKLARING|NOUN|Case=Nom|Definite=Ind|Gender=Ne'
            'ut|Number=Sing|Regeringsförklaring .|PUNCT|.\n')

    def test_links_write(self):
        OpusRead(
            '-d RF -s en -t sv -m 1 -w test_files/test_result '
            '-wm links'.split()).printPairs()
        with open('test_files/test_result', 'r') as f:
            self.assertEqual(f.read(),
                '<?xml version="1.0" encoding="utf-8"?>\n'
                '<!DOCTYPE cesAlign PUBLIC "-//CES//DTD'
                ' XML cesAlign//EN" "">\n<cesAlign version="1.0">\n '
                '<linkGrp targType="s" toDoc="sv/1988.xml.gz"'
                ' fromDoc="en/1988.xml.gz">\n'
                '<link certainty="-0.0636364" xtargets="s1.1;s1.1" id="SL1"'
                ' />\n </linkGrp>\n</cesAlign>')

    def test_links_write_unalphabetical(self):
        OpusRead(
            '-d RF -s sv -t en -m 1 -w test_files/test_result '
            '-wm links -S 1 -T 2'.split()).printPairs()
        with open('test_files/test_result', 'r') as f:
            self.assertEqual(f.read(),
                '<?xml version="1.0" encoding="utf-8"?>\n'
                '<!DOCTYPE cesAlign PUBLIC "-//CES//DTD'
                ' XML cesAlign//EN" "">\n<cesAlign version="1.0">\n '
                '<linkGrp targType="s" toDoc="sv/1988.xml.gz"'
                ' fromDoc="en/1988.xml.gz">\n'
                '<link certainty="0.188136" xtargets="s4.4 s4.5;s4.4" id="SL10"'
                ' />\n </linkGrp>\n</cesAlign>')

    def test_links_print(self):
        var = pairPrinterToVariable(
            '-d RF -s en -t sv -m 1 -wm links'.split())
        self.assertEqual(var,
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<!DOCTYPE cesAlign PUBLIC "-//CES//DTD'
            ' XML cesAlign//EN" "">\n<cesAlign version="1.0">\n '
            '<linkGrp targType="s" toDoc="sv/1988.xml.gz"'
            ' fromDoc="en/1988.xml.gz">\n'
            '<link certainty="-0.0636364" xtargets="s1.1;s1.1" id="SL1"'
            ' />\n </linkGrp>\n</cesAlign>\n')

    def test_links_print_unalphabetical(self):
        var = pairPrinterToVariable(
            '-d RF -s sv -t en -m 1 -wm links -S 1 -T 2'.split())
        self.assertEqual(var,
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<!DOCTYPE cesAlign PUBLIC "-//CES//DTD'
            ' XML cesAlign//EN" "">\n<cesAlign version="1.0">\n '
            '<linkGrp targType="s" toDoc="sv/1988.xml.gz"'
            ' fromDoc="en/1988.xml.gz">\n'
            '<link certainty="0.188136" xtargets="s4.4 s4.5;s4.4" id="SL10"'
            ' />\n </linkGrp>\n</cesAlign>\n')

    def test_iteration_stops_at_the_end_of_the_document_even_if_max_is_not_filled(self):
        var = pairPrinterToVariable(
            '-d RF -s en -t sv -S 2 -T 1 -m 5'.split())
        self.assertEqual(var,
            """\n# en/1988.xml.gz\n# sv/1988.xml.gz\n\n=============="""
            """==================\n(src)="s4.4">The army will be reor"""
            """ganized with the aim of making it more effective .\n("""
            """src)="s4.5">It is the Government 's intention to seek """
            """broad solutions in issues that are of importance for o"""
            """ur national security .\n(trg)="s4.4">Det är regeringe"""
            """ns föresats att söka breda lösningar i frågor som är a"""
            """v betydelse för vår nationella säkerhet .\n=========="""
            """======================\n\n# en/1996.xml.gz\n# sv/1996."""
            """xml.gz\n\n================================\n""")


    def test_use_given_sentence_alignment_file(self):
        OpusRead(
            '-d Books -s en -t fi -S 5 -T 2 -wm links -w '
            'test_files/testlinks'.split()).printPairs()
        var = pairPrinterToVariable(
            '-d Books -s en -t fi -af test_files/testlinks'.split())
        self.assertEqual(var,
            '\n# en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz\n'
            '# fi/Doyle_Arthur_Conan-Hound_of_the_'
            'Baskervilles.xml.gz\n\n================================\n'
            '(src)="s942.0">" So I think .\n(src)="s9'
            '42.1">But if we can only trace L. L. it should clear up the '
            'whole business .\n(src)="s942.2">We h'
            'ave gained that much .\n(src)="s942.3">We know that there is '
            'someone who has the facts if we can '
            'only find her .\n(src)="s942.4">What do you think we should do ?'
            ' "\n(trg)="s942.0">" Niin minäkin ajattelen , mutta jos '
            'voisitte saada tuon L. L : n käsiinne , niin olisi paljon '
            'voitettu , ja onhan edullista jo tietääkin , että on olemassa '
            'joku nainen , joka tuntee asian oikean laidan , jos vaan '
            'voimme saada hänet ilmi .\n(trg)="s942.1">Mitä arvelette nyt '
            'olevan tekeminen ? "\n================================\n')

    def test_use_given_sentence_alignment_file_with_lingGrp_end_tag_on_the_same_line_as_link_tag(self):
        OpusRead(
            '-d RF -s en -t sv -S 2 -T 1 -wm links -w '
            'test_files/testlinks'.split()).printPairs()
        var = pairPrinterToVariable(
            '-d RF -s en -t sv -af test_files/testlinks'.split())
        self.assertEqual(var,
            """\n# en/1988.xml.gz\n# sv/1988.xml.gz\n\n=============="""
            """==================\n(src)="s4.4">The army will be reor"""
            """ganized with the aim of making it more effective .\n("""
            """src)="s4.5">It is the Government 's intention to seek """
            """broad solutions in issues that are of importance for o"""
            """ur national security .\n(trg)="s4.4">Det är regeringe"""
            """ns föresats att söka breda lösningar i frågor som är a"""
            """v betydelse för vår nationella säkerhet .\n=========="""
            """======================\n\n# en/1996.xml.gz\n# sv/1996."""
            """xml.gz\n\n================================\n""")

    def test_use_given_sentence_alignment_file_and_print_links(self):
        OpusRead(
            '-d RF -s en -t sv -m 1 -wm links '
            '-w test_files/testlinks'.split()).printPairs()
        var = pairPrinterToVariable(
            '-d RF -s en -t sv -wm links -af test_files/testlinks'.split())
        self.assertEqual(var, '<?xml version="1.0" encoding="utf-8"?>'
        '\n<!DOCTYPE cesAlign PUBLIC "-//CES//DTD XML cesAlign//EN" "'
        '">\n<cesAlign version="1.0">\n <linkGrp targType="s" toDoc="'
        'sv/1988.xml.gz" fromDoc="en/1988.xml.gz">\n<link certainty="'
        '-0.0636364" xtargets="s1.1;s1.1" id="SL1" />\n </linkGrp>\n<'
        '/cesAlign>\n') 

    def test_use_given_sentence_alignment_file_and_write_links(self):
        OpusRead(
            '-d RF -s en -t sv -m 1 -wm links '
            '-w test_files/testlinks'.split()).printPairs()
        OpusRead(
            '-d RF -s en -t sv -wm links -af test_files/testlinks -w '
            'test_files/testresult'.split()).printPairs()
        with open('test_files/testresult', 'r') as f:
            self.assertEqual(f.read(), '<?xml version="1.0" encoding="utf-8"?>'
            '\n<!DOCTYPE cesAlign PUBLIC "-//CES//DTD XML cesAlign//EN" "'
            '">\n<cesAlign version="1.0">\n <linkGrp targType="s" toDoc="'
            'sv/1988.xml.gz" fromDoc="en/1988.xml.gz">\n<link certainty="'
            '-0.0636364" xtargets="s1.1;s1.1" id="SL1" />\n </linkGrp>\n<'
            '/cesAlign>\n') 

    def test_use_given_sentence_alignment_file_and_print_links_Books(self):
        OpusRead(
            '-d Books -s en -t fi -m 1 -wm links '
            '-w test_files/testlinks'.split()).printPairs()
        var = pairPrinterToVariable(
            '-d Books -s en -t fi -wm links -af test_files/testlinks'.split())
        self.assertEqual(var, '<?xml version="1.0" encoding="utf-8"?>'
        '\n<!DOCTYPE cesAlign PUBLIC "-//CES//DTD XML cesAlign//EN" "'
        '">\n<cesAlign version="1.0">\n<linkGrp targType="s" fromDoc'
        '="en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz" to'
        'Doc="fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz"'
        ' >\n<link xtargets="s1;s1" id="SL1"/>\n </linkGrp>\n<'
        '/cesAlign>\n') 

    def test_use_given_sentence_alignment_file_and_write_links_Books(self):
        OpusRead(
            '-d Books -s en -t fi -m 1 -wm links '
            '-w test_files/testlinks'.split()).printPairs()
        OpusRead(
            '-d Books -s en -t fi -wm links -af test_files/testlinks '
            '-w test_files/testresult'.split()).printPairs()
        with open('test_files/testresult', 'r') as f:
            self.assertEqual(f.read(), '<?xml version="1.0" encoding="utf-8"?>'
            '\n<!DOCTYPE cesAlign PUBLIC "-//CES//DTD XML cesAlign//EN" "'
            '">\n<cesAlign version="1.0">\n<linkGrp targType="s" fromDoc'
            '="en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz" to'
            'Doc="fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz"'
            ' >\n<link xtargets="s1;s1" id="SL1"/>\n </linkGrp>\n<'
            '/cesAlign>\n') 

    def test_checks_first_whether_documents_are_in_path(self):
        with open('test_files/testlinks', 'w') as f:
            f.write(
                '<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE cesAlign '
                'PUBLIC "-//CES//DTD XML cesAlign//EN" "">'
                '\n<cesAlign version="1.0">\n<linkGrp fromDoc="test_files/'
                'test_en" toDoc="test_files/test_fi" >\n<link xtargets='
                '"s1;s1"/>\n </linkGrp>+\n</cesAlign>')
        with open('test_files/test_en', 'w') as f:
            f.write(
                '<?xml version="1.0" encoding="utf-8"?>\n<text>\n'
                '<body>\n<s id="s1">\n <w>test_en1</w>\n <w>test_en2'
                '</w>\n</s>\n </body>\n</text>')
        with open('test_files/test_fi', 'w') as f:
            f.write(
                '<?xml version="1.0" encoding="utf-8"?>\n<text>\n <body>\n'
                '<s id="s1">\n <w>test_fi1</w>\n <w>test_fi2'
                '</w>\n</s>\n </body>\n</text>')
        var = pairPrinterToVariable(
            '-d Books -s en -t fi -af test_files/testlinks'.split())
        self.assertEqual(var,
            '\n# test_files/test_en\n# test_files/test_fi\n\n'
            '================================\n(src)="s1">test_en1 test_en2\n'
            '(trg)="s1">test_fi1 test_fi2'
            '\n================================\n')

    def test_checks_first_whether_documents_are_in_path_gz(self):
        with open('test_files/testlinks', 'w') as f:
            f.write(
                '<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE cesAlign '
                'PUBLIC "-//CES//DTD XML cesAlign//EN" "">'
                '\n<cesAlign version="1.0">\n<linkGrp fromDoc="test_files/'
                'test_en.gz" toDoc="test_files/test_fi.gz" >\n<link '
                'xtargets="s1;s1"/>\n </linkGrp>+\n</cesAlign>')
        with open('test_files/test_en', 'w') as f:
            f.write(
                '<?xml version="1.0" encoding="utf-8"?>\n<text>\n'
                '<body>\n<s id="s1">\n <w>test_en1</w>\n <w>test_en2'
                '</w>\n</s>\n </body>\n</text>')
        with open('test_files/test_fi', 'w') as f:
            f.write(
                '<?xml version="1.0" encoding="utf-8"?>\n<text>\n <body>\n'
                '<s id="s1">\n <w>test_fi1</w>\n <w>test_fi2'
                '</w>\n</s>\n </body>\n</text>')
        with open('test_files/test_en', 'rb') as f:
            with gzip.open('test_files/test_en.gz', 'wb') as gf:
                shutil.copyfileobj(f, gf)
        with open('test_files/test_fi', 'rb') as f:
            with gzip.open('test_files/test_fi.gz', 'wb') as gf:
                shutil.copyfileobj(f, gf)
        var = pairPrinterToVariable(
            '-d Books -s en -t fi -af test_files/testlinks'.split())
        self.assertEqual(var,
            '\n# test_files/test_en.gz\n# test_files/test_fi.gz\n\n'
            '================================\n(src)="s1">test_en1 test_en2\n'
            '(trg)="s1">test_fi1 test_fi2'
            '\n================================\n')

    def test_filtering_by_src_cld2(self):
        var = pairPrinterToVariable(
            '-d RF -s en -t sv -r v1 -m 1 --src_cld2 en 0.98'
            ' -af books_alignment.xml'.split())
        self.assertEqual(var,
            '\n# en/1996.xml.gz\n'
            '# sv/1996.xml.gz\n'
            '\n================================'
            '\n(src)="s5.0">Mr. Sherlock Holmes'
            '\n(trg)="s5.0">Herra Sherlock Holmes'
            '\n================================\n')

    def test_filtering_by_trg_cld2(self):
        var = pairPrinterToVariable(
            '-d RF -s en -t sv -r v1 -m 1 --trg_cld2 ia 0'
            ' -af books_alignment.xml'.split())
        self.assertEqual(var,
            '\n# en/1996.xml.gz\n'
            '# sv/1996.xml.gz\n'
            '\n================================'
            '\n(src)="s4">Chapter 1 Mr. Sherlock Holmes'
            '\n(trg)="s4">Herra Sherlock Holmes .'
            '\n================================\n')

    def test_filtering_by_src_langid(self):
        var = pairPrinterToVariable(
            '-d RF -s en -t sv -r v1 -m 1 --src_langid de 0'
            ' -af books_alignment.xml'.split())
        self.assertEqual(var,
            '\n# en/1996.xml.gz\n'
            '# sv/1996.xml.gz\n'
            '\n================================'
            '\n(src)="s167.0">" Excellent !'
            '\n(trg)="s167.0">" Erinomaista .'
            '\n================================\n')

    def test_filtering_by_trg_langid(self):
        var = pairPrinterToVariable(
            '-d RF -s en -t sv -r v1 -m 1 --trg_langid et 0'
            ' -af books_alignment.xml'.split())
        self.assertEqual(var,
            '\n# en/1996.xml.gz\n'
            '# sv/1996.xml.gz\n'
            '\n================================'
            '\n(src)="s4">Chapter 1 Mr. Sherlock Holmes'
            '\n(trg)="s4">Herra Sherlock Holmes .'
            '\n================================\n')

    def test_filtering_by_lang_labels(self):
        var = pairPrinterToVariable(
            '-d RF -s en -t sv -r v1 -m 1 --src_cld2 un 0 --trg_cld2 '
            'fi 0.97 --src_langid en 0.17 --trg_langid fi 1'
            ' -af books_alignment.xml'.split())
        self.assertEqual(var,
            '\n# en/1996.xml.gz\n'
            '# sv/1996.xml.gz\n'
            '\n================================'
            '\n(src)="s8.1">I believe'
            '\n(trg)="s8.1">Luulenpa että sinulla'
            '\n================================\n')

    def test_filtering_by_lang_labels_fast(self):
        var = pairPrinterToVariable(
            '-d RF -s en -t sv -r v1 -m 1 --src_cld2 un 0 --trg_cld2 '
            'fi 0.97 --src_langid en 0.17 --trg_langid fi 1 -f'
            ' -af books_alignment.xml'.split())
        self.assertEqual(var,
            '\n# en/1996.xml.gz\n'
            '# sv/1996.xml.gz\n'
            '\n================================'
            '\n(src)="s8.1">I believe'
            '\n(trg)="s8.1">Luulenpa että sinulla'
            '\n================================\n')

    def test_filtering_by_lang_labels_nonalphabetical_lang_order(self):
        var = pairPrinterToVariable(
            '-d RF -s sv -t en -r v1 -m 1 --trg_cld2 un 0 --src_cld2 '
            'fi 0.97 --trg_langid en 0.17 --src_langid fi 1'
            ' -af books_alignment.xml'.split())
        self.assertEqual(var,
            '\n# en/1996.xml.gz\n'
            '# sv/1996.xml.gz\n'
            '\n================================'
            '\n(src)="s8.1">Luulenpa että sinulla'
            '\n(trg)="s8.1">I believe'
            '\n================================\n')

    def test_filtering_by_lang_labels_nonalphabetical_lang_order_fast(self):
        var = pairPrinterToVariable(
            '-d RF -s sv -t en -r v1 -m 1 --trg_cld2 un 0 --src_cld2 '
            'fi 0.97 --trg_langid en 0.17 --src_langid fi 1 -f'
            ' -af books_alignment.xml'.split())
        self.assertEqual(var,
            '\n# en/1996.xml.gz\n'
            '# sv/1996.xml.gz\n'
            '\n================================'
            '\n(src)="s8.1">Luulenpa että sinulla'
            '\n(trg)="s8.1">I believe'
            '\n================================\n')

    def test_filtering_by_lang_labels_no_matches_found(self):
        var = pairPrinterToVariable(
            '-d RF -s en -t sv -r v1 -m 1 --src_cld2 fi 2'
            ' -af books_alignment.xml'.split())
        self.assertEqual(var,
            '\n# en/1996.xml.gz\n'
            '# sv/1996.xml.gz\n'
            '\n================================\n')

    def test_filtering_by_lang_labels_no_matches_found_fast(self):
        var = pairPrinterToVariable(
            '-d RF -s en -t sv -r v1 -m 1 --src_cld2 fi 2'
            ' -af books_alignment.xml -f'.split())
        self.assertEqual(var,
            '\n# en/1996.xml.gz\n'
            '# sv/1996.xml.gz\n'
            '\n================================\n')

    def test_filtering_by_src_cld2_print_links(self):
        var = pairPrinterToVariable(
            '-d RF -s en -t sv -r v1 -m 1 --src_cld2 en 0.98'
            ' -af books_alignment.xml -wm links'.split())
        self.assertEqual(var,
            '<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE cesAli'
            'gn PUBLIC "-//CES//DTD XML cesAlign//EN" "">\n<cesAlign '
            'version="1.0">\n'
            '<linkGrp targType="s" fromDoc="en/1996.xml.gz" toDoc="sv'
            '/1996.xml.gz" >\n<link xtargets="s5.0;s5.0" id="SL5.0"/>'
            '\n </linkGrp>\n</cesAlign>\n')

    def test_filtering_by_lang_labels_print_links(self):
        var = pairPrinterToVariable(
            '-d RF -s en -t sv -r v1 -m 1 --src_cld2 un 0 --trg_cld2 '
            'fi 0.97 --src_langid en 0.17 --trg_langid fi 1'
            ' -af books_alignment.xml -wm links'.split())
        self.assertEqual(var,
            '<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE cesAli'
            'gn PUBLIC "-//CES//DTD XML cesAlign//EN" "">\n<cesAlign '
            'version="1.0">\n'
            '<linkGrp targType="s" fromDoc="en/1996.xml.gz" toDoc="sv'
            '/1996.xml.gz" >\n<link xtargets="s8.1;s8.1" id="SL8.1"/>'
            '\n </linkGrp>\n</cesAlign>\n')

    def test_filtering_by_lang_labels_write_links(self):
        OpusRead(
            '-d RF -s en -t sv -r v1 -m 1 --src_cld2 un 0 --trg_cld2 '
            'fi 0.97 --src_langid en 0.17 --trg_langid fi 1'
            ' -af books_alignment.xml -wm links '
            '-w test_files/result'.split()).printPairs()
        with open('test_files/result', 'r') as f:
            self.assertEqual(f.read(),
                '<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE cesAli'
                'gn PUBLIC "-//CES//DTD XML cesAlign//EN" "">\n<cesAlign '
                'version="1.0">\n'
                '<linkGrp targType="s" fromDoc="en/1996.xml.gz" toDoc="sv'
                '/1996.xml.gz" >\n<link xtargets="s8.1;s8.1" id="SL8.1"/>'
                '\n </linkGrp>\n</cesAlign>')

    def test_use_given_zip_files(self):
        var = pairPrinterToVariable(
            '-d RF -s en -t sv -m1 -sz en.zip -tz sv.zip'
            ' -af books_alignment.xml'.split())
        self.assertEqual(var,
            '\n# en/1996.xml.gz'
            '\n# sv/1996.xml.gz'
            '\n\n================================'
            '\n(src)="s1">Source : manybooks.netAudiobook available here'
            '\n(trg)="s1">Source : Project Gutenberg'
            '\n================================\n')

    def test_use_given_zip_files_unalphabetical(self):
        var = pairPrinterToVariable(
            '-d RF -s sv -t en -m1 -sz sv.zip -tz en.zip'
            ' -af books_alignment.xml'.split())
        self.assertEqual(var,
            '\n# en/1996.xml.gz'
            '\n# sv/1996.xml.gz'
            '\n\n================================'
            '\n(src)="s1">Source : Project Gutenberg'
            '\n(trg)="s1">Source : manybooks.netAudiobook available here'
            '\n================================\n')

    def test_source_zip_given_and_target_automatic(self):
        opr = OpusRead('-d RF -s en -t sv -sz en.zip'.split())
        opr.par.initializeSentenceParsers(
            {'fromDoc': 'en/1996.xml.gz', 'toDoc': 'sv/1996.xml.gz'})
        self.assertEqual(opr.par.sourcezip.filename,
            'en.zip')
        self.assertEqual(opr.par.targetzip.filename,
            '/proj/nlpl/data/OPUS/RF/latest/xml/sv.zip')

    def test_source_zip_given_and_target_automatic_unalphabetical(self):
        opr = OpusRead('-d RF -s sv -t en -sz sv.zip'.split())
        opr.par.initializeSentenceParsers(
            {'fromDoc': 'en/1996.xml.gz', 'toDoc': 'sv/1996.xml.gz'})
        self.assertEqual(opr.par.sourcezip.filename,
            '/proj/nlpl/data/OPUS/RF/latest/xml/en.zip')
        self.assertEqual(opr.par.targetzip.filename,
            'sv.zip')

    def test_target_zip_given_and_source_automatic(self):
        opr = OpusRead('-d RF -s en -t sv -tz sv.zip'.split())
        opr.par.initializeSentenceParsers(
            {'fromDoc': 'en/1996.xml.gz', 'toDoc': 'sv/1996.xml.gz'})
        self.assertEqual(opr.par.sourcezip.filename,
            '/proj/nlpl/data/OPUS/RF/latest/xml/en.zip')
        self.assertEqual(opr.par.targetzip.filename,
            'sv.zip')

    def test_target_zip_given_and_source_local(self):
        opr = OpusRead('-d RF -s en -t sv -r v1 -tz sv.zip'.split())
        opr.par.initializeSentenceParsers(
            {'fromDoc': 'en/1996.xml.gz', 'toDoc': 'sv/1996.xml.gz'})
        self.assertEqual(opr.par.sourcezip.filename,
            'RF_v1_xml_en.zip')
        self.assertEqual(opr.par.targetzip.filename,
            'sv.zip')

    def test_target_zip_given_and_source_local_unalphabetical(self):
        opr = OpusRead('-d RF -s sv -t en -r v1 -tz en.zip'.split())
        opr.par.initializeSentenceParsers(
            {'fromDoc': 'en/1996.xml.gz', 'toDoc': 'sv/1996.xml.gz'})
        self.assertEqual(opr.par.sourcezip.filename,
            'en.zip')
        self.assertEqual(opr.par.targetzip.filename,
            'RF_v1_xml_sv.zip')

    def test_source_zip_given_and_target_local(self):
        opr = OpusRead('-d RF -s en -t sv -r v1 -sz en.zip'.split())
        opr.par.initializeSentenceParsers(
            {'fromDoc': 'en/1996.xml.gz', 'toDoc': 'sv/1996.xml.gz'})
        self.assertEqual(opr.par.sourcezip.filename,
            'en.zip')
        self.assertEqual(opr.par.targetzip.filename,
            'RF_v1_xml_sv.zip')

    def test_source_zip_local_and_target_automatic(self):
        opr = OpusRead('-d RF -s en -t es -r v1'.split())
        opr.par.initializeSentenceParsers(
            {'fromDoc': 'en/1996.xml.gz', 'toDoc': 'es/1996.xml.gz'})
        self.assertEqual(opr.par.sourcezip.filename,
            'RF_v1_xml_en.zip')
        self.assertEqual(opr.par.targetzip.filename,
            '/proj/nlpl/data/OPUS/RF/v1/xml/es.zip')

    def test_source_zip_local_and_target_automatic_unalphabetical(self):
        opr = OpusRead('-d RF -s sv -t es -r v1'.split())
        opr.par.initializeSentenceParsers(
            {'fromDoc': 'es/1996.xml.gz', 'toDoc': 'sv/1996.xml.gz'})
        self.assertEqual(opr.par.sourcezip.filename,
            '/proj/nlpl/data/OPUS/RF/v1/xml/es.zip')
        self.assertEqual(opr.par.targetzip.filename,
            'RF_v1_xml_sv.zip')

    def test_target_zip_local_and_source_automatic(self):
        opr = OpusRead('-d RF -s es -t sv -r v1'.split())
        opr.par.initializeSentenceParsers(
            {'fromDoc': 'es/1996.xml.gz', 'toDoc': 'sv/1996.xml.gz'})
        self.assertEqual(opr.par.sourcezip.filename,
            '/proj/nlpl/data/OPUS/RF/v1/xml/es.zip')
        self.assertEqual(opr.par.targetzip.filename,
            'RF_v1_xml_sv.zip')

    def test_empty_argument_list(self):
        temp_args = sys.argv.copy()
        sys.argv = [temp_args[0]] + '-d RF -s en -t sv -m 1 -f'.split()
        var = pairPrinterToVariable([])
        self.assertEqual(var,
            '\n# en/1988.xml.gz\n# sv/1988.xml.gz\n\n================'
            '================\n(src)="s1.1">Statement of Government P'
            'olicy by the Prime Minister , Mr Ingvar Carlsson , at th'
            'e Opening of the Swedish Parliament on Tuesday , 4 Octob'
            'er , 1988 .\n(trg)="s1.1">REGERINGSFÖRKLARING .\n======='
            '=========================\n')
        sys.argv = temp_args.copy()

    @mock.patch('opustools_pkg.opus_get.input', create=True)
    def test_alignment_file_not_found(self, mocked_input):
        mocked_input.side_effect = ['y', 'n']
        opr = OpusRead(
            '-d RF -s en -t sv -m 1 -af unfound.xml.gz'.split())
        opr.printPairs()
        os.remove('RF_latest_xml_en-sv.xml.gz')
        os.remove('RF_latest_xml_en.zip')
        os.remove('RF_latest_xml_sv.zip')
        var = pairPrinterToVariable(
            '-d RF -s en -t sv -m 1 -af unfound.xml.gz'.split())
        self.assertEqual(var[-18:], '128 KB Total size\n') 

    @mock.patch('opustools_pkg.opus_get.input', create=True)
    def test_zip_file_not_found(self, mocked_input):
        mocked_input.side_effect = ['y']
        opr = OpusRead('-d RF -s en -t sv -m 1'.split())
        opr.par.source = ''

        old_stdout = sys.stdout
        printout = io.StringIO()
        sys.stdout = printout
        opr.printPairs()
        sys.stdout = old_stdout

        os.remove('RF_latest_xml_en-sv.xml.gz')
        os.remove('RF_latest_xml_en.zip')
        os.remove('RF_latest_xml_sv.zip')
        
        self.assertEqual(printout.getvalue()[-230:],
            '(src)="s1.1">S'
            'tatement of Government Policy by the Prime Minister , Mr'
            ' Ingvar Carlsson , at the Opening of the Swedish Parliame'
            'nt on Tuesday , 4 October , 1988 .\n(trg)="s1.1">REGERIN'
            'GSFÖRKLARING .\n================================\n')

    def test_testConfidence_with_empty_attrsList(self):
        self.assertFalse(self.opr.par.testConfidence('', [], ''))

    def test_id_file_printing(self):
        OpusRead('-d RF -s en -t sv -m 1 -a certainty -tr 1 '
            '-id test_files/test.id'.split()).printPairs()
        with open('test_files/test.id') as id_file:
            self.assertEqual(id_file.read(), 'en/1988.xml.gz\tsv/1988'
                '.xml.gz\ts3.2\ts3.2\t1.14214\n')

    def test_id_file_printing_unalphabetical(self):
        OpusRead('-d RF -s sv -t en -m 1 -S 1 -T 2 -a certainty -tr 0.1 '
            '-id test_files/test.id'.split()).printPairs()
        with open('test_files/test.id') as id_file:
            self.assertEqual(id_file.read(), 'sv/1988.xml.gz\ten/1988'
                '.xml.gz\ts4.4\ts4.4 s4.5\t0.188136\n')

    def test_pair_output_sending_with_single_output_file(self):
        self.opr.args.wm = 'moses'
        self.opr.args.w = ['test_files/moses.txt']
        self.opr.resultfile = open(self.opr.args.w[0], 'w')
        wpair = ('sentence 1\tsentence 2\n', '')
        self.opr.sendPairOutput(wpair)
        self.opr.resultfile.close()
        with open('test_files/moses.txt') as mosesf:
            self.assertEqual(mosesf.read(), 'sentence 1\tsentence 2\n')
        
    def test_pair_output_sending_with_two_output_files(self):
        self.opr.args.wm = 'moses'
        self.opr.args.w = ['test_files/moses.src', 'test_files/moses.trg']
        self.opr.mosessrc = open(self.opr.args.w[0], 'w')
        self.opr.mosestrg = open(self.opr.args.w[1], 'w')
        wpair = ('sentence 1\t', 'sentence 2\n')
        self.opr.sendPairOutput(wpair)
        self.opr.mosessrc.close()
        self.opr.mosestrg.close()
        with open('test_files/moses.src') as mosessrc:
            self.assertEqual(mosessrc.read(), 'sentence 1\t')
        with open('test_files/moses.trg') as mosestrg:
            self.assertEqual(mosestrg.read(), 'sentence 2\n')

    def test_writing_id_file_line(self):
        self.opr.id_file = open('test_files/id_file', 'w')
        id_details = ('file_name1', 'file_name2',
            ['id1', 'id2'], ['id1'], 'value')
        self.opr.sendIdOutput(id_details)
        self.opr.id_file.close()
        with open('test_files/id_file') as id_file:
            self.assertEqual(id_file.read(),
                'file_name1\tfile_name2\tid1 id2\tid1\tvalue\n')

class TestOpusCat(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.maxDiff = None

    def printSentencesToVariable(self, arguments):
        old_stdout = sys.stdout
        printout = io.StringIO()
        sys.stdout = printout
        oprinter = OpusCat(arguments)
        oprinter.printSentences()
        sys.stdout = old_stdout
        return printout.getvalue()

    def test_printing_sentences(self):
        var  = self.printSentencesToVariable('-d RF -l en -p'.split())
        self.assertEqual(var[-183:],
            """("s72.1")>It is the Government 's resposibility and ai"""
            """m to put to use all good initiatives , to work for bro"""
            """ad solutions and to pursue a policy in the interests o"""
            """f the whole nation .\n""")

    def test_printing_sentences_with_limit(self):
        var = self.printSentencesToVariable('-d RF -l en -m 1 -p'.split())
        self.assertEqual(var,
            '\n# RF/xml/en/1996.xml\n\n("s1.1")>MINISTRY FOR FOREIGN'
            ' AFFAIRS Press Section Check against delivery\n')

    def test_printing_sentences_without_ids(self):
        var = self.printSentencesToVariable(
            '-d RF -l en -m 1 -i -p'.split())
        self.assertEqual(var,
            '\n# RF/xml/en/1996.xml\n\nMINISTRY FOR FOREIGN'
            ' AFFAIRS Press Section Check against delivery\n')

    def test_print_annotations(self):
        var = self.printSentencesToVariable(
            '-d RF -l en -m 1 -i -p -pa'.split())
        self.assertEqual(var,
            '\n# RF/xml/en/1996.xml\n\nMINISTRY|NNP|ministry FOR|NNP'
            '|for FOREIGN|NNP|FOREIGN AFFAIRS|NNP Press|NNP|Press Sec'
            'tion|NNP|Section Check|NNP|Check against|IN|against deli'
            'very|NN|delivery\n')

    def test_print_annotations_all_attributes(self):
        var = self.printSentencesToVariable(
            '-d RF -l en -m 1 -i -p -pa -sa all_attrs'.split())
        self.assertEqual(var,
            '\n# RF/xml/en/1996.xml\n\nMINISTRY|null|0|NN|w1.1.1|mini'
            'stry|NNP|NN FOR|prep|1|IN|w1.1.2|for|NNP|IN FOREIGN|nn|7'
            '|NNP|w1.1.3|FOREIGN|NNP|NP AFFAIRS|nn|7|NNP|w1.1.4|NNP|N'
            'P Press|nn|7|NNP|w1.1.5|Press|NNP|NP Section|nn|7|NNP|w1'
            '.1.6|Section|NNP|NP Check|pobj|2|NNP|w1.1.7|Check|NNP|NP'
            ' against|prep|1|IN|w1.1.8|against|IN|IN delivery|pobj|8|N'
            'N|w1.1.9|delivery|NN|NN\n')

    def test_print_xml(self):
        var = self.printSentencesToVariable('-d RF -l en -m 1'.split())
        self.assertEqual(var[-38:],
            '<w id="w2.10">1996</w>\n</p><p id="3">\n')

    def test_printing_specific_file(self):
        var = self.printSentencesToVariable(
            '-d RF -l en -m 1 -i -p -f RF/xml/en/1988.xml'.split())
        self.assertEqual(var,
            '\n# RF/xml/en/1988.xml\n\nStatement of Government Policy'
            ' by the Prime Minister , Mr Ingvar Carlsson , at the Open'
            'ing of the Swedish Parliament on Tuesday , 4 October , 1'
            '988 .\n')

    def test_empty_argument_list(self):
        temp_args = sys.argv.copy()
        sys.argv = [temp_args[0]] + '-d RF -l en -m 1 -p'.split()
        var = self.printSentencesToVariable([])
        self.assertEqual(var,
            '\n# RF/xml/en/1996.xml\n\n("s1.1")>MINISTRY FOR FOREIGN '
            'AFFAIRS Press Section Check against delivery\n')
        sys.argv = temp_args.copy()

    @mock.patch('opustools_pkg.opus_get.input', create=True)
    def test_file_not_found(self, mocked_input):
        mocked_input.side_effect = ['y']
        var = self.printSentencesToVariable('-d RFOSIAJ -l en -m 1 -p'.split())

        self.assertEqual(var[-28:],
            '\nNecessary files not found.\n')

    @mock.patch('opustools_pkg.opus_get.input', create=True)
    def test_download_necessary_files(self, mocked_input):
        mocked_input.side_effect = ['y', 'n']

        old_stdout = sys.stdout
        printout = io.StringIO()
        sys.stdout = printout
        OpusCat.openFiles(OpusCat('-d RF -l en'.split()),
            'RF_latest_xml_en.zip', '')
        os.remove('RF_latest_xml_en.zip')
        OpusCat.openFiles(OpusCat('-d RF -l en'.split()),
            'RF_latest_xml_en.zip', '')
        sys.stdout = old_stdout
        
        self.assertEqual(printout.getvalue()[-161:-132],
           'No file found with parameters')

class TestOpusGet(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.maxDiff = None

    def test_empty_argument_list(self):
        temp_args = sys.argv.copy()
        sys.argv = [temp_args[0]] + '-s eo'.split()
        opg = OpusGet([])
        self.assertEqual(opg.url, 'http://opus.nlpl.eu/opusapi/?source=eo&')
        sys.argv = temp_args.copy()

    def test_format_size(self):
        opg = OpusGet('-s eo'.split())
        self.assertEqual(opg.format_size(1), '1 KB')
        self.assertEqual(opg.format_size(291), '291 KB')
        self.assertEqual(opg.format_size(1000), '1 MB')
        self.assertEqual(opg.format_size(2514), '3 MB')
        self.assertEqual(opg.format_size(1000000), '1 GB')
        self.assertEqual(opg.format_size(3385993), '3 GB')
        self.assertEqual(opg.format_size(1000000000), '1 TB')
        self.assertEqual(opg.format_size(2304006273), '2 TB')

    def test_remove_data_with_no_alignment_if_needed(self):
        opg = OpusGet('-s en -t sv -l'.split())
        self.assertEqual(opg.get_corpora_data()[2], '247 GB')

    def test_get_files_invalid_url(self):
        opg = OpusGet('-d RF -s en -t sv -l'.split())
        opg.url = 'http://slkdfjlks'
        old_stdout = sys.stdout
        printout = io.StringIO()
        sys.stdout = printout
        opg.get_files()
        sys.stdout = old_stdout

        self.assertEqual(printout.getvalue(), 'Unable to retrieve the data.\n')

    @mock.patch('opustools_pkg.opus_get.input', create=True)
    def test_download_invalid_url(self, mocked_input):
        mocked_input.side_effect = ['y']
        opg = OpusGet('-d RF -s en -t sv -l'.split())
        corpora, file_n, total_size = opg.get_corpora_data()
        corpora[0]['url'] = 'http://alskdjfl'
        old_stdout = sys.stdout
        printout = io.StringIO()
        sys.stdout = printout
        opg.download(corpora, file_n, total_size)
        sys.stdout = old_stdout

        self.assertEqual(printout.getvalue(), 'Unable to retrieve the data.\n')

if __name__ == '__main__':
    unittest.main()

