import os
import unittest
import io
import sys
import xml.parsers.expat
import gzip
import shutil
import zipfile

from opustools_pkg import OpusRead, OpusCat

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
        try:
            os.mkdir('test_files')
        except FileExistsError:
            pass

        try:
            os.mkdir('Books')
            os.mkdir('Books/xml')
            os.mkdir('Books/xml/en')
            with open(('Books/xml/en/Doyle_Arthur_Conan-Hound_of_the_'
                    'Baskervilles.xml'), 'w') as f:
                f.write(('<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<text>'
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
                '</body>\n</text>\n'))

            with zipfile.ZipFile('Books_v1_xml_en.zip', 'w') as zf:
                zf.write(('Books/xml/en/Doyle_Arthur_Conan-Hound_of_the_'
                    'Baskervilles.xml'))

            os.mkdir('Books/xml/fi')
            with open(('Books/xml/fi/Doyle_Arthur_Conan-Hound_of_the_'
                    'Baskervilles.xml'), 'w') as f:
                f.write(('<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<text'
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
                '</s></p>\n </body>\n</text>\n'))

            with zipfile.ZipFile('Books_v1_xml_fi.zip', 'w') as zf:
                zf.write(('Books/xml/fi/Doyle_Arthur_Conan-Hound_of_the_'
                    'Baskervilles.xml'))

            shutil.copyfile('Books_v1_xml_en.zip', 'en.zip')
            shutil.copyfile('Books_v1_xml_fi.zip', 'fi.zip')

        except FileExistsError:
            pass

        with open('books_alignment.xml', 'w') as f:
            f.write(('<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE '
            'cesAlign PUBLIC "-//CES//DTD XML cesAlign//EN" "">\n<cesAlign '
            'version="1.0">\n<linkGrp targType="s" fromDoc="en/'
            'Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz" '
            'toDoc="fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz" '
            '>\n<link xtargets="s1;s1" id="SL1"/>\n<link xtargets="s4;s4" '
            'id="SL4"/>\n<link xtargets="s5.0;s5.0" id="SL5.0"/>\n<link '
            'xtargets="s8.1;s8.1" id="SL8.1"/>\n<link xtargets="s167.0'
            ';s167.0" id="SL167.0"/>\n  </linkGrp>\n</cesAlign>\n'))

        self.opr = OpusRead('-d Books -s en -t fi'.split())
        self.opr.par.initializeSentenceParsers(
            {'fromDoc':
                'en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz',
             'toDoc':
                'fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz'})
        self.fastopr = OpusRead('-d Books -s en -t fi -f'.split())
        self.fastopr.par.initializeSentenceParsers(
            {'fromDoc':
                'en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz',
             'toDoc':
                'fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz'})

        self.maxDiff= None
    @classmethod
    def tearDownClass(self):
        self.opr.par.sPar.document.close()
        self.opr.par.tPar.document.close()
        self.opr.par.closeFiles()
        self.fastopr.par.sPar.document.close()
        self.fastopr.par.tPar.document.close()
        self.fastopr.par.closeFiles()

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
        self.assertEqual(len(self.opr.par.sPar.sentences), 3831)
        self.assertEqual(len(self.opr.par.tPar.sentences), 3757)

    def test_ExhaustiveSentenceParser_getSentence(self):
        self.assertEqual(self.opr.par.sPar.getSentence('s1')[0],
            'Source : manybooks.netAudiobook available here')
        self.assertEqual(self.opr.par.tPar.getSentence('s1')[0],
            'Source : Project Gutenberg')

        self.assertEqual(self.opr.par.sPar.getSentence('s4')[0],
            'Chapter 1 Mr. Sherlock Holmes')
        self.assertEqual(self.opr.par.tPar.getSentence('s4')[0],
            'Herra Sherlock Holmes .')

        self.assertEqual(self.opr.par.sPar.getSentence('s5.4')[0],
            ('" To James Mortimer , M.R.C.S. , from his friends of the'
            ' C.C.H. , " was engraved upon it , with the date " 1884 . "'))
        self.assertEqual(self.opr.par.tPar.getSentence('s5.5')[0],
            ("James Mortimerille ystäviltänsä C. C. H : ssa ' oli"
            " kaiverrettu tuuman-levyiselle , kädensijan alapuolella"
            " olevalle hopealevylle , sekä vielä vuosiluku 1884 ."))

    def test_ExhaustiveSentenceParser_readSentence_format(self):
        self.assertEqual(self.opr.par.sPar.readSentence(['s1'])[0],
            '(src)="s1">Source : manybooks.netAudiobook available here')
        self.assertEqual(self.opr.par.tPar.readSentence(['s1'])[0],
            '(trg)="s1">Source : Project Gutenberg')
        self.assertEqual(self.opr.par.sPar.readSentence(['s11.0', 's11.1'])[0],
            ('(src)="s11.0">" Good ! " said Holmes .\n'
            '(src)="s11.1">" Excellent ! "'))

    def test_ExhaustiveSentenceParser_readSentence_moses(self):
        self.opr.par.sPar.wmode = 'moses'
        self.assertEqual(self.opr.par.sPar.readSentence(['s5.2'])[0],
            ('It was a fine , thick piece of wood , bulbous-headed ,'
            ' of the sort which is known as a " Penang lawyer . "'))

    def test_ExhaustiveSentenceParser_readSentence_tmx(self):
        self.opr.par.sPar.wmode = 'tmx'
        self.assertEqual(self.opr.par.sPar.readSentence(['s5.2'])[0],
            ('\t\t<tu>\n\t\t\t<tuv xml:lang="en"><seg>It was a fine ,'
            ' thick piece of wood , bulbous-headed , of the sort which '
            'is known as a " Penang lawyer . "</seg></tuv>'))
        self.opr.par.tPar.wmode = 'tmx'
        self.assertEqual(self.opr.par.tPar.readSentence(['s5.2', 's5.3'])[0],
            ("""\t\t\t<tuv xml:lang="fi"><seg>Se oli jokseenkin soma ja """
            """tukeva , se oli varustettu sipulinmuotoisella kädensijalla """
            """ja näytti oikealta " tuomarin sauvalta . " ' M.R.C.S.</seg>"""
            """</tuv>\n\t\t</tu>"""))

    def test_ExhaustiveSentenceParser_readSentence_empty(self):
        self.assertEqual(self.opr.par.sPar.readSentence([''])[0], '')

    def test_SentenceParser_readSentence_format(self):
        self.assertEqual(self.fastopr.par.sPar.readSentence(['s1'])[0],
            '(src)="s1">Source : manybooks.netAudiobook available here')
        self.assertEqual(self.fastopr.par.tPar.readSentence(['s1'])[0],
            '(trg)="s1">Source : Project Gutenberg')
        self.assertEqual(self.fastopr.par.sPar.readSentence(
            ['s11.0', 's11.1'])[0],
            ('(src)="s11.0">" Good ! " said Holmes .\n'
            '(src)="s11.1">" Excellent ! "'))

    def test_SentenceParser_readSentence_moses(self):
        self.fastopr.par.sPar.wmode = 'moses'
        self.assertEqual(self.fastopr.par.sPar.readSentence(['s12'])[0],
            ('" I think also that the probability is in favour of'
            ' his being a country practitioner who does a great deal '
            'of his visiting on foot . "'))

    def test_SentenceParser_readSentence_tmx(self):
        self.fastopr.par.sPar.wmode = 'tmx'
        self.fastopr.par.tPar.wmode = 'tmx'
        self.assertEqual(self.fastopr.par.sPar.readSentence(['s16.0'])[0],
            ("""\t\t<tu>\n\t\t\t<tuv xml:lang="en"><seg>" And"""
            """ then again , there is the ' friends of the C.C.H. '"""
            """</seg></tuv>"""))
        self.assertEqual(self.fastopr.par.tPar.readSentence(
            ['s16.1', 's16.2'])[0],
            ("""\t\t\t<tuv xml:lang="fi"><seg>Minä otaksun , että H """
            """tarkoittaa jotain hevosurheiluseuraa . Ehkäpä hän """
            """kirurgina oli tehnyt palveluksia paikallisen urheiluseuran """
            """jäsenille , ja nämä ovat kiitollisuutensa osoitteeksi """
            """antaneet tämän pienen lahjan . "</seg></tuv>\n\t\t</tu>"""))

    def test_SentenceParser_readSentence_empty(self):
        self.assertEqual(self.fastopr.par.sPar.readSentence([''])[0], '')

    def test_AlignmentParser_readPair_returns_1_if_tag_is_not_link_and_write_mode_is_links(self):
        self.opr.par.args.wm='links'
        self.opr.par.parseLine('<s>')
        ret = self.opr.par.readPair()
        self.assertEqual(ret, 1)

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
            ('(src)="s4">Chapter 1 Mr. Sherlock Holmes\n(trg)="s4">Herra '
            'Sherlock Holmes .\n================================'))

    def test_PairPrinter_printPair_tmx(self):
        self.opr.par.args.wm = 'tmx'
        sPair = (('\t\t<tu>\n\t\t\t<tuv xml:lang="en"><seg>Chapter 1 Mr. '
                'Sherlock Holmes</seg></tuv>', '\t\t\t<tuv xml:lang="fi">'
                '<seg>Herra Sherlock Holmes .</seg></tuv>\n\t\t</tu>'))
        self.assertEqual(self.opr.printPair(sPair),
            ('\t\t<tu>\n\t\t\t<tuv xml:lang="en"><seg>Chapter 1 Mr. Sherlock'
            ' Holmes</seg></tuv>\n\t\t\t<tuv xml:lang="fi"><seg>Herra '
            'Sherlock Holmes .</seg></tuv>\n\t\t</tu>'))

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
            ('(src)="3">Director PARK Jae-sik\n\n'
            '================================'))

    def test_PairPrinter_writePair_normal(self):
        sPair = ('(src)="s4">Chapter 1 Mr. Sherlock Holmes',
                '(trg)="s4">Herra Sherlock Holmes .')
        self.assertEqual(self.opr.writePair(sPair),
            (('(src)="s4">Chapter 1 Mr. Sherlock Holmes\n(trg)="s4">Herra '
            'Sherlock Holmes .\n================================\n'), ''))

    def test_PairPrinter_writePair_tmx(self):
        self.opr.par.args.wm = 'tmx'
        sPair = (('\t\t<tu>\n\t\t\t<tuv xml:lang="en"><seg>Chapter 1 Mr. '
                'Sherlock Holmes</seg></tuv>'),
                ('\t\t\t<tuv xml:lang="fi"><seg>Herra Sherlock Holmes .'
                '</seg></tuv>\n\t\t</tu>'))
        self.assertEqual(self.opr.writePair(sPair),
            (('\t\t<tu>\n\t\t\t<tuv xml:lang="en"><seg>Chapter 1 Mr. Sherlock'
            ' Holmes</seg></tuv>\n\t\t\t<tuv xml:lang="fi"><seg>Herra '
            'Sherlock Holmes .</seg></tuv>\n\t\t</tu>\n'), ''))

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
            (('(src)="3">Director PARK Jae-sik\n\n'
            '================================\n'), ''))


    def test_switch_labels_when_languages_are_in_unalphabetical_order(self):
        opr = OpusRead('-d Books -s fi -t en'.split())
        opr.par.initializeSentenceParsers(
            {'fromDoc':
                'en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz',
             'toDoc':
                'fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz'})
        self.assertEqual(opr.par.sPar.readSentence(['s1'])[0],
            '(trg)="s1">Source : manybooks.netAudiobook available here')
        self.assertEqual(opr.par.tPar.readSentence(['s1'])[0],
            '(src)="s1">Source : Project Gutenberg')
        opr.par.closeFiles()
        fastopr = OpusRead('-d Books -s fi -t en -f'.split())
        fastopr.par.initializeSentenceParsers(
            {'fromDoc':
                'en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz',
             'toDoc':
                'fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz'})
        self.assertEqual(fastopr.par.sPar.readSentence(['s1'])[0],
            '(trg)="s1">Source : manybooks.netAudiobook available here')
        self.assertEqual(fastopr.par.tPar.readSentence(['s1'])[0],
            '(src)="s1">Source : Project Gutenberg')
        fastopr.par.closeFiles()

    def test_ExhaustiveSentenceParser_readSentence_annotations(self):
        opr = OpusRead('-d Books -s en -t eo -pa'.split())
        opr.par.initializeSentenceParsers(
            {'fromDoc':
                'en/Carroll_Lewis-Alice_in_wonderland.xml.gz',
             'toDoc':
                'eo/Carroll_Lewis-Alice_in_wonderland.xml.gz'})
        self.assertEqual(opr.par.sPar.readSentence(['s4'])[0],
            ('(src)="s4">CHAPTER|NN|chapter I|PRP|I Down|VBP|down'
            ' the|DT|the Rabbit-Hole|NNP'))
        opr.par.closeFiles()
        opr = OpusRead( '-d Books -s en -t eo -pa -ca @'.split())
        opr.par.initializeSentenceParsers(
            {'fromDoc':
                'en/Carroll_Lewis-Alice_in_wonderland.xml.gz',
             'toDoc':
                'eo/Carroll_Lewis-Alice_in_wonderland.xml.gz'})

        self.assertEqual(opr.par.sPar.readSentence(['s4'])[0],
            ('(src)="s4">CHAPTER@NN@chapter I@PRP@I Down@VBP@down '
            'the@DT@the Rabbit-Hole@NNP'))
        opr.par.closeFiles()

    def test_ExhaustiveSentenceParser_readSentence_raw(self):
        rawprint = OpusRead('-d Books -s en -t fi -p raw'.split())
        rawprint.par.initializeSentenceParsers(
            {'fromDoc':
                'en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz',
             'toDoc':
                'fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz'})
        self.assertEqual(rawprint.par.sPar.readSentence(['s5.2'])[0],
            ('(src)="s5.2">It was a fine, thick piece of wood, bulbous-'
            'headed, of the sort which is known as a "Penang lawyer."'))
        rawprint.par.closeFiles()

    def test_ExhaustiveSentenceParser_readSentence_raw(self):
        rawprint = OpusRead('-d Books -s en -t fi -p raw'.split())
        rawprint.par.initializeSentenceParsers(
            {'fromDoc':
                'en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz',
             'toDoc':
                'fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz'})
        self.assertEqual(rawprint.par.sPar.readSentence(['s5.2'])[0],
            ('(src)="s5.2">It was a fine, thick piece of wood, bulbous-'
            'headed, of the sort which is known as a "Penang lawyer."'))
        rawprint.par.closeFiles()

    def test_SentenceParser_readSentence_annotations(self):
        opr = OpusRead('-d Books -s en -t eo -pa'.split())
        opr.par.initializeSentenceParsers(
            {'fromDoc':
                'en/Carroll_Lewis-Alice_in_wonderland.xml.gz',
             'toDoc':
                'eo/Carroll_Lewis-Alice_in_wonderland.xml.gz'})

        self.assertEqual(opr.par.sPar.readSentence(['s4'])[0],
            ('(src)="s4">CHAPTER|NN|chapter I|PRP|I Down|VBP|down '
            'the|DT|the Rabbit-Hole|NNP'))
        opr.par.closeFiles()

    def test_SentenceParser_readSentence_annotations_change_delimiter(self):
        opr = OpusRead('-d Books -s en -t eo -pa -ca @'.split())
        opr.par.initializeSentenceParsers(
            {'fromDoc':
                'en/Carroll_Lewis-Alice_in_wonderland.xml.gz',
             'toDoc':
                'eo/Carroll_Lewis-Alice_in_wonderland.xml.gz'})

        self.assertEqual(opr.par.sPar.readSentence(['s4'])[0],
            '(src)="s4">CHAPTER@NN@chapter I@PRP@I Down@VBP@down ' +
            'the@DT@the Rabbit-Hole@NNP')
        opr.par.closeFiles()

    def test_SentenceParser_readSentence_raw(self):
        fastprinter = OpusRead('-d Books -s en -t fi -p raw -f'.split())
        fastprinter.par.initializeSentenceParsers(
            {'fromDoc':
                'en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz',
             'toDoc':
                'fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz'})
        self.assertEqual(fastprinter.par.sPar.readSentence(['s5.2'])[0],
            ('(src)="s5.2">It was a fine, thick piece of wood, bulbous-'
            'headed, of the sort which is known as a "Penang lawyer."'))
        fastprinter.par.closeFiles()

    def test_AlignmentParser_readPair_sentence_limits_when_languages_in_unalphabetical_order(self):
        opr = OpusRead('-d Books -s fi -t en -T 0'.split())
        opr.par.initializeSentenceParsers(
            {'fromDoc':
                'en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz',
             'toDoc':
                'fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz'})

        opr.par.parseLine('<s>')
        opr.par.parseLine('<link xtargets="s1;s1" id="SL1"/>')
        ret = opr.par.readPair()
        self.assertEqual(ret, -1)

        opr.par.closeFiles()

        opr = OpusRead('-d Books -s fi -t en -T 1'.split())
        opr.par.initializeSentenceParsers(
            {'fromDoc':
                'en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz',
             'toDoc':
                'fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz'})

        opr.par.parseLine('<s>')
        opr.par.parseLine('<link xtargets="s1;s1" id="SL1"/>')
        ret = opr.par.readPair()
        self.assertEqual(type(ret[0]), str)

        opr.par.closeFiles()

        opr = OpusRead('-d Books -s fi -t en -S 3-4 -T 1'.split())
        opr.par.initializeSentenceParsers(
            {'fromDoc':
                'en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz',
             'toDoc':
                'fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz'})
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
        printer = OpusRead('-d Books -s en -t eo'.split())
        printer.printPairs()
        self.assertEqual(True, True)

    def test_normal_xml_write(self):
        OpusRead(('-d OpenOffice -s en_GB -t fr -m 1 -w '
            'test_files/test_result').split()).printPairs()
        with open('test_files/test_result', 'r') as f:
            self.assertEqual(f.read(),
                ('\n# en_GB/text/schart/main0000.xml.gz\n'
                '# fr/text/schart/main0000.xml.gz\n\n'
                '================================\n(src)="stit.1">Charts '
                'in $[ officename ]\n(trg)="stit.1">Diagrammes dans'
                ' $[officename ]\n================================\n'))

    def test_normal_xml_write_fast(self):
        OpusRead(('-d OpenOffice -s en_GB -t fr -m 1 -w '
            'test_files/test_result -f').split()).printPairs()
        with open('test_files/test_result', 'r') as f:
            self.assertEqual(f.read(),
                ('\n# en_GB/text/schart/main0000.xml.gz\n'
                '# fr/text/schart/main0000.xml.gz\n\n'
                '================================\n(src)="stit.1">Charts '
                'in $[ officename ]\n(trg)="stit.1">Diagrammes dans'
                ' $[officename ]\n================================\n'))

    def test_normal_xml_print(self):
        var = pairPrinterToVariable('-d OpenOffice -s en_GB -t fr -m 1'.split())
        self.assertEqual(var,
            ('\n# en_GB/text/schart/main0000.xml.gz\n'
            '# fr/text/schart/main0000.xml.gz\n\n'
            '================================\n(src)="stit.1">Charts '
            'in $[ officename ]\n(trg)="stit.1">Diagrammes'
            ' dans $[officename ]\n================================\n'))

    def test_normal_xml_print_fast(self):
        var = pairPrinterToVariable(
            '-d OpenOffice -s en_GB -t fr -m 1 -f'.split())
        self.assertEqual(var,
            ('\n# en_GB/text/schart/main0000.xml.gz\n'
            '# fr/text/schart/main0000.xml.gz\n\n'
            '================================\n(src)="stit.1">Charts '
            'in $[ officename ]\n(trg)="stit.1">Diagrammes'
            ' dans $[officename ]\n================================\n'))

    def test_normal_raw_write(self):
        OpusRead(
            ('-d OpenOffice -s en_GB -t fr -m 1 -w test_files/test_result '
            '-p raw').split()).printPairs()
        with open('test_files/test_result', 'r') as f:
            self.assertEqual(f.read(),
                ('\n# en_GB/text/schart/main0000.xml.gz\n'
                '# fr/text/schart/main0000.xml.gz\n\n'
                '================================\n(src)="stit.1">Charts '
                'in $[officename]\n(trg)="stit.1">Diagrammes'
                ' dans $[officename]\n================================\n'))

    def test_normal_raw_write_fast(self):
        OpusRead(
            ('-d OpenOffice -s en_GB -t fr -m 1 -w test_files/test_result '
            '-p raw -f').split()).printPairs()
        with open('test_files/test_result', 'r') as f:
            self.assertEqual(f.read(),
                ('\n# en_GB/text/schart/main0000.xml.gz\n'
                '# fr/text/schart/main0000.xml.gz\n\n'
                '================================\n(src)="stit.1">Charts '
                'in $[officename]\n(trg)="stit.1">Diagrammes'
                ' dans $[officename]\n================================\n'))

    def test_normal_raw_print(self):
        var = pairPrinterToVariable(
            '-d OpenOffice -s en_GB -t fr -m 1 -p raw'.split())
        self.assertEqual(var,
            ('\n# en_GB/text/schart/main0000.xml.gz\n'
            '# fr/text/schart/main0000.xml.gz\n\n'
            '================================\n(src)="stit.1">Charts '
            'in $[officename]\n(trg)="stit.1">Diagrammes'
            ' dans $[officename]\n================================\n'))

    def test_normal_raw_print_fast(self):
        var = pairPrinterToVariable(
            '-d OpenOffice -s en_GB -t fr -m 1 -p raw -f'.split())
        self.assertEqual(var,
            ('\n# en_GB/text/schart/main0000.xml.gz\n'
            '# fr/text/schart/main0000.xml.gz\n\n'
            '================================\n(src)="stit.1">Charts '
            'in $[officename]\n(trg)="stit.1">Diagrammes'
            ' dans $[officename]\n================================\n'))

    def test_normal_raw_print_OpenSubtitles(self):
        var = pairPrinterToVariable(
            '-d OpenSubtitles -s eo -t kk -m 1 -p raw'.split())
        self.assertEqual(var,
            ('\n# eo/2001/245429/5818397.xml.gz\n'
            '# kk/2001/245429/6899218.xml.gz\n\n'
             '================================\n(src)="1">Filmo de '
             '"Studio Ghibli"\n(trg)="1">ГИБЛИ" '
             'студиясы\n================================\n'))

    def test_normal_raw_print_OpenSubtitles_fast(self):
        var = pairPrinterToVariable(
            '-d OpenSubtitles -s eo -t kk -m 1 -p raw -f'.split())
        self.assertEqual(var,
            ('\n# eo/2001/245429/5818397.xml.gz\n'
            '# kk/2001/245429/6899218.xml.gz\n\n'
             '================================\n(src)="1">Filmo de '
             '"Studio Ghibli"\n(trg)="1">ГИБЛИ" '
             'студиясы\n================================\n'))


    def test_normal_parsed_write(self):
        OpusRead(
            ('-d DGT -s en -t es -m 1 -p parsed -pa -sa upos '
            'feats lemma -ta upos feats lemma -w test_files/test_result '
            '-r v4').split()).printPairs()
        with open('test_files/test_result', 'r') as f:
            self.assertEqual(f.read(),
                ('\n# en/12005S_TTE.xml.gz\n# es/12005S_TTE.xml.gz\n\n'
                '================================'
                '\n(src)="1">Treaty|NOUN|Number=Sing|treaty\n(trg)="1">'
                'Tratado|VERB|Gender=Masc|Number=Sing|VerbForm=Part|tratado'
                '\n================================\n'))

    def test_normal_parsed_write_fast(self):
        OpusRead(
            ('-d DGT -s en -t es -m 1 -p parsed -pa -sa upos feats lemma '
            '-ta upos feats lemma -w test_files/test_result -f '
            '-r v4').split()).printPairs()
        with open('test_files/test_result', 'r') as f:
            self.assertEqual(f.read(),
                ('\n# en/12005S_TTE.xml.gz\n'
                '# es/12005S_TTE.xml.gz\n\n================================'
                '\n(src)="1">Treaty|NOUN|Number=Sing|treaty\n(trg)="1">'
                'Tratado|VERB|Gender=Masc|Number=Sing|VerbForm=Part|tratado'
                '\n================================\n'))

    def test_normal_parsed_print(self):
        var = pairPrinterToVariable(
            ('-d DGT -s en -t es -m 1 -p parsed -pa -sa upos feats lemma '
            '-ta upos feats lemma -r v4').split())
        self.assertEqual(var,
            ('\n# en/12005S_TTE.xml.gz\n# es/12005S_TTE.xml.gz\n\n'
            '================================'
            '\n(src)="1">Treaty|NOUN|Number=Sing|treaty\n(trg)="1">'
            'Tratado|VERB|Gender=Masc|Number=Sing|VerbForm=Part|tratado'
            '\n================================\n'))

    def test_normal_parsed_print_unalphabetical(self):
        var = pairPrinterToVariable(
            ('-d DGT -s es -t en -m 1 -p parsed -pa -sa upos lemma '
            '-ta upos feats lemma -r v4').split())
        self.assertEqual(var,
            ('\n# en/12005S_TTE.xml.gz\n# es/12005S_TTE.xml.gz\n\n'
            '================================'
            '\n(src)="1">Tratado|VERB|tratado\n(trg)="1">Treaty|NOUN|'
            'Number=Sing|treaty\n================================\n'))

    def test_normal_parsed_print_fast(self):
        var = pairPrinterToVariable(
            ('-d DGT -s en -t es -m 1 -p parsed -pa -sa upos feats lemma '
            '-ta upos feats lemma -f -r v4').split())
        self.assertEqual(var,
            ('\n# en/12005S_TTE.xml.gz\n# es/12005S_TTE.xml.gz\n\n'
            '================================'
            '\n(src)="1">Treaty|NOUN|Number=Sing|treaty\n(trg)="1">'
            'Tratado|VERB|Gender=Masc|Number=Sing|VerbForm=Part|tratado'
            '\n================================\n'))

    def test_normal_parsed_print_all_attributes(self):
        var = pairPrinterToVariable(
            ('-d DGT -s en -t es -m 1 -p parsed -pa -sa all_attrs '
            '-ta all_attrs -r v4').split())
        self.assertEqual(var,
            ('\n# en/12005S_TTE.xml.gz\n# es/12005S_TTE.xml.gz\n\n'
            '================================'
            '\n(src)="1">Treaty|root|Number=Sing|0|1.1|treaty|SpaceAfter=No|'
            'NOUN|NOUN\n(trg)="1">Tratado|root|Gender=Masc|Number=Sing|'
            'VerbForm=Part|0|1.1|tratado|SpaceAfter=No|VERB'
            '\n================================\n'))

    def test_normal_parsed_print_all_attributes_fast(self):
        var = pairPrinterToVariable(
            ('-d DGT -s en -t es -m 1 -p parsed -pa -sa all_attrs '
            '-ta all_attrs -f -r v4').split())
        self.assertEqual(var,
            ('\n# en/12005S_TTE.xml.gz\n# es/12005S_TTE.xml.gz\n\n'
            '================================'
            '\n(src)="1">Treaty|root|Number=Sing|0|1.1|treaty|SpaceAfter=No|'
            'NOUN|NOUN\n(trg)="1">Tratado|root|Gender=Masc|Number=Sing|'
            'VerbForm=Part|0|1.1|tratado|SpaceAfter=No|VERB'
            '\n================================\n'))

    def test_tmx_xml_write(self):
        OpusRead(
            ('-d OpenOffice -s en_GB -t fr -m 1 -w test_files/test_result '
            '-wm tmx').split()).printPairs()
        with open('test_files/test_result', 'r') as f:
            self.assertEqual(f.read(),
                ('<?xml version="1.0" encoding="utf-8"?>\n<tmx version="1.4.">'
                '\n<header srclang="en_GB"\n\tadminlang="en"\n\tsegtype='
                '"sentence"\n\tdatatype="PlainText" />\n\t<body>\n\t\t<tu>'
                '\n\t\t\t<tuv xml:lang="en_GB"><seg>Charts in $[ officename ]'
                '</seg></tuv>\n\t\t\t<tuv xml:lang="fr"><seg>Diagrammes dans '
                '$[officename ]</seg></tuv>\n\t\t</tu>\n\t</body>\n</tmx>'))

    def test_tmx_xml_write_unalphabetical(self):
        var = pairPrinterToVariable(
            ('-d OpenOffice -s fr -t en_GB -m 1 -w test_files/test_result '
            '-wm tmx').split())
        with open('test_files/test_result', 'r') as f:
            self.assertEqual(f.read(),
                ('<?xml version="1.0" encoding="utf-8"?>\n<tmx version="1.4."'
                '>\n<header srclang="fr"\n\tadminlang="en"\n\tsegtype="'
                'sentence"\n\tdatatype="PlainText" />\n\t<body>\n\t\t<tu>'
                '\n\t\t\t<tuv xml:lang="fr"><seg>Diagrammes dans '
                '$[officename ]</seg></tuv>\n\t\t\t<tuv xml:lang="en_GB">'
                '<seg>Charts in $[ officename ]</seg></tuv>\n\t\t</tu>\n\t'
                '</body>\n</tmx>'))

    def test_tmx_xml_write_fast(self):
        OpusRead(
            ('-d OpenOffice -s en_GB -t fr -m 1 -w test_files/test_result '
            '-wm tmx -f').split()).printPairs()
        with open('test_files/test_result', 'r') as f:
            self.assertEqual(f.read(),
                ('<?xml version="1.0" encoding="utf-8"?>\n<tmx version="1.4.">'
                '\n<header srclang="en_GB"\n\tadminlang="en"\n\tsegtype='
                '"sentence"\n\tdatatype="PlainText" />\n\t<body>\n\t\t<tu>'
                '\n\t\t\t<tuv xml:lang="en_GB"><seg>Charts in $[ officename ]'
                '</seg></tuv>\n\t\t\t<tuv xml:lang="fr"><seg>Diagrammes dans '
                '$[officename ]</seg></tuv>\n\t\t</tu>\n\t</body>\n</tmx>'))

    def test_tmx_xml_print(self):
        var = pairPrinterToVariable(
            '-d OpenOffice -s en_GB -t fr -m 1 -wm tmx'.split())
        self.assertEqual(var,
            ('<?xml version="1.0" encoding="utf-8"?>\n<tmx version="1.4.">\n'
            '<header srclang="en_GB"\n\tadminlang="en"\n\tsegtype="sentence"'
            '\n\tdatatype="PlainText" />\n\t<body>\n\t\t<tu>\n\t\t\t'
            '<tuv xml:lang="en_GB"><seg>Charts in $[ officename ]</seg></tuv>'
            '\n\t\t\t<tuv xml:lang="fr"><seg>Diagrammes dans $[officename ]'
            '</seg></tuv>\n\t\t</tu>\n\t</body>\n</tmx>\n'))

    def test_tmx_xml_print_unalphabetical(self):
        var = pairPrinterToVariable(
            '-d OpenOffice -s fr -t en_GB -m 1 -wm tmx'.split())
        self.assertEqual(var,
            ('<?xml version="1.0" encoding="utf-8"?>\n<tmx version="1.4.">\n'
            '<header srclang="fr"\n\tadminlang="en"\n\tsegtype="sentence"'
            '\n\tdatatype="PlainText" />\n\t<body>\n\t\t<tu>\n\t\t\t'
            '<tuv xml:lang="fr"><seg>Diagrammes dans $[officename ]'
            '</seg></tuv>\n\t\t\t<tuv xml:lang="en_GB"><seg>Charts in '
            '$[ officename ]</seg></tuv>\n\t\t</tu>\n\t</body>\n</tmx>\n'))

    def test_tmx_xml_print_fast(self):
        var = pairPrinterToVariable(
            '-d OpenOffice -s en_GB -t fr -m 1 -wm tmx -f'.split())
        self.assertEqual(var,
            ('<?xml version="1.0" encoding="utf-8"?>\n<tmx version="1.4.">\n'
            '<header srclang="en_GB"\n\tadminlang="en"\n\tsegtype="sentence"'
            '\n\tdatatype="PlainText" />\n\t<body>\n\t\t<tu>\n\t\t\t'
            '<tuv xml:lang="en_GB"><seg>Charts in $[ officename ]</seg></tuv>'
            '\n\t\t\t<tuv xml:lang="fr"><seg>Diagrammes dans $[officename ]'
            '</seg></tuv>\n\t\t</tu>\n\t</body>\n</tmx>\n'))

    def test_tmx_raw_write(self):
        OpusRead(
            ('-d OpenOffice -s en_GB -t fr -m 1 -w test_files/test_result '
            '-wm tmx -p raw').split()).printPairs()
        with open('test_files/test_result', 'r') as f:
            self.assertEqual(f.read(),
                ('<?xml version="1.0" encoding="utf-8"?>\n<tmx version="1.4.">'
                '\n<header srclang="en_GB"\n\tadminlang="en"\n\tsegtype='
                '"sentence"\n\tdatatype="PlainText" />\n\t<body>\n\t\t<tu>'
                '\n\t\t\t<tuv xml:lang="en_GB"><seg>Charts in $[officename]'
                '</seg></tuv>\n\t\t\t<tuv xml:lang="fr"><seg>Diagrammes dans '
                '$[officename]</seg></tuv>\n\t\t</tu>\n\t</body>\n</tmx>'))

    def test_tmx_raw_write_fast(self):
        OpusRead(
            ('-d OpenOffice -s en_GB -t fr -m 1 -w test_files/test_result '
            '-wm tmx -p raw -f').split()).printPairs()
        with open('test_files/test_result', 'r') as f:
            self.assertEqual(f.read(),
                ('<?xml version="1.0" encoding="utf-8"?>\n<tmx version="1.4.">'
                '\n<header srclang="en_GB"\n\tadminlang="en"\n\tsegtype='
                '"sentence"\n\tdatatype="PlainText" />\n\t<body>\n\t\t<tu>'
                '\n\t\t\t<tuv xml:lang="en_GB"><seg>Charts in $[officename]'
                '</seg></tuv>\n\t\t\t<tuv xml:lang="fr"><seg>Diagrammes dans '
                '$[officename]</seg></tuv>\n\t\t</tu>\n\t</body>\n</tmx>'))

    def test_tmx_raw_print(self):
        var = pairPrinterToVariable(
            '-d OpenOffice -s en_GB -t fr -m 1 -wm tmx -p raw'.split())
        self.assertEqual(var,
            ('<?xml version="1.0" encoding="utf-8"?>\n<tmx version="1.4.">\n'
            '<header srclang="en_GB"\n\tadminlang="en"\n\tsegtype="sentence"'
            '\n\tdatatype="PlainText" />\n\t<body>\n\t\t<tu>\n\t\t\t'
            '<tuv xml:lang="en_GB"><seg>Charts in $[officename]</seg></tuv>'
            '\n\t\t\t<tuv xml:lang="fr"><seg>Diagrammes dans $[officename]'
            '</seg></tuv>\n\t\t</tu>\n\t</body>\n</tmx>\n'))

    def test_tmx_raw_print_fast(self):
        var = pairPrinterToVariable(
            '-d OpenOffice -s en_GB -t fr -m 1 -wm tmx -p raw -f'.split())
        self.assertEqual(var,
            ('<?xml version="1.0" encoding="utf-8"?>\n<tmx version="1.4.">\n'
            '<header srclang="en_GB"\n\tadminlang="en"\n\tsegtype="sentence"'
            '\n\tdatatype="PlainText" />\n\t<body>\n\t\t<tu>\n\t\t\t'
            '<tuv xml:lang="en_GB"><seg>Charts in $[officename]</seg></tuv>'
            '\n\t\t\t<tuv xml:lang="fr"><seg>Diagrammes dans $[officename]'
            '</seg></tuv>\n\t\t</tu>\n\t</body>\n</tmx>\n'))

    def test_tmx_parsed_write(self):
        OpusRead(
            ('-d DGT -s en -t es -m 1 -w test_files/test_result -wm tmx '
            '-p parsed -pa -sa upos feats lemma -ta upos feats lemma '
            '-r v4').split()).printPairs()
        with open('test_files/test_result', 'r') as f:
            self.assertEqual(f.read(),
                ('<?xml version="1.0" encoding="utf-8"?>\n<tmx version="1.4.">'
                '\n<header srclang="en"\n\tadminlang="en"\n\tsegtype='
                '"sentence"\n\tdatatype="PlainText" />\n\t<body>\n\t\t<tu>'
                '\n\t\t\t<tuv xml:lang="en"><seg>Treaty|NOUN|Number=Sing|'
                'treaty</seg></tuv>\n\t\t\t<tuv xml:lang="es"><seg>Tratado|'
                'VERB|Gender=Masc|Number=Sing|VerbForm=Part|tratado</seg>'
                '</tuv>\n\t\t</tu>\n\t</body>\n</tmx>'))

    def test_tmx_parsed_write_fast(self):
        OpusRead(
            ('-d DGT -s en -t es -m 1 -w test_files/test_result -wm tmx '
            '-p parsed -pa -sa upos feats lemma -ta upos feats lemma -f '
            '-r v4').split()).printPairs()
        with open('test_files/test_result', 'r') as f:
            self.assertEqual(f.read(),
                ('<?xml version="1.0" encoding="utf-8"?>\n<tmx version="1.4.">'
                '\n<header srclang="en"\n\tadminlang="en"\n\tsegtype='
                '"sentence"\n\tdatatype="PlainText" />\n\t<body>\n\t\t<tu>'
                '\n\t\t\t<tuv xml:lang="en"><seg>Treaty|NOUN|Number=Sing|'
                'treaty</seg></tuv>\n\t\t\t<tuv xml:lang="es"><seg>Tratado|'
                'VERB|Gender=Masc|Number=Sing|VerbForm=Part|tratado</seg>'
                '</tuv>\n\t\t</tu>\n\t</body>\n</tmx>'))

    def test_tmx_parsed_print(self):
        var = pairPrinterToVariable(
            ('-d DGT -s en -t es -m 1 -wm tmx -p parsed -pa '
            '-sa upos feats lemma -ta upos feats lemma -r v4').split())
        self.assertEqual(var,
            ('<?xml version="1.0" encoding="utf-8"?>\n<tmx version="1.4.">'
            '\n<header srclang="en"\n\tadminlang="en"\n\tsegtype='
            '"sentence"\n\tdatatype="PlainText" />\n\t<body>\n\t\t<tu>'
            '\n\t\t\t<tuv xml:lang="en"><seg>Treaty|NOUN|Number=Sing|'
            'treaty</seg></tuv>\n\t\t\t<tuv xml:lang="es"><seg>Tratado|VERB|'
            'Gender=Masc|Number=Sing|VerbForm=Part|tratado</seg></tuv>\n\t\t'
            '</tu>\n\t</body>\n</tmx>\n'))

    def test_tmx_parsed_print_fast(self):
        var = pairPrinterToVariable(
            ('-d DGT -s en -t es -m 1 -wm tmx -p parsed -pa -sa upos feats '
            'lemma -ta upos feats lemma -f -r v4').split())
        self.assertEqual(var,
            ('<?xml version="1.0" encoding="utf-8"?>\n<tmx version="1.4.">'
            '\n<header srclang="en"\n\tadminlang="en"\n\tsegtype='
            '"sentence"\n\tdatatype="PlainText" />\n\t<body>\n\t\t<tu>'
            '\n\t\t\t<tuv xml:lang="en"><seg>Treaty|NOUN|Number=Sing|'
            'treaty</seg></tuv>\n\t\t\t<tuv xml:lang="es"><seg>Tratado|'
            'VERB|Gender=Masc|Number=Sing|VerbForm=Part|tratado</seg>'
            '</tuv>\n\t\t</tu>\n\t</body>\n</tmx>\n'))

    def test_moses_xml_write(self):
        OpusRead(
            ('-d OpenOffice -s en_GB -t fr -m 1 -w test_files/test.src '
            'test_files/test.trg -wm moses').split()).printPairs()
        with open('test_files/test.src', 'r') as f:
            self.assertEqual(f.read(), 'Charts in $[ officename ]\n')
        with open('test_files/test.trg', 'r') as f:
            self.assertEqual(f.read(), 'Diagrammes dans $[officename ]\n')

    def test_moses_xml_write_unalphabetical(self):
        OpusRead(
            ('-d OpenOffice -s fr -t en_GB -m 1 -w test_files/test.src '
            'test_files/test.trg -wm moses').split()).printPairs()
        with open('test_files/test.src', 'r') as f:
            self.assertEqual(f.read(), 'Diagrammes dans $[officename ]\n')
        with open('test_files/test.trg', 'r') as f:
            self.assertEqual(f.read(), 'Charts in $[ officename ]\n')

    def test_moses_xml_write_with_file_names(self):
        OpusRead(
            ('-d OpenOffice -s en_GB -t fr -m 1 -w test_files/test.src '
            'test_files/test.trg -wm moses -pn').split()).printPairs()
        with open('test_files/test.src', 'r') as f:
            self.assertEqual(f.read(),
                ('\n<fromDoc>en_GB/text/schart/main0000.xml.gz</fromDoc>\n\n'
                'Charts in $[ officename ]\n'))
        with open('test_files/test.trg', 'r') as f:
            self.assertEqual(f.read(),
                ('\n<toDoc>fr/text/schart/main0000.xml.gz</toDoc>\n\n'
                'Diagrammes dans $[officename ]\n'))

    def test_moses_xml_write_single_file(self):
        OpusRead(
            ('-d OpenOffice -s en_GB -t fr -m 1 -w test_files/test.src '
            '-wm moses').split()).printPairs()
        with open('test_files/test.src', 'r') as f:
            self.assertEqual(f.read(),
                'Charts in $[ officename ]\tDiagrammes dans $[officename ]\n')

    def test_moses_xml_write_single_file_unalphabetical(self):
        OpusRead(
            ('-d OpenOffice -s fr -t en_GB -m 1 -w test_files/test.src '
            '-wm moses').split()).printPairs()
        with open('test_files/test.src', 'r') as f:
            self.assertEqual(f.read(),
                'Diagrammes dans $[officename ]\tCharts in $[ officename ]\n')

    def test_moses_xml_write_single_file_with_file_names(self):
        OpusRead(
            ('-d OpenOffice -s en_GB -t fr -m 1 -w test_files/test.src '
            '-wm moses -pn').split()).printPairs()
        with open('test_files/test.src', 'r') as f:
            self.assertEqual(f.read(),
                ('\n<fromDoc>en_GB/text/schart/main0000.xml.gz</fromDoc>\n'
                '<toDoc>fr/text/schart/main0000.xml.gz</toDoc>\n\n'
                'Charts in $[ officename ]\tDiagrammes dans $[officename ]\n'))

    def test_moses_xml_write_single_file_with_file_names_unalphabetical(self):
        OpusRead(
            ('-d OpenOffice -s fr -t en_GB -m 1 -w test_files/test.src '
            '-wm moses -pn').split()).printPairs()
        with open('test_files/test.src', 'r') as f:
            self.assertEqual(f.read(),
                ('\n<fromDoc>en_GB/text/schart/main0000.xml.gz</fromDoc>\n'
                '<toDoc>fr/text/schart/main0000.xml.gz</toDoc>\n\n'
                'Diagrammes dans $[officename ]\tCharts in $[ officename ]\n'))

    def test_moses_xml_write_fast(self):
        OpusRead(
            ('-d OpenOffice -s en_GB -t fr -m 1 -w test_files/test.src '
            'test_files/test.trg -wm moses -f').split()).printPairs()
        with open('test_files/test.src', 'r') as f:
            self.assertEqual(f.read(), 'Charts in $[ officename ]\n')
        with open('test_files/test.trg', 'r') as f:
            self.assertEqual(f.read(), 'Diagrammes dans $[officename ]\n')

    def test_moses_xml_print(self):
        var = pairPrinterToVariable(
            '-d OpenOffice -s en_GB -t fr -m 1 -wm moses'.split())
        self.assertEqual(var,
            'Charts in $[ officename ]\tDiagrammes dans $[officename ]\n')

    def test_moses_xml_print_unalphabetical(self):
        var = pairPrinterToVariable(
            '-d OpenOffice -s fr -t en_GB -m 1 -wm moses'.split())
        self.assertEqual(var,
            'Diagrammes dans $[officename ]\tCharts in $[ officename ]\n')

    def test_moses_xml_print_with_file_names(self):
        var = pairPrinterToVariable(
            '-d OpenOffice -s en_GB -t fr -m 1 -wm moses -pn'.split())
        self.assertEqual(var,
            ('\n<fromDoc>en_GB/text/schart/main0000.xml.gz</fromDoc>\n'
            '<toDoc>fr/text/schart/main0000.xml.gz</toDoc>\n\nCharts in '
            '$[ officename ]\tDiagrammes dans $[officename ]\n'))

    def test_moses_xml_print_fast(self):
        var = pairPrinterToVariable(
            '-d OpenOffice -s en_GB -t fr -m 1 -wm moses -f'.split())
        self.assertEqual(var,
            'Charts in $[ officename ]\tDiagrammes dans $[officename ]\n')

    def test_moses_raw_write(self):
        OpusRead(
            ('-d OpenOffice -s en_GB -t fr -m 1 -w test_files/test.src '
            'test_files/test.trg -wm moses -p raw').split()).printPairs()
        with open('test_files/test.src', 'r') as f:
            self.assertEqual(f.read(), 'Charts in $[officename]\n')
        with open('test_files/test.trg', 'r') as f:
            self.assertEqual(f.read(), 'Diagrammes dans $[officename]\n')

    def test_moses_raw_write_fast(self):
        OpusRead(
            ('-d OpenOffice -s en_GB -t fr -m 1 -w test_files/test.src '
            'test_files/test.trg -wm moses -p raw -f').split()).printPairs()
        with open('test_files/test.src', 'r') as f:
            self.assertEqual(f.read(), 'Charts in $[officename]\n')
        with open('test_files/test.trg', 'r') as f:
            self.assertEqual(f.read(), 'Diagrammes dans $[officename]\n')

    def test_moses_raw_print(self):
        var = pairPrinterToVariable(
            '-d OpenOffice -s en_GB -t fr -m 1 -wm moses -p raw'.split())
        self.assertEqual(var,
            'Charts in $[officename]\tDiagrammes dans $[officename]\n')

    def test_moses_raw_print_fast(self):
        var = pairPrinterToVariable(
            '-d OpenOffice -s en_GB -t fr -m 1 -wm moses -p raw -f'.split())
        self.assertEqual(var,
            'Charts in $[officename]\tDiagrammes dans $[officename]\n')

    def test_moses_parsed_write(self):
        OpusRead(
            ('-d DGT -s en -t es -m 1 -w test_files/test.src '
            'test_files/test.trg -wm moses -p parsed -pa -sa upos feats '
            'lemma -ta upos feats lemma -r v4').split()).printPairs()
        with open('test_files/test.src', 'r') as f:
            self.assertEqual(f.read(), 'Treaty|NOUN|Number=Sing|treaty\n')
        with open('test_files/test.trg', 'r') as f:
            self.assertEqual(f.read(),
                'Tratado|VERB|Gender=Masc|Number=Sing|VerbForm=Part|tratado\n')

    def test_moses_parsed_write_fast(self):
        OpusRead(
            ('-d DGT -s en -t es -m 1 -w test_files/test.src '
            'test_files/test.trg -wm moses -p parsed -pa -sa upos feats '
            'lemma -ta upos feats lemma -f -r v4').split()).printPairs()
        with open('test_files/test.src', 'r') as f:
            self.assertEqual(f.read(), 'Treaty|NOUN|Number=Sing|treaty\n')
        with open('test_files/test.trg', 'r') as f:
            self.assertEqual(f.read(),
                'Tratado|VERB|Gender=Masc|Number=Sing|VerbForm=Part|tratado\n')

    def test_moses_parsed_print(self):
        var = pairPrinterToVariable(
            ('-d DGT -s en -t es -m 1 -wm moses -p parsed -pa -sa upos '
            'feats lemma -ta upos feats lemma -r v4').split())
        self.assertEqual(var,
            ('Treaty|NOUN|Number=Sing|treaty\tTratado|VERB|Gender=Masc|'
            'Number=Sing|VerbForm=Part|tratado\n'))

    def test_moses_parsed_print_fast(self):
        var = pairPrinterToVariable(
            ('-d DGT -s en -t es -m 1 -wm moses -p parsed -pa -sa upos '
            'feats lemma -ta upos feats lemma -f -r v4').split())
        self.assertEqual(var,
            ('Treaty|NOUN|Number=Sing|treaty\tTratado|VERB|Gender=Masc|'
            'Number=Sing|VerbForm=Part|tratado\n'))

    def test_links_write(self):
        OpusRead(
            ('-d OpenOffice -s en_GB -t fr -m 1 -w test_files/test_result '
            '-wm links').split()).printPairs()
        with open('test_files/test_result', 'r') as f:
            self.assertEqual(f.read(),
                ('<?xml version="1.0" encoding="utf-8"?>\n'
                '<!DOCTYPE cesAlign PUBLIC "-//CES//DTD'
                ' XML cesAlign//EN" "">\n<cesAlign version="1.0">\n '
                '<linkGrp targType="s" toDoc="fr/text/schart/main0000.xml.gz"'
                ' fromDoc="en_GB/text/schart/main0000.xml.gz">\n'
                '<link certainty="3.118182" xtargets="stit.1;stit.1" id="SL1"'
                ' />\n </linkGrp>\n</cesAlign>'))

    def test_links_write_unalphabetical(self):
        OpusRead(
            ('-d OpenOffice -s fr -t en_GB -m 1 -w test_files/test_result '
            '-wm links -S 1 -T 2').split()).printPairs()
        with open('test_files/test_result', 'r') as f:
            self.assertEqual(f.read(),
                ('<?xml version="1.0" encoding="utf-8"?>'
                '\n<!DOCTYPE cesAlign PUBLIC "-//CES//DTD XML cesAlign//EN" "">'
                '\n<cesAlign version="1.0">\n <linkGrp targType="s" '
                'toDoc="fr/text/schart/main0000.xml.gz" '
                'fromDoc="en_GB/text/schart/main0000.xml.gz">'
                '\n <linkGrp targType="s" toDoc="fr/text/schart/main0202.xml.gz"'
                ' fromDoc="en_GB/text/schart/main0202.xml.gz">'
                '\n<link certainty="0.1794861" xtargets="s7.2 s7.3;s7.2" '
                'id="SL20" />\n </linkGrp>\n</cesAlign>'))

    def test_links_print(self):
        var = pairPrinterToVariable(
            '-d OpenOffice -s en_GB -t fr -m 1 -wm links'.split())
        self.assertEqual(var,
            ('<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE cesAlign '
            'PUBLIC "-//CES//DTD XML cesAlign//EN" "">\n<cesAlign '
            'version="1.0">\n <linkGrp targType="s" '
            'toDoc="fr/text/schart/main0000.xml.gz"'
            ' fromDoc="en_GB/text/schart/main0000.xml.gz">\n'
            '<link certainty="3.118182" xtargets="stit.1;stit.1" id="SL1" />'
            '\n </linkGrp>\n</cesAlign>\n'))

    def test_links_print_unalphabetical(self):
        var = pairPrinterToVariable(
            '-d OpenOffice -s fr -t en_GB -m 1 -wm links -S 1 -T 2'.split())
        self.assertEqual(var,
            ('<?xml version="1.0" encoding="utf-8"?>'
            '\n<!DOCTYPE cesAlign PUBLIC "-//CES//DTD XML cesAlign//EN" "">'
            '\n<cesAlign version="1.0">\n <linkGrp targType="s" '
            'toDoc="fr/text/schart/main0000.xml.gz" '
            'fromDoc="en_GB/text/schart/main0000.xml.gz">'
            '\n <linkGrp targType="s" toDoc="fr/text/schart/main0202.xml.gz"'
            ' fromDoc="en_GB/text/schart/main0202.xml.gz">'
            '\n<link certainty="0.1794861" xtargets="s7.2 s7.3;s7.2" '
            'id="SL20" />\n </linkGrp>\n</cesAlign>\n'))

    def test_iteration_stops_at_the_end_of_the_document_even_if_max_is_not_filled(self):
        var = pairPrinterToVariable(
            '-d Books -s en -t fi -S 5 -T 2 -m 5'.split())
        self.assertEqual(var,
            ('\n# en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz\n'
            '# fi/Doyle_Arthur_Conan-Hound_of_the_'
            'Baskervilles.xml.gz\n\n================================\n'
            '(src)="s942.0">" So I think .\n(src)="s9'
            '42.1">But if we can only trace L. L. it should clear up the '
            'whole business .\n(src)="s942.2">We have gained that much .\n'
            '(src)="s942.3">We know that there is someone who has the facts'
            ' if we can only find her .\n(src)="s942.4">What do you think we '
            'should do ? "\n(trg)="s942.0">" Niin minäkin'
            ' ajattelen , mutta jos voisitte saada tuon L. L : n käsiinne , '
            'niin olisi paljon voitettu , ja onhan edullista jo tietääkin , '
            'että on olemassa joku nainen , joka tuntee asian oikean laidan ,'
            ' jos vaan voimme saada hänet ilmi .\n(trg)="s942.1">Mitä '
            'arvelette nyt olevan tekeminen ? "\n'
            '================================\n'))

    def test_use_given_sentence_alignment_file(self):
        OpusRead(
            ('-d Books -s en -t fi -S 5 -T 2 -wm links -w '
            'test_files/testlinks').split()).printPairs()
        var = pairPrinterToVariable(
            '-d Books -s en -t fi -af test_files/testlinks'.split())
        self.assertEqual(var,
            ('\n# en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz\n'
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
            'olevan tekeminen ? "\n================================\n'))

    def test_checks_first_whether_documents_are_in_path(self):
        with open('test_files/testlinks', 'w') as f:
            f.write(
                ('<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE cesAlign '
                'PUBLIC "-//CES//DTD XML cesAlign//EN" "">'
                '\n<cesAlign version="1.0">\n<linkGrp fromDoc="test_files/'
                'test_en" toDoc="test_files/test_fi" >\n<link xtargets='
                '"s1;s1"/>\n </linkGrp>+\n</cesAlign>'))
        with open('test_files/test_en', 'w') as f:
            f.write(
                ('<?xml version="1.0" encoding="utf-8"?>\n<text>\n'
                '<body>\n<s id="s1">\n <w>test_en1</w>\n <w>test_en2'
                '</w>\n</s>\n </body>\n</text>'))
        with open('test_files/test_fi', 'w') as f:
            f.write(
                ('<?xml version="1.0" encoding="utf-8"?>\n<text>\n <body>\n'
                '<s id="s1">\n <w>test_fi1</w>\n <w>test_fi2'
                '</w>\n</s>\n </body>\n</text>'))
        var = pairPrinterToVariable(
            '-d Books -s en -t fi -af test_files/testlinks'.split())
        self.assertEqual(var,
            ('\n# test_files/test_en\n# test_files/test_fi\n\n'
            '================================\n(src)="s1">test_en1 test_en2\n'
            '(trg)="s1">test_fi1 test_fi2'
            '\n================================\n'))

    def test_checks_first_whether_documents_are_in_path_gz(self):
        with open('test_files/testlinks', 'w') as f:
            f.write(
                ('<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE cesAlign '
                'PUBLIC "-//CES//DTD XML cesAlign//EN" "">'
                '\n<cesAlign version="1.0">\n<linkGrp fromDoc="test_files/'
                'test_en.gz" toDoc="test_files/test_fi.gz" >\n<link '
                'xtargets="s1;s1"/>\n </linkGrp>+\n</cesAlign>'))
        with open('test_files/test_en', 'w') as f:
            f.write(
                ('<?xml version="1.0" encoding="utf-8"?>\n<text>\n'
                '<body>\n<s id="s1">\n <w>test_en1</w>\n <w>test_en2'
                '</w>\n</s>\n </body>\n</text>'))
        with open('test_files/test_fi', 'w') as f:
            f.write(
                ('<?xml version="1.0" encoding="utf-8"?>\n<text>\n <body>\n'
                '<s id="s1">\n <w>test_fi1</w>\n <w>test_fi2'
                '</w>\n</s>\n </body>\n</text>'))
        with open('test_files/test_en', 'rb') as f:
            with gzip.open('test_files/test_en.gz', 'wb') as gf:
                shutil.copyfileobj(f, gf)
        with open('test_files/test_fi', 'rb') as f:
            with gzip.open('test_files/test_fi.gz', 'wb') as gf:
                shutil.copyfileobj(f, gf)
        var = pairPrinterToVariable(
            '-d Books -s en -t fi -af test_files/testlinks'.split())
        self.assertEqual(var,
            ('\n# test_files/test_en.gz\n# test_files/test_fi.gz\n\n'
            '================================\n(src)="s1">test_en1 test_en2\n'
            '(trg)="s1">test_fi1 test_fi2'
            '\n================================\n'))

    def test_filtering_by_src_cld2(self):
        var = pairPrinterToVariable(
                ('-d Books -s en -t fi -r v1 -m 1 --src_cld2 en 0.98'
                ' -af books_alignment.xml').split())
        self.assertEqual(var,
            ('\n# en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz\n'
            '# fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz\n'
            '\n================================'
            '\n(src)="s5.0">Mr. Sherlock Holmes'
            '\n(trg)="s5.0">Herra Sherlock Holmes'
            '\n================================\n'))

    def test_filtering_by_trg_cld2(self):
        var = pairPrinterToVariable(
                ('-d Books -s en -t fi -r v1 -m 1 --trg_cld2 ia 0'
                ' -af books_alignment.xml').split())
        self.assertEqual(var,
            ('\n# en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz\n'
            '# fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz\n'
            '\n================================'
            '\n(src)="s4">Chapter 1 Mr. Sherlock Holmes'
            '\n(trg)="s4">Herra Sherlock Holmes .'
            '\n================================\n'))

    def test_filtering_by_src_langid(self):
        var = pairPrinterToVariable(
                ('-d Books -s en -t fi -r v1 -m 1 --src_langid de 0'
                ' -af books_alignment.xml').split())
        self.assertEqual(var,
            ('\n# en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz\n'
            '# fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz\n'
            '\n================================'
            '\n(src)="s167.0">" Excellent !'
            '\n(trg)="s167.0">" Erinomaista .'
            '\n================================\n'))

    def test_filtering_by_trg_langid(self):
        var = pairPrinterToVariable(
                ('-d Books -s en -t fi -r v1 -m 1 --trg_langid et 0'
                ' -af books_alignment.xml').split())
        self.assertEqual(var,
            ('\n# en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz\n'
            '# fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz\n'
            '\n================================'
            '\n(src)="s4">Chapter 1 Mr. Sherlock Holmes'
            '\n(trg)="s4">Herra Sherlock Holmes .'
            '\n================================\n'))

    def test_filtering_by_lang_labels(self):
        var = pairPrinterToVariable(
            ('-d Books -s en -t fi -r v1 -m 1 --src_cld2 un 0 --trg_cld2 '
            'fi 0.97 --src_langid en 0.17 --trg_langid fi 1'
            ' -af books_alignment.xml').split())
        self.assertEqual(var,
            ('\n# en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz\n'
            '# fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz\n'
            '\n================================'
            '\n(src)="s8.1">I believe'
            '\n(trg)="s8.1">Luulenpa että sinulla'
            '\n================================\n'))

    def test_filtering_by_lang_labels_fast(self):
        var = pairPrinterToVariable(
            ('-d Books -s en -t fi -r v1 -m 1 --src_cld2 un 0 --trg_cld2 '
            'fi 0.97 --src_langid en 0.17 --trg_langid fi 1 -f'
            ' -af books_alignment.xml').split())
        self.assertEqual(var,
            ('\n# en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz\n'
            '# fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz\n'
            '\n================================'
            '\n(src)="s8.1">I believe'
            '\n(trg)="s8.1">Luulenpa että sinulla'
            '\n================================\n'))

    def test_filtering_by_lang_labels_nonalphabetical_lang_order(self):
        var = pairPrinterToVariable(
            ('-d Books -s fi -t en -r v1 -m 1 --trg_cld2 un 0 --src_cld2 '
            'fi 0.97 --trg_langid en 0.17 --src_langid fi 1'
            ' -af books_alignment.xml').split())
        self.assertEqual(var,
            ('\n# en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz\n'
            '# fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz\n'
            '\n================================'
            '\n(src)="s8.1">Luulenpa että sinulla'
            '\n(trg)="s8.1">I believe'
            '\n================================\n'))

    def test_filtering_by_lang_labels_nonalphabetical_lang_order_fast(self):
        var = pairPrinterToVariable(
            ('-d Books -s fi -t en -r v1 -m 1 --trg_cld2 un 0 --src_cld2 '
            'fi 0.97 --trg_langid en 0.17 --src_langid fi 1 -f'
            ' -af books_alignment.xml').split())
        self.assertEqual(var,
            ('\n# en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz\n'
            '# fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz\n'
            '\n================================'
            '\n(src)="s8.1">Luulenpa että sinulla'
            '\n(trg)="s8.1">I believe'
            '\n================================\n'))

    def test_filtering_by_lang_labels_no_matches_found(self):
        var = pairPrinterToVariable(
            ('-d Books -s en -t fi -r v1 -m 1 --src_cld2 fi 2'
            ' -af books_alignment.xml').split())
        self.assertEqual(var,
            ('\n# en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz\n'
            '# fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz\n'
            '\n================================\n'))

    def test_filtering_by_lang_labels_no_matches_found_fast(self):
        var = pairPrinterToVariable(
            ('-d Books -s en -t fi -r v1 -m 1 --src_cld2 fi 2'
            ' -af books_alignment.xml -f').split())
        self.assertEqual(var,
            ('\n# en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz\n'
            '# fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz\n'
            '\n================================\n'))

    def test_use_given_zip_files(self):
        var = pairPrinterToVariable(
            ('-d Books -s en -t fi -m1 -sz en.zip -tz fi.zip'.split()))
        self.assertEqual(var,
            ('\n# en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz'
            '\n# fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz'
            '\n\n================================'
            '\n(src)="s1">Source : manybooks.netAudiobook available here'
            '\n(trg)="s1">Source : Project Gutenberg'
            '\n================================\n'))

    def test_use_given_zip_files_unalphabetical(self):
        var = pairPrinterToVariable(
            ('-d Books -s fi -t en -m1 -sz fi.zip -tz en.zip'.split()))
        self.assertEqual(var,
            ('\n# en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz'
            '\n# fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz'
            '\n\n================================'
            '\n(src)="s1">Source : Project Gutenberg'
            '\n(trg)="s1">Source : manybooks.netAudiobook available here'
            '\n================================\n'))

    def test_source_zip_given_and_target_automatic(self):
        opr = OpusRead('-d Books -s en -t fi -sz en.zip'.split())
        opr.par.initializeSentenceParsers(
            {'fromDoc':
                'en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz',
             'toDoc':
                'fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz'})
        self.assertEqual(opr.par.sourcezip.filename,
            'en.zip')
        self.assertEqual(opr.par.targetzip.filename,
            '/proj/nlpl/data/OPUS/Books/latest/xml/fi.zip')

    def test_source_zip_given_and_target_automatic_unalphabetical(self):
        opr = OpusRead('-d Books -s fi -t en -sz fi.zip'.split())
        opr.par.initializeSentenceParsers(
            {'fromDoc':
                'en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz',
             'toDoc':
                'fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz'})
        self.assertEqual(opr.par.sourcezip.filename,
            '/proj/nlpl/data/OPUS/Books/latest/xml/en.zip')
        self.assertEqual(opr.par.targetzip.filename,
            'fi.zip')

    def test_target_zip_given_and_source_automatic(self):
        opr = OpusRead('-d Books -s en -t fi -tz fi.zip'.split())
        opr.par.initializeSentenceParsers(
            {'fromDoc':
                'en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz',
             'toDoc':
                'fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz'})
        self.assertEqual(opr.par.sourcezip.filename,
            '/proj/nlpl/data/OPUS/Books/latest/xml/en.zip')
        self.assertEqual(opr.par.targetzip.filename,
            'fi.zip')

    def test_target_zip_given_and_source_local(self):
        opr = OpusRead('-d Books -s en -t fi -r v1 -tz fi.zip'.split())
        opr.par.initializeSentenceParsers(
            {'fromDoc':
                'en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz',
             'toDoc':
                'fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz'})
        self.assertEqual(opr.par.sourcezip.filename,
            'Books_v1_xml_en.zip')
        self.assertEqual(opr.par.targetzip.filename,
            'fi.zip')

    def test_target_zip_given_and_source_local_unalphabetical(self):
        opr = OpusRead('-d Books -s fi -t en -r v1 -tz en.zip'.split())
        opr.par.initializeSentenceParsers(
            {'fromDoc':
                'en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz',
             'toDoc':
                'fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz'})
        self.assertEqual(opr.par.sourcezip.filename,
            'en.zip')
        self.assertEqual(opr.par.targetzip.filename,
            'Books_v1_xml_fi.zip')

    def test_source_zip_given_and_target_local(self):
        opr = OpusRead('-d Books -s en -t fi -r v1 -sz en.zip'.split())
        opr.par.initializeSentenceParsers(
            {'fromDoc':
                'en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz',
             'toDoc':
                'fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz'})
        self.assertEqual(opr.par.sourcezip.filename,
            'en.zip')
        self.assertEqual(opr.par.targetzip.filename,
            'Books_v1_xml_fi.zip')

    def test_source_zip_local_and_target_automatic(self):
        opr = OpusRead('-d Books -s en -t es -r v1'.split())
        opr.par.initializeSentenceParsers(
            {'fromDoc':
                'en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz',
             'toDoc':
                'es/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz'})
        self.assertEqual(opr.par.sourcezip.filename,
            'Books_v1_xml_en.zip')
        self.assertEqual(opr.par.targetzip.filename,
            '/proj/nlpl/data/OPUS/Books/v1/xml/es.zip')

    def test_source_zip_local_and_target_automatic_unalphabetical(self):
        opr = OpusRead('-d Books -s fi -t es -r v1'.split())
        opr.par.initializeSentenceParsers(
            {'fromDoc':
                'es/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz',
             'toDoc':
                'fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz'})
        self.assertEqual(opr.par.sourcezip.filename,
            '/proj/nlpl/data/OPUS/Books/v1/xml/es.zip')
        self.assertEqual(opr.par.targetzip.filename,
            'Books_v1_xml_fi.zip')

    def test_target_zip_local_and_source_automatic(self):
        opr = OpusRead('-d Books -s es -t fi -r v1'.split())
        opr.par.initializeSentenceParsers(
            {'fromDoc':
                'es/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz',
             'toDoc':
                'fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz'})
        self.assertEqual(opr.par.sourcezip.filename,
            '/proj/nlpl/data/OPUS/Books/v1/xml/es.zip')
        self.assertEqual(opr.par.targetzip.filename,
            'Books_v1_xml_fi.zip')

class TestOpusCat(unittest.TestCase):

    def printSentencesToVariable(self, arguments):
        old_stdout = sys.stdout
        printout = io.StringIO()
        sys.stdout = printout
        oprinter = OpusCat(arguments)
        oprinter.printSentences()
        sys.stdout = old_stdout
        return printout.getvalue()

    def test_printing_sentences(self):
        var  = self.printSentencesToVariable('-d Books -l fi -p'.split())
        self.assertEqual(var[-145:],
            ('("s1493.9")>Saanko sitten pyytää sinua laittautumaan valmiiksi '
            'puolessa tunnissa , niin menemme samalla tiellä Marciniin '
            'syömään päivällistä ? "\n'))

    def test_printing_sentences_with_limit(self):
        var = self.printSentencesToVariable('-d Books -l fi -m 1 -p'.split())
        self.assertEqual(var,
            ('\n# Books/xml/fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles'
            '.xml\n\n("s1")>Source : Project Gutenberg\n'))

    def test_printing_sentences_without_ids(self):
        var = self.printSentencesToVariable(
            '-d Books -l fi -m 1 -i -p'.split())
        self.assertEqual(var,
            ('\n# Books/xml/fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles'
            '.xml\n\nSource : Project Gutenberg\n'))

    def test_print_annotations(self):
        var = self.printSentencesToVariable(
            '-d Books -l en -m 1 -i -p -pa'.split())
        self.assertEqual(var,
            ('\n# Books/xml/en/Hugo_Victor-Notre_Dame_de_Paris.'
            'xml\n\nSource|NN|source :|:|: Project|NNP|Project '
            'GutenbergTranslation|NNP :|:|: Isabel|NNP|Isabel F.|NNP|F. '
            'HapgoodAudiobook|NNP available|NN|available here|RB|here\n'))

    def test_print_annotations_all_attributes(self):
        var = self.printSentencesToVariable(
            '-d Books -l en -m 1 -i -p -pa -sa all_attrs'.split())
        self.assertEqual(var,
            ('\n# Books/xml/en/Hugo_Victor-Notre_Dame_de_Paris.'
            'xml\n\nSource|NN|w1.1|source|NN|NN :|:|w1.2|:|:|: '
            'Project|NNP|w1.3|Project|NNP|NP GutenbergTranslation|NNP|'
            'w1.4|NNP|NP :|:|w1.5|:|:|: Isabel|NNP|w1.6|Isabel|NNP|NP F'
            '.|NNP|w1.7|F.|NNP|NP HapgoodAudiobook|NNP|w1.8|NNP|NP '
            'available|JJ|w1.9|available|NN|JJ here|RB|w1.10|here|RB|RB\n'))

    def test_print_xml(self):
        var = self.printSentencesToVariable('-d Books -l eo -m 1'.split())
        self.assertEqual(var[-53:],
            '\n <w id="w1.8">,</w> \n <w id="w1.9">M.A.</w>\n</s>\n  \n')

    def test_printing_specific_file(self):
        var = self.printSentencesToVariable(
            ('-d Books -l eo -m 1 -i -p -f '
            'Books/xml/eo/Carroll_Lewis-Alice_in_wonderland.xml').split())
        self.assertEqual(var,
            ('\n# Books/xml/eo/Carroll_Lewis-Alice_in_wonderland.'
            'xml\n\nSource : Project GutenbergTranslation : E.L. '
            'KEARNEY , M.A.\n'))

if __name__ == '__main__':
    unittest.main()

