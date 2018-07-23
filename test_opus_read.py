import unittest
import io
import sys
from opustools_pkg import OpusRead, OpusCat
import xml.parsers.expat

class TestOpusRead(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.opr = OpusRead(["-d", "Books", "-s", "en", "-t", "fi"])
        self.opr.par.initializeSentenceParsers({"fromDoc": "en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz",\
                                             "toDoc": "fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz"})
        self.fastopr = OpusRead(["-d", "Books", "-s", "en", "-t", "fi", "-f"])
        self.fastopr.par.initializeSentenceParsers({"fromDoc": "en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz",\
                                             "toDoc": "fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz"})
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
        self.opr.par.args.wm="normal"
        self.opr.par.slim=["all"]
        self.opr.par.tlim=["all"]
        self.opr.par.args.a = "any"
        self.opr.par.nonAlignments = self.opr.par.args.ln
        self.opr.par.args.m = "all"
        self.opr.par.alignParser = xml.parsers.expat.ParserCreate()
        self.opr.par.alignParser.StartElementHandler = self.opr.par.start_element
        self.opr.par.sPar.wmode = "normal"
        self.opr.par.sPar.pre = "xml"
        self.opr.par.tPar.wmode = "normal"
        self.opr.par.tPar.pre = "xml"
        self.opr.par.sPar.annotations = False
        self.opr.par.tPar.annotations = False
        self.opr.par.args.cm = "\t"
        self.fastopr.par.args.wm="normal"
        self.fastopr.par.slim=["all"]
        self.fastopr.par.tlim=["all"]
        self.fastopr.par.args.a = "any"
        self.fastopr.par.nonAlignments = self.fastopr.par.args.ln
        self.fastopr.par.args.m = "all"
        self.fastopr.par.alignParser = xml.parsers.expat.ParserCreate()
        self.fastopr.par.alignParser.StartElementHandler = self.fastopr.par.start_element
        self.fastopr.par.sPar.wmode = "normal"
        self.fastopr.par.sPar.pre = "xml"
        self.fastopr.par.tPar.wmode = "normal"
        self.fastopr.par.tPar.pre = "xml"
        self.fastopr.par.sPar.annotations = False
        self.fastopr.par.tPar.annotations = False

    def pairPrinterToVariable(self, arguments):
        old_stdout = sys.stdout
        printout = io.StringIO()
        sys.stdout = printout
        oprinter = OpusRead(arguments)
        oprinter.printPairs()
        oprinter.par.closeFiles()
        sys.stdout = old_stdout
        return printout.getvalue()
    
    def test_ExhaustiveSentenceParser_initializing(self):
        self.assertEqual(len(self.opr.par.sPar.sentences), 3831)
        self.assertEqual(len(self.opr.par.tPar.sentences), 3757)

    def test_ExhaustiveSentenceParser_getSentence(self):
        self.assertEqual(self.opr.par.sPar.getSentence("s1"), "Source : manybooks.netAudiobook available here")
        self.assertEqual(self.opr.par.tPar.getSentence("s1"), "Source : Project Gutenberg")

        self.assertEqual(self.opr.par.sPar.getSentence("s4"), "Chapter 1 Mr. Sherlock Holmes")
        self.assertEqual(self.opr.par.tPar.getSentence("s4"), "Herra Sherlock Holmes .")

        self.assertEqual(self.opr.par.sPar.getSentence("s5.4"), '" To James Mortimer , M.R.C.S. , from his friends of the' + \
                                                        ' C.C.H. , " was engraved upon it , with the date " 1884 . "')
        self.assertEqual(self.opr.par.tPar.getSentence("s5.5"), "James Mortimerille ystäviltänsä C. C. H : ssa ' oli" + \
            " kaiverrettu tuuman-levyiselle , kädensijan alapuolella olevalle hopealevylle , sekä vielä vuosiluku 1884 .")

    def test_ExhaustiveSentenceParser_readSentence_format(self):
        self.assertEqual(self.opr.par.sPar.readSentence(["s1"]), '(src)="s1">Source : manybooks.netAudiobook available here')
        self.assertEqual(self.opr.par.tPar.readSentence(["s1"]), '(trg)="s1">Source : Project Gutenberg')
        self.assertEqual(self.opr.par.sPar.readSentence(["s11.0", "s11.1"]), '(src)="s11.0">" Good ! " said Holmes .\n' + \
                                                        '(src)="s11.1">" Excellent ! "')

    def test_ExhaustiveSentenceParser_readSentence_annotations(self):
        opr = OpusRead(["-d", "Books", "-s", "en", "-t", "eo", "-pa"])
        opr.par.initializeSentenceParsers({"fromDoc": "en/Carroll_Lewis-Alice_in_wonderland.xml.gz",\
                                             "toDoc": "eo/Carroll_Lewis-Alice_in_wonderland.xml.gz"})
        self.assertEqual(opr.par.sPar.readSentence(["s4"]), """(src)="s4">CHAPTER|NN|chapter I|PRP|I Down|VBP|down the|DT|the Rabbit-Hole|NNP""")
        opr.par.closeFiles()
        opr = OpusRead(["-d", "Books", "-s", "en", "-t", "eo", "-pa", "-ca", "@"])
        opr.par.initializeSentenceParsers({"fromDoc": "en/Carroll_Lewis-Alice_in_wonderland.xml.gz",\
                                             "toDoc": "eo/Carroll_Lewis-Alice_in_wonderland.xml.gz"})

        self.assertEqual(opr.par.sPar.readSentence(["s4"]), """(src)="s4">CHAPTER@NN@chapter I@PRP@I Down@VBP@down the@DT@the Rabbit-Hole@NNP""")
        opr.par.closeFiles()

    def test_ExhaustiveSentenceParser_readSentence_moses(self):
        self.opr.par.sPar.wmode = "moses"
        self.assertEqual(self.opr.par.sPar.readSentence(["s5.2"]), 'It was a fine , thick piece of wood , bulbous-headed ,' + \
                                                        ' of the sort which is known as a " Penang lawyer . "')

    def test_ExhaustiveSentenceParser_readSentence_tmx(self):
        self.opr.par.sPar.wmode = "tmx"
        self.assertEqual(self.opr.par.sPar.readSentence(["s5.2"]), '\t\t<tu>\n\t\t\t<tuv xml:lang="en"><seg>It was a fine ,' + \
                    ' thick piece of wood , bulbous-headed , of the sort which is known as a " Penang lawyer . "</seg></tuv>')
        self.opr.par.tPar.wmode = "tmx"
        self.assertEqual(self.opr.par.tPar.readSentence(["s5.2", "s5.3"]), """\t\t\t<tuv xml:lang="fi"><seg>Se oli""" + \
         """ jokseenkin soma ja tukeva , se oli varustettu sipulinmuotoisella kädensijalla ja näytti oikealta " tuomarin""" + \
        """ sauvalta . " ' M.R.C.S.</seg></tuv>\n\t\t</tu>""")
    
    def test_ExhaustiveSentenceParser_readSentence_raw(self):
        rawprint = OpusRead(["-d", "Books", "-s", "en", "-t", "fi", "-p", "raw"])
        rawprint.par.initializeSentenceParsers({"fromDoc": "en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz",\
                                             "toDoc": "fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz"})
        self.assertEqual(rawprint.par.sPar.readSentence(["s5.2"]), '(src)="s5.2">It was a fine, thick piece of wood,' + \
                                                    ' bulbous-headed, of the sort which is known as a "Penang lawyer."')
        rawprint.par.closeFiles()
    
    def test_ExhaustiveSentenceParser_readSentence_empty(self):
        self.assertEqual(self.opr.par.sPar.readSentence([""]), "")

    def test_SentenceParser_readSentence_format(self):
        self.assertEqual(self.fastopr.par.sPar.readSentence(["s1"]), '(src)="s1">Source : manybooks.netAudiobook available here')
        self.assertEqual(self.fastopr.par.tPar.readSentence(["s1"]), '(trg)="s1">Source : Project Gutenberg')
        self.assertEqual(self.fastopr.par.sPar.readSentence(["s11.0", "s11.1"]), '(src)="s11.0">" Good ! " said Holmes .\n' + \
                                                            '(src)="s11.1">" Excellent ! "')

    def test_SentenceParser_readSentence_annotations(self):
        opr = OpusRead(["-d", "Books", "-s", "en", "-t", "eo", "-pa"])
        opr.par.initializeSentenceParsers({"fromDoc": "en/Carroll_Lewis-Alice_in_wonderland.xml.gz",\
                                             "toDoc": "eo/Carroll_Lewis-Alice_in_wonderland.xml.gz"})

        self.assertEqual(opr.par.sPar.readSentence(["s4"]), """(src)="s4">CHAPTER|NN|chapter I|PRP|I Down|VBP|down the|DT|the Rabbit-Hole|NNP""")
        opr.par.closeFiles()

    def test_SentenceParser_readSentence_annotations_change_delimiter(self):
        opr = OpusRead(["-d", "Books", "-s", "en", "-t", "eo", "-pa", "-ca", "@"])
        opr.par.initializeSentenceParsers({"fromDoc": "en/Carroll_Lewis-Alice_in_wonderland.xml.gz",\
                                             "toDoc": "eo/Carroll_Lewis-Alice_in_wonderland.xml.gz"})

        self.assertEqual(opr.par.sPar.readSentence(["s4"]), """(src)="s4">CHAPTER@NN@chapter I@PRP@I Down@VBP@down the@DT@the Rabbit-Hole@NNP""")
        opr.par.closeFiles()
    
    def test_SentenceParser_readSentence_moses(self):
        self.fastopr.par.sPar.wmode = "moses"
        self.assertEqual(self.fastopr.par.sPar.readSentence(["s12"]), '" I think also that the probability is in favour of' + \
                                        ' his being a country practitioner who does a great deal of his visiting on foot . "')
    
    def test_SentenceParser_readSentence_tmx(self):
        self.fastopr.par.sPar.wmode = "tmx"
        self.fastopr.par.tPar.wmode = "tmx"
        self.assertEqual(self.fastopr.par.sPar.readSentence(["s16.0"]), """\t\t<tu>\n\t\t\t<tuv xml:lang="en"><seg>" And""" + \
                                                    """ then again , there is the ' friends of the C.C.H. '</seg></tuv>""")
        self.assertEqual(self.fastopr.par.tPar.readSentence(["s16.1", "s16.2"]), """\t\t\t<tuv xml:lang="fi"><seg>Minä""" + \
        """ otaksun , että H tarkoittaa jotain hevosurheiluseuraa . Ehkäpä hän kirurgina oli tehnyt palveluksia""" + \
        """ paikallisen urheiluseuran jäsenille , ja nämä ovat kiitollisuutensa osoitteeksi antaneet tämän pienen lahjan""" + \
        """ . "</seg></tuv>\n\t\t</tu>""")
    
    def test_SentenceParser_readSentence_raw(self):
        fastprinter = OpusRead(["-d", "Books", "-s", "en", "-t", "fi", "-p", "raw", "-f"])
        fastprinter.par.initializeSentenceParsers({"fromDoc": "en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz",\
                                             "toDoc": "fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz"})
        self.assertEqual(fastprinter.par.sPar.readSentence(["s5.2"]), '(src)="s5.2">It was a fine, thick piece of wood,' + \
                                                        ' bulbous-headed, of the sort which is known as a "Penang lawyer."')
        fastprinter.par.closeFiles()
    
    def test_SentenceParser_readSentence_empty(self):
        self.assertEqual(self.fastopr.par.sPar.readSentence([""]), "")
    
    def test_AlignmentParser_readPair_returns_1_if_tag_is_not_link_and_write_mode_is_links(self):
        self.opr.par.args.wm="links"
        self.opr.par.parseLine("<s>")
        ret = self.opr.par.readPair()
        self.assertEqual(ret, 1)

    def test_AlignmentParser_readPair_returns_minus_1_if_tag_is_not_link_and_write_mode_id_not_links(self):
        self.opr.par.parseLine("<s>")
        ret = self.opr.par.readPair()
        self.assertEqual(ret, -1)

    def test_AlignmentParser_readPair_returns_minus_1_if_number_of_sentences_is_outside_limit(self):
        self.opr.par.slim = ["0"]
        self.opr.par.parseLine("<s>")
        self.opr.par.parseLine('<link xtargets="s1;s1" id="SL1"/>')
        ret = self.opr.par.readPair()
        self.assertEqual(ret, -1)

        self.opr.par.slim = ["1"]
        self.opr.par.parseLine('<link xtargets="s1;s1" id="SL1"/>')
        ret = self.opr.par.readPair()
        self.assertEqual(type(ret[0]), str)

        self.opr.par.slim = ["1"]
        self.opr.par.parseLine('<link xtargets="s1;s1" id="SL1"/>')
        ret = self.opr.par.readPair()
        self.assertEqual(type(ret[0]), str)

        self.opr.par.tlim = ["3", "4"]
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
        self.opr.par.args.a = "certainty"
        self.opr.par.args.tr = 0.6
        self.opr.par.parseLine("<s>")
        self.opr.par.parseLine('<link xtargets="s1;s1" id="SL1" certainty="0.5"/> ')
        ret = self.opr.par.readPair()
        self.assertEqual(ret, -1)
        self.opr.par.parseLine('<link xtargets="s1;s1" id="SL1" certainty="0.7"/> ')
        ret = self.opr.par.readPair()
        self.assertEqual(type(ret[0]), str)

    def test_AlignmentParser_readPair_returns_minus_1_if_nonAlignments_is_on_and_source_or_target_is_empty(self):
        self.opr.par.parseLine("<s>")
        self.opr.par.parseLine('<link xtargets="s1;" id="SL1"/> ')
        ret = self.opr.par.readPair()
        self.assertEqual(type(ret[0]), str)
        self.opr.par.nonAlignments = True
        self.opr.par.parseLine('<link xtargets="s1;" id="SL1"/> ')
        ret = self.opr.par.readPair()
        self.assertEqual(ret, -1)

    def test_AlignmentParser_readPair_returns_1_if_alignment_is_valid_and_write_mode_is_links(self):
        self.opr.par.args.wm = "links"
        self.opr.par.parseLine("<s>")
        self.opr.par.parseLine('<link xtargets="s1;s1" id="SL1"/> ')
        ret = self.opr.par.readPair()
        self.assertEqual(ret, 1)

    def test_AlignmentParser_previous_document_is_closed_before_next_is_opened(self):
        printer = OpusRead(["-d", "Books", "-s", "en", "-t", "eo"])
        printer.printPairs()
        self.assertEqual(True, True)

    def test_PairPrinter_printPair_normal(self):
        sPair = ('(src)="s4">Chapter 1 Mr. Sherlock Holmes', '(trg)="s4">Herra Sherlock Holmes .')
        self.assertEqual(self.opr.printPair(sPair), '(src)="s4">Chapter 1 Mr. Sherlock Holmes\n(trg)="s4">Herra Sherlock' + \
                                                    ' Holmes .\n================================')
    
    def test_PairPrinter_printPair_tmx(self):
        self.opr.par.args.wm = "tmx"
        sPair = ('\t\t<tu>\n\t\t\t<tuv xml:lang="en"><seg>Chapter 1 Mr. Sherlock Holmes</seg></tuv>', '\t\t\t<tuv' + \
                    ' xml:lang="fi"><seg>Herra Sherlock Holmes .</seg></tuv>\n\t\t</tu>')
        self.assertEqual(self.opr.printPair(sPair), '\t\t<tu>\n\t\t\t<tuv xml:lang="en"><seg>Chapter 1 Mr. Sherlock' + \
        ' Holmes</seg></tuv>\n\t\t\t<tuv xml:lang="fi"><seg>Herra Sherlock Holmes .</seg></tuv>\n\t\t</tu>')

    def test_PairPrinter_printPair_moses(self):
        self.opr.par.args.wm = "moses"
        sPair = ('Chapter 1 Mr. Sherlock Holmes', 'Herra Sherlock Holmes .')
        self.assertEqual(self.opr.printPair(sPair), """Chapter 1 Mr. Sherlock Holmes\tHerra Sherlock Holmes .""")

    def test_PairPrinter_printPair_moses_change_delimiter(self):
        self.opr.par.args.wm = "moses"
        self.opr.args.cm = "@"
        sPair = ('Chapter 1 Mr. Sherlock Holmes', 'Herra Sherlock Holmes .')
        self.assertEqual(self.opr.printPair(sPair), """Chapter 1 Mr. Sherlock Holmes@Herra Sherlock Holmes .""")

    def test_PairPrinter_printPair_links(self):
        self.opr.par.args.wm = "links"
        sPair = '<link xtargets="s4;s4" id="SL4"/>'
        self.assertEqual(self.opr.printPair(sPair), '<link xtargets="s4;s4" id="SL4"/>')

    def test_PairPrinter_printPair_empty(self):
        sPair = ('(src)="3">Director PARK Jae-sik', '')
        self.assertEqual(self.opr.printPair(sPair), '(src)="3">Director PARK Jae-sik\n\n================================')

    def test_PairPrinter_writePair_normal(self):
        sPair = ('(src)="s4">Chapter 1 Mr. Sherlock Holmes', '(trg)="s4">Herra Sherlock Holmes .')
        self.assertEqual(self.opr.writePair(sPair), ('(src)="s4">Chapter 1 Mr. Sherlock Holmes\n(trg)="s4">Herra Sherlock' + \
                                                    ' Holmes .\n================================\n', ''))

    def test_PairPrinter_writePair_tmx(self):
        self.opr.par.args.wm = "tmx"
        sPair = ('\t\t<tu>\n\t\t\t<tuv xml:lang="en"><seg>Chapter 1 Mr. Sherlock Holmes</seg></tuv>', '\t\t\t<tuv' + \
                ' xml:lang="fi"><seg>Herra Sherlock Holmes .</seg></tuv>\n\t\t</tu>')
        self.assertEqual(self.opr.writePair(sPair), ('\t\t<tu>\n\t\t\t<tuv xml:lang="en"><seg>Chapter 1 Mr. Sherlock' + \
        ' Holmes</seg></tuv>\n\t\t\t<tuv xml:lang="fi"><seg>Herra Sherlock Holmes .</seg></tuv>\n\t\t</tu>\n', ''))

    def test_PairPrinter_writePair_moses(self):
        self.opr.par.args.wm = "moses"
        sPair = ('Chapter 1 Mr. Sherlock Holmes', 'Herra Sherlock Holmes .')
        self.assertEqual(self.opr.writePair(sPair), ('Chapter 1 Mr. Sherlock Holmes\n',    'Herra Sherlock Holmes .\n'))

    def test_PairPrinter_writePair_links(self):
        self.opr.par.args.wm = "links"
        sPair = '<link xtargets="s4;s4" id="SL4"/>'
        self.assertEqual(self.opr.writePair(sPair), ('<link xtargets="s4;s4" id="SL4"/>\n', ''))

    def test_PairPrinter_writePair_empty(self):
        sPair = ('(src)="3">Director PARK Jae-sik', '')
        self.assertEqual(self.opr.writePair(sPair), ('(src)="3">Director PARK Jae-sik\n\n' + \
                                                    '================================\n', ''))

    def test_normal_xml_write(self):
        OpusRead(["-d", "OpenOffice", "-s", "en_GB", "-t", "fr", "-m", "1", "-w", "test_result"]).printPairs()
        with open("test_result", "r") as f:
            self.assertEqual(f.read(), '\n# en_GB/text/schart/main0000.xml.gz\n# fr/text/schart/main0000.xml.gz\n\n' + \
            '================================\n(src)="stit.1">Charts in $[ officename ]\n(trg)="stit.1">Diagrammes dans' + \
            ' $[officename ]\n================================\n') 

    def test_normal_xml_write_fast(self):
        OpusRead(["-d", "OpenOffice", "-s", "en_GB", "-t", "fr", "-m", "1", "-w", "test_result", "-f"]).printPairs()
        with open("test_result", "r") as f:
            self.assertEqual(f.read(), '\n# en_GB/text/schart/main0000.xml.gz\n# fr/text/schart/main0000.xml.gz\n\n' + \
            '================================\n(src)="stit.1">Charts in $[ officename ]\n(trg)="stit.1">Diagrammes dans' + \
            ' $[officename ]\n================================\n')

    def test_normal_xml_print(self):
        var = self.pairPrinterToVariable(["-d", "OpenOffice", "-s", "en_GB", "-t", "fr", "-m", "1"])
        self.assertEqual(var, '\n# en_GB/text/schart/main0000.xml.gz\n# fr/text/schart/main0000.xml.gz\n\n' + \
        '================================\n(src)="stit.1">Charts in $[ officename ]\n(trg)="stit.1">Diagrammes' + \
        ' dans $[officename ]\n================================\n')

    def test_normal_xml_print_fast(self):
        var = self.pairPrinterToVariable(["-d", "OpenOffice", "-s", "en_GB", "-t", "fr", "-m", "1", "-f"])
        self.assertEqual(var, '\n# en_GB/text/schart/main0000.xml.gz\n# fr/text/schart/main0000.xml.gz\n\n' + \
        '================================\n(src)="stit.1">Charts in $[ officename ]\n(trg)="stit.1">Diagrammes' + \
        ' dans $[officename ]\n================================\n')

    def test_normal_raw_write(self):
        OpusRead(["-d", "OpenOffice", "-s", "en_GB", "-t", "fr", "-m", "1", "-w", "test_result", "-p",
                                "raw"]).printPairs()
        with open("test_result", "r") as f:
            self.assertEqual(f.read(), '\n# en_GB/text/schart/main0000.xml.gz\n# fr/text/schart/main0000.xml.gz\n\n' + \
            '================================\n(src)="stit.1">Charts in $[officename]\n(trg)="stit.1">Diagrammes' + \
            ' dans $[officename]\n================================\n')

    def test_normal_raw_write_fast(self):
        OpusRead(["-d", "OpenOffice", "-s", "en_GB", "-t", "fr", "-m", "1", "-w", "test_result", "-p",
                                "raw", "-f"]).printPairs()
        with open("test_result", "r") as f:
            self.assertEqual(f.read(), '\n# en_GB/text/schart/main0000.xml.gz\n# fr/text/schart/main0000.xml.gz\n\n' + \
            '================================\n(src)="stit.1">Charts in $[officename]\n(trg)="stit.1">Diagrammes' + \
            ' dans $[officename]\n================================\n')
    
    def test_normal_raw_print(self):
        var = self.pairPrinterToVariable(["-d", "OpenOffice", "-s", "en_GB", "-t", "fr", "-m", "1", "-p", "raw"])
        self.assertEqual(var, '\n# en_GB/text/schart/main0000.xml.gz\n# fr/text/schart/main0000.xml.gz\n\n' + \
        '================================\n(src)="stit.1">Charts in $[officename]\n(trg)="stit.1">Diagrammes' + \
        ' dans $[officename]\n================================\n')

    def test_normal_raw_print_fast(self):
        var = self.pairPrinterToVariable(["-d", "OpenOffice", "-s", "en_GB", "-t", "fr", "-m", "1", "-p", "raw", "-f"])
        self.assertEqual(var, '\n# en_GB/text/schart/main0000.xml.gz\n# fr/text/schart/main0000.xml.gz\n\n' + \
        '================================\n(src)="stit.1">Charts in $[officename]\n(trg)="stit.1">Diagrammes' + \
        ' dans $[officename]\n================================\n')

    def test_normal_raw_print_OpenSubtitles(self):
        var = self.pairPrinterToVariable("-d OpenSubtitles -s eo -t kk -m 1 -p raw".split())
        self.assertEqual(var, '\n# eo/2001/245429/5818397.xml.gz\n# kk/2001/245429/6899218.xml.gz\n\n' + \
                         '================================\n(src)="1">Filmo de "Studio Ghibli"\n(trg)="1">ГИБЛИ" ' + \
                         'студиясы\n================================\n')

    def test_normal_raw_print_OpenSubtitles_fast(self):
        var = self.pairPrinterToVariable("-d OpenSubtitles -s eo -t kk -m 1 -p raw -f".split())
        self.assertEqual(var, '\n# eo/2001/245429/5818397.xml.gz\n# kk/2001/245429/6899218.xml.gz\n\n' + \
                         '================================\n(src)="1">Filmo de "Studio Ghibli"\n(trg)="1">ГИБЛИ" ' + \
                         'студиясы\n================================\n')
        
    def test_normal_parsed_write(self):
        OpusRead(["-d", "DGT", "-s", "en", "-t", "es", "-m", "1", "-p", "parsed", "-pa", "-sa", "upos,feats,lemma", "-ta", "upos,feats,lemma", "-w", "test_result"]).printPairs()
        with open("test_result", "r") as f:
            self.assertEqual(f.read(), '\n# en/12005S_TTE.xml.gz\n# es/12005S_TTE.xml.gz\n\n================================' + \
            '\n(src)="1">Treaty|NOUN|Number=Sing|treaty\n(trg)="1">Tratado|VERB|Gender=Masc|Number=Sing|VerbForm=Part|tratado' + \
            '\n================================\n')

    def test_normal_parsed_write_fast(self):
        OpusRead(["-d", "DGT", "-s", "en", "-t", "es", "-m", "1", "-p", "parsed", "-pa", "-sa", "upos,feats,lemma", "-ta", "upos,feats,lemma", "-w",
                                "test_result", "-f"]).printPairs()
        with open("test_result", "r") as f:
            self.assertEqual(f.read(), '\n# en/12005S_TTE.xml.gz\n# es/12005S_TTE.xml.gz\n\n================================' + \
            '\n(src)="1">Treaty|NOUN|Number=Sing|treaty\n(trg)="1">Tratado|VERB|Gender=Masc|Number=Sing|VerbForm=Part|tratado' + \
            '\n================================\n')

    def test_normal_parsed_print(self):
        var = self.pairPrinterToVariable(["-d", "DGT", "-s", "en", "-t", "es", "-m", "1", "-p", "parsed", "-pa", "-sa", "upos,feats,lemma", "-ta", "upos,feats,lemma"])
        self.assertEqual(var, '\n# en/12005S_TTE.xml.gz\n# es/12005S_TTE.xml.gz\n\n================================' + \
            '\n(src)="1">Treaty|NOUN|Number=Sing|treaty\n(trg)="1">Tratado|VERB|Gender=Masc|Number=Sing|VerbForm=Part|tratado' + \
            '\n================================\n')

    def test_normal_parsed_print_fast(self):
        var = self.pairPrinterToVariable(["-d", "DGT", "-s", "en", "-t", "es", "-m", "1", "-p", "parsed", "-pa", "-sa", "upos,feats,lemma", "-ta", "upos,feats,lemma", "-f"])
        self.assertEqual(var, '\n# en/12005S_TTE.xml.gz\n# es/12005S_TTE.xml.gz\n\n================================' + \
            '\n(src)="1">Treaty|NOUN|Number=Sing|treaty\n(trg)="1">Tratado|VERB|Gender=Masc|Number=Sing|VerbForm=Part|tratado' + \
            '\n================================\n')
        
    def test_normal_parsed_print_all_attributes(self):
        var = self.pairPrinterToVariable(["-d", "DGT", "-s", "en", "-t", "es", "-m", "1", "-p", "parsed", "-pa", "-sa", "all_attrs", "-ta", "all_attrs"])
        self.assertEqual(var, '\n# en/12005S_TTE.xml.gz\n# es/12005S_TTE.xml.gz\n\n================================' + \
            '\n(src)="1">Treaty|root|Number=Sing|0|1.1|treaty|SpaceAfter=No|NOUN|NOUN\n(trg)="1">Tratado|root|Gender=Masc|Number=Sing|VerbForm=Part|0|1.1|tratado|SpaceAfter=No|VERB' + \
            '\n================================\n')
        
    def test_normal_parsed_print_all_attributes_fast(self):
        var = self.pairPrinterToVariable(["-d", "DGT", "-s", "en", "-t", "es", "-m", "1", "-p", "parsed", "-pa", "-sa", "all_attrs", "-ta", "all_attrs", "-f"])
        self.assertEqual(var, '\n# en/12005S_TTE.xml.gz\n# es/12005S_TTE.xml.gz\n\n================================' + \
            '\n(src)="1">Treaty|root|Number=Sing|0|1.1|treaty|SpaceAfter=No|NOUN|NOUN\n(trg)="1">Tratado|root|Gender=Masc|Number=Sing|VerbForm=Part|0|1.1|tratado|SpaceAfter=No|VERB' + \
            '\n================================\n')

    def test_tmx_xml_write(self):
        OpusRead(["-d", "OpenOffice", "-s", "en_GB", "-t", "fr", "-m", "1", "-w", "test_result", "-wm",
                                "tmx"]).printPairs()
        with open("test_result", "r") as f:
            self.assertEqual(f.read(), '<?xml version="1.0" encoding="utf-8"?>\n<tmx version="1.4.">\n' + \
            '<header srclang="en_GB"\n\tadminlang="en"\n\tsegtype="sentence"\n\tdatatype="PlainText" />' + \
            '\n\t<body>\n\t\t<tu>\n\t\t\t<tuv xml:lang="en_GB"><seg>Charts in $[ officename ]</seg></tuv>' + \
            '\n\t\t\t<tuv xml:lang="fr"><seg>Diagrammes dans $[officename ]</seg></tuv>\n\t\t</tu>\n\t</body>' + \
            '\n</tmx>')

    def test_tmx_xml_write_fast(self):
        OpusRead(["-d", "OpenOffice", "-s", "en_GB", "-t", "fr", "-m", "1", "-w", "test_result", "-wm",
                                "tmx", "-f"]).printPairs()
        with open("test_result", "r") as f:
            self.assertEqual(f.read(), '<?xml version="1.0" encoding="utf-8"?>\n<tmx version="1.4.">\n' + \
            '<header srclang="en_GB"\n\tadminlang="en"\n\tsegtype="sentence"\n\tdatatype="PlainText" />' + \
            '\n\t<body>\n\t\t<tu>\n\t\t\t<tuv xml:lang="en_GB"><seg>Charts in $[ officename ]</seg></tuv>' + \
            '\n\t\t\t<tuv xml:lang="fr"><seg>Diagrammes dans $[officename ]</seg></tuv>\n\t\t</tu>\n\t</body>' + \
            '\n</tmx>')

    def test_tmx_xml_print(self):
        var = self.pairPrinterToVariable(["-d", "OpenOffice", "-s", "en_GB", "-t", "fr", "-m", "1", "-wm", "tmx"])
        self.assertEqual(var, '<?xml version="1.0" encoding="utf-8"?>\n<tmx version="1.4.">\n' + \
            '<header srclang="en_GB"\n\tadminlang="en"\n\tsegtype="sentence"\n\tdatatype="PlainText" />' + \
            '\n\t<body>\n\t\t<tu>\n\t\t\t<tuv xml:lang="en_GB"><seg>Charts in $[ officename ]</seg></tuv>' + \
            '\n\t\t\t<tuv xml:lang="fr"><seg>Diagrammes dans $[officename ]</seg></tuv>\n\t\t</tu>\n\t</body>' + \
            '\n</tmx>\n')

    def test_tmx_xml_print_fast(self):
        var = self.pairPrinterToVariable(["-d", "OpenOffice", "-s", "en_GB", "-t", "fr", "-m", "1", "-wm", "tmx", "-f"])
        self.assertEqual(var, '<?xml version="1.0" encoding="utf-8"?>\n<tmx version="1.4.">\n' + \
            '<header srclang="en_GB"\n\tadminlang="en"\n\tsegtype="sentence"\n\tdatatype="PlainText" />' + \
            '\n\t<body>\n\t\t<tu>\n\t\t\t<tuv xml:lang="en_GB"><seg>Charts in $[ officename ]</seg></tuv>' + \
            '\n\t\t\t<tuv xml:lang="fr"><seg>Diagrammes dans $[officename ]</seg></tuv>\n\t\t</tu>\n\t</body>' + \
            '\n</tmx>\n')

    def test_tmx_raw_write(self):
        OpusRead(["-d", "OpenOffice", "-s", "en_GB", "-t", "fr", "-m", "1", "-w", "test_result", "-wm",
                                "tmx", "-p", "raw"]).printPairs()
        with open("test_result", "r") as f:
            self.assertEqual(f.read(), '<?xml version="1.0" encoding="utf-8"?>\n<tmx version="1.4.">\n' + \
            '<header srclang="en_GB"\n\tadminlang="en"\n\tsegtype="sentence"\n\tdatatype="PlainText" />' + \
            '\n\t<body>\n\t\t<tu>\n\t\t\t<tuv xml:lang="en_GB"><seg>Charts in $[officename]</seg></tuv>' + \
            '\n\t\t\t<tuv xml:lang="fr"><seg>Diagrammes dans $[officename]</seg></tuv>\n\t\t</tu>\n\t</body>' + \
            '\n</tmx>')
    
    def test_tmx_raw_write_fast(self):
        OpusRead(["-d", "OpenOffice", "-s", "en_GB", "-t", "fr", "-m", "1", "-w", "test_result", "-wm",
                                "tmx", "-p", "raw", "-f"]).printPairs()
        with open("test_result", "r") as f:
            self.assertEqual(f.read(), '<?xml version="1.0" encoding="utf-8"?>\n<tmx version="1.4.">\n' + \
            '<header srclang="en_GB"\n\tadminlang="en"\n\tsegtype="sentence"\n\tdatatype="PlainText" />' + \
            '\n\t<body>\n\t\t<tu>\n\t\t\t<tuv xml:lang="en_GB"><seg>Charts in $[officename]</seg></tuv>' + \
            '\n\t\t\t<tuv xml:lang="fr"><seg>Diagrammes dans $[officename]</seg></tuv>\n\t\t</tu>\n\t</body>' + \
            '\n</tmx>')

    def test_tmx_raw_print(self):
        var = self.pairPrinterToVariable(["-d", "OpenOffice", "-s", "en_GB", "-t", "fr", "-m", "1", "-wm", "tmx", "-p", "raw"])
        self.assertEqual(var, '<?xml version="1.0" encoding="utf-8"?>\n<tmx version="1.4.">\n' + \
            '<header srclang="en_GB"\n\tadminlang="en"\n\tsegtype="sentence"\n\tdatatype="PlainText" />' + \
            '\n\t<body>\n\t\t<tu>\n\t\t\t<tuv xml:lang="en_GB"><seg>Charts in $[officename]</seg></tuv>' + \
            '\n\t\t\t<tuv xml:lang="fr"><seg>Diagrammes dans $[officename]</seg></tuv>\n\t\t</tu>\n\t</body>' + \
            '\n</tmx>\n')

    def test_tmx_raw_print_fast(self):
        var = self.pairPrinterToVariable(["-d", "OpenOffice", "-s", "en_GB", "-t", "fr", "-m", "1", "-wm", "tmx", "-p", "raw",
                                            "-f"])
        self.assertEqual(var, '<?xml version="1.0" encoding="utf-8"?>\n<tmx version="1.4.">\n' + \
            '<header srclang="en_GB"\n\tadminlang="en"\n\tsegtype="sentence"\n\tdatatype="PlainText" />' + \
            '\n\t<body>\n\t\t<tu>\n\t\t\t<tuv xml:lang="en_GB"><seg>Charts in $[officename]</seg></tuv>' + \
            '\n\t\t\t<tuv xml:lang="fr"><seg>Diagrammes dans $[officename]</seg></tuv>\n\t\t</tu>\n\t</body>' + \
            '\n</tmx>\n')

    def test_tmx_parsed_write(self):
        OpusRead(["-d", "DGT", "-s", "en", "-t", "es", "-m", "1", "-w", "test_result", "-wm",
                                "tmx", "-p", "parsed", "-pa", "-sa", "upos,feats,lemma", "-ta", "upos,feats,lemma"]).printPairs()
        with open("test_result", "r") as f:
            self.assertEqual(f.read(), '<?xml version="1.0" encoding="utf-8"?>\n<tmx version="1.4.">\n<header srclang="en"' + \
        '\n\tadminlang="en"\n\tsegtype="sentence"\n\tdatatype="PlainText" />\n\t<body>\n\t\t<tu>\n\t\t\t<tuv' + \
        ' xml:lang="en"><seg>Treaty|NOUN|Number=Sing|treaty</seg></tuv>\n\t\t\t<tuv' + \
        ' xml:lang="es"><seg>Tratado|VERB|Gender=Masc|Number=Sing|VerbForm=Part|tratado</seg></tuv>\n\t\t</tu>\n\t' + \
        '</body>\n</tmx>')

    def test_tmx_parsed_write_fast(self):
        OpusRead(["-d", "DGT", "-s", "en", "-t", "es", "-m", "1", "-w", "test_result", "-wm",
                                "tmx", "-p", "parsed", "-pa", "-sa", "upos,feats,lemma", "-ta", "upos,feats,lemma", "-f"]).printPairs()
        with open("test_result", "r") as f:
            self.assertEqual(f.read(), '<?xml version="1.0" encoding="utf-8"?>\n<tmx version="1.4.">\n<header srclang="en"' + \
        '\n\tadminlang="en"\n\tsegtype="sentence"\n\tdatatype="PlainText" />\n\t<body>\n\t\t<tu>\n\t\t\t<tuv' + \
        ' xml:lang="en"><seg>Treaty|NOUN|Number=Sing|treaty</seg></tuv>\n\t\t\t<tuv' + \
        ' xml:lang="es"><seg>Tratado|VERB|Gender=Masc|Number=Sing|VerbForm=Part|tratado</seg></tuv>\n\t\t</tu>\n\t' + \
        '</body>\n</tmx>') 

    def test_tmx_parsed_print(self):
        var = self.pairPrinterToVariable(["-d", "DGT", "-s", "en", "-t", "es", "-m", "1", "-wm", "tmx", "-p", "parsed", "-pa", "-sa", "upos,feats,lemma", "-ta", "upos,feats,lemma"])
        self.assertEqual(var, '<?xml version="1.0" encoding="utf-8"?>\n<tmx version="1.4.">\n<header srclang="en"' + \
        '\n\tadminlang="en"\n\tsegtype="sentence"\n\tdatatype="PlainText" />\n\t<body>\n\t\t<tu>\n\t\t\t<tuv' + \
        ' xml:lang="en"><seg>Treaty|NOUN|Number=Sing|treaty</seg></tuv>\n\t\t\t<tuv' + \
        ' xml:lang="es"><seg>Tratado|VERB|Gender=Masc|Number=Sing|VerbForm=Part|tratado</seg></tuv>\n\t\t</tu>\n\t</body>\n' + \
        '</tmx>\n')

    def test_tmx_parsed_print_fast(self):
        var = self.pairPrinterToVariable(["-d", "DGT", "-s", "en", "-t", "es", "-m", "1", "-wm", "tmx", "-p", "parsed", "-pa", "-sa", "upos,feats,lemma", "-ta", "upos,feats,lemma",
                                            "-f"])
        self.assertEqual(var, '<?xml version="1.0" encoding="utf-8"?>\n<tmx version="1.4.">\n<header srclang="en"' + \
        '\n\tadminlang="en"\n\tsegtype="sentence"\n\tdatatype="PlainText" />\n\t<body>\n\t\t<tu>\n\t\t\t<tuv' + \
        ' xml:lang="en"><seg>Treaty|NOUN|Number=Sing|treaty</seg></tuv>\n\t\t\t<tuv' + \
        ' xml:lang="es"><seg>Tratado|VERB|Gender=Masc|Number=Sing|VerbForm=Part|tratado</seg></tuv>\n\t\t</tu>\n\t</body>\n' + \
        '</tmx>\n')

    def test_moses_xml_write(self):
        OpusRead(["-d", "OpenOffice", "-s", "en_GB", "-t", "fr", "-m", "1", "-w", "test.src,test.trg", "-wm",
                                "moses"]).printPairs()
        with open("test.src", "r") as f:
            self.assertEqual(f.read(), 'Charts in $[ officename ]\n')
        with open("test.trg", "r") as f:
            self.assertEqual(f.read(), 'Diagrammes dans $[officename ]\n')

    def test_moses_xml_write_fast(self):
        OpusRead(["-d", "OpenOffice", "-s", "en_GB", "-t", "fr", "-m", "1", "-w", "test.src,test.trg", "-wm",
                                "moses", "-f"]).printPairs()
        with open("test.src", "r") as f:
            self.assertEqual(f.read(), 'Charts in $[ officename ]\n')
        with open("test.trg", "r") as f:
            self.assertEqual(f.read(), 'Diagrammes dans $[officename ]\n')

    def test_moses_xml_print(self):
        var = self.pairPrinterToVariable(["-d", "OpenOffice", "-s", "en_GB", "-t", "fr", "-m", "1", "-wm", "moses"])
        self.assertEqual(var, 'Charts in $[ officename ]\tDiagrammes dans $[officename ]\n')

    def test_moses_xml_print_fast(self):
        var = self.pairPrinterToVariable(["-d", "OpenOffice", "-s", "en_GB", "-t", "fr", "-m", "1", "-wm", "moses", "-f"])
        self.assertEqual(var, 'Charts in $[ officename ]\tDiagrammes dans $[officename ]\n')
    
    def test_moses_raw_write(self):
        OpusRead(["-d", "OpenOffice", "-s", "en_GB", "-t", "fr", "-m", "1", "-w", "test.src,test.trg", "-wm",
                                "moses", "-p", "raw"]).printPairs()
        with open("test.src", "r") as f:
            self.assertEqual(f.read(), 'Charts in $[officename]\n')
        with open("test.trg", "r") as f:
            self.assertEqual(f.read(), 'Diagrammes dans $[officename]\n')

    def test_moses_raw_write_fast(self):
        OpusRead(["-d", "OpenOffice", "-s", "en_GB", "-t", "fr", "-m", "1", "-w", "test.src,test.trg", "-wm",
                                "moses", "-p", "raw", "-f"]).printPairs()
        with open("test.src", "r") as f:
            self.assertEqual(f.read(), 'Charts in $[officename]\n')
        with open("test.trg", "r") as f:
            self.assertEqual(f.read(), 'Diagrammes dans $[officename]\n')

    def test_moses_raw_print(self):
        var = self.pairPrinterToVariable(["-d", "OpenOffice", "-s", "en_GB", "-t", "fr", "-m", "1", "-wm", "moses", "-p", "raw"])
        self.assertEqual(var, 'Charts in $[officename]\tDiagrammes dans $[officename]\n')

    def test_moses_raw_print_fast(self):
        var = self.pairPrinterToVariable(["-d", "OpenOffice", "-s", "en_GB", "-t", "fr", "-m", "1", "-wm", "moses", "-p", "raw",
                                        "-f"])
        self.assertEqual(var, 'Charts in $[officename]\tDiagrammes dans $[officename]\n')

    def test_moses_parsed_write(self):
        OpusRead(["-d", "DGT", "-s", "en", "-t", "es", "-m", "1", "-w", "test.src,test.trg", "-wm",
                                "moses", "-p", "parsed", "-pa", "-sa", "upos,feats,lemma", "-ta", "upos,feats,lemma"]).printPairs()
        with open("test.src", "r") as f:
            self.assertEqual(f.read(), 'Treaty|NOUN|Number=Sing|treaty\n')
        with open("test.trg", "r") as f:
            self.assertEqual(f.read(), 'Tratado|VERB|Gender=Masc|Number=Sing|VerbForm=Part|tratado\n')

    def test_moses_parsed_write_fast(self):
        OpusRead(["-d", "DGT", "-s", "en", "-t", "es", "-m", "1", "-w", "test.src,test.trg", "-wm",
                                "moses", "-p", "parsed", "-pa", "-sa", "upos,feats,lemma", "-ta", "upos,feats,lemma", "-f"]).printPairs()
        with open("test.src", "r") as f:
            self.assertEqual(f.read(), 'Treaty|NOUN|Number=Sing|treaty\n')
        with open("test.trg", "r") as f:
            self.assertEqual(f.read(), 'Tratado|VERB|Gender=Masc|Number=Sing|VerbForm=Part|tratado\n')

    def test_moses_parsed_print(self):
        var = self.pairPrinterToVariable(["-d", "DGT", "-s", "en", "-t", "es", "-m", "1", "-wm", "moses", "-p", "parsed", "-pa", "-sa", "upos,feats,lemma", "-ta", "upos,feats,lemma"])
        self.assertEqual(var, 'Treaty|NOUN|Number=Sing|treaty\tTratado|VERB|Gender=Masc|Number=Sing|VerbForm=Part|tratado\n')

    def test_moses_parsed_print_fast(self):
        var = self.pairPrinterToVariable(["-d", "DGT", "-s", "en", "-t", "es", "-m", "1", "-wm", "moses", "-p", "parsed", "-pa", "-sa", "upos,feats,lemma", "-ta", "upos,feats,lemma",
                                          "-f"])
        self.assertEqual(var, 'Treaty|NOUN|Number=Sing|treaty\tTratado|VERB|Gender=Masc|Number=Sing|VerbForm=Part|tratado\n')

    def test_links_write(self):
        OpusRead(["-d", "OpenOffice", "-s", "en_GB", "-t", "fr", "-m", "1", "-w", "test_result", "-wm",
                                "links"]).printPairs()
        with open("test_result", "r") as f:
            self.assertEqual(f.read(), '<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE cesAlign PUBLIC "-//CES//DTD' + \
            ' XML cesAlign//EN" "">\n<cesAlign version="1.0">\n <linkGrp targType="s" toDoc="fr/text/schart/main0000.xml.gz"' + \
            ' fromDoc="en_GB/text/schart/main0000.xml.gz">\n<link certainty="3.118182" xtargets="stit.1;stit.1" id="SL1" />' + \
            '\n </linkGrp>\n</cesAlign>')

    def test_links_print(self):
        var = self.pairPrinterToVariable(["-d", "OpenOffice", "-s", "en_GB", "-t", "fr", "-m", "1", "-wm", "links"])
        self.assertEqual(var, '<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE cesAlign PUBLIC "-//CES//DTD' + \
            ' XML cesAlign//EN" "">\n<cesAlign version="1.0">\n <linkGrp targType="s" toDoc="fr/text/schart/main0000.xml.gz"' + \
            ' fromDoc="en_GB/text/schart/main0000.xml.gz">\n<link certainty="3.118182" xtargets="stit.1;stit.1" id="SL1" />' + \
            '\n </linkGrp>\n</cesAlign>\n')

    def test_iteration_stops_at_the_end_of_the_document_even_if_max_is_not_filled(self):
        var = self.pairPrinterToVariable(["-d", "Books", "-s", "en", "-t", "fi", "-S", "5", "-T", "2", "-m", "5"])
        self.assertEqual(var,'\n# en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz\n# fi/Doyle_Arthur_Conan-Hound_of_the_' + \
                        'Baskervilles.xml.gz\n\n================================\n(src)="s942.0">" So I think .\n(src)="s9' + \
                        '42.1">But if we can only trace L. L. it should clear up the whole business .\n(src)="s942.2">We h' + \
                        'ave gained that much .\n(src)="s942.3">We know that there is someone who has the facts if we can ' + \
                        'only find her .\n(src)="s942.4">What do you think we should do ? "\n(trg)="s942.0">" Niin minäkin' + \
                        ' ajattelen , mutta jos voisitte saada tuon L. L : n käsiinne , niin olisi paljon voitettu , ja onh' + \
                        'an edullista jo tietääkin , että on olemassa joku nainen , joka tuntee asian oikean laidan , jos ' + \
                        'vaan voimme saada hänet ilmi .\n(trg)="s942.1">Mitä arvelette nyt olevan tekeminen ? "\n=========' + \
                        '=======================\n')

    def test_use_given_sentence_alignment_file(self):
        OpusRead(["-d", "Books", "-s", "en", "-t", "fi", "-S", "5", "-T", "2", "-wm", "links", "-w", "testlinks"]).printPairs()
        var = self.pairPrinterToVariable(["-d", "Books", "-s", "en", "-t", "fi", "-af", "testlinks"])
        self.assertEqual(var,'\n# en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz\n# fi/Doyle_Arthur_Conan-Hound_of_the_' + \
                        'Baskervilles.xml.gz\n\n================================\n(src)="s942.0">" So I think .\n(src)="s9' + \
                        '42.1">But if we can only trace L. L. it should clear up the whole business .\n(src)="s942.2">We h' + \
                        'ave gained that much .\n(src)="s942.3">We know that there is someone who has the facts if we can ' + \
                        'only find her .\n(src)="s942.4">What do you think we should do ? "\n(trg)="s942.0">" Niin minäkin' + \
                        ' ajattelen , mutta jos voisitte saada tuon L. L : n käsiinne , niin olisi paljon voitettu , ja onh' + \
                        'an edullista jo tietääkin , että on olemassa joku nainen , joka tuntee asian oikean laidan , jos ' + \
                        'vaan voimme saada hänet ilmi .\n(trg)="s942.1">Mitä arvelette nyt olevan tekeminen ? "\n=========' + \
                        '=======================\n')
        
    
    def test_checks_first_whether_documents_are_in_path(self):
        with open("testlinks", "w") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE cesAlign PUBLIC "-//CES//DTD XML cesAlign//EN" "">'+ \
            '\n<cesAlign version="1.0">\n<linkGrp fromDoc="test_en.gz" toDoc="test_fi.gz" >\n<link xtargets="s1;s1"/>\n </'+ \
            'linkGrp>+\n</cesAlign>')
        with open("test_en", "w") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n<text>\n <body>\n<s id="s1">\n <w>test_en1</w>\n <w>test_en2' + \
            '</w>\n</s>\n </body>\n</text>')
        with open("test_fi", "w") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n<text>\n <body>\n<s id="s1">\n <w>test_fi1</w>\n <w>test_fi2' + \
            '</w>\n</s>\n </body>\n</text>')
        var = self.pairPrinterToVariable(["-d", "Books", "-s", "en", "-t", "fi", "-af", "testlinks"])
        self.assertEqual(var, '\n# test_en.gz\n# test_fi.gz\n\n================================\n(src)="s1">test_en1 test_en2\n' + \
                        '(trg)="s1">test_fi1 test_fi2\n================================\n')

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
        var  = self.printSentencesToVariable(["-d", "Books", "-l", "fi", "-p"])
        self.assertEqual(var[-145:], '("s1493.9")>Saanko sitten pyytää sinua laittautumaan valmiiksi puolessa tunnissa , niin'+ \
        ' menemme samalla tiellä Marciniin syömään päivällistä ? "\n')

    def test_printing_sentences_with_limit(self):
        var = self.printSentencesToVariable(["-d", "Books", "-l", "fi", "-m", "1", "-p"])
        self.assertEqual(var, '\n# Books/xml/fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml\n\n("s1")>Source :' + \
                    ' Project Gutenberg\n')

    def test_printing_sentences_without_ids(self):
        var = self.printSentencesToVariable(["-d", "Books", "-l", "fi", "-m", "1", "-i", "-p"])
        self.assertEqual(var, '\n# Books/xml/fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml\n\nSource :' + \
                    ' Project Gutenberg\n')
        
    def test_print_annotations(self):
        var = self.printSentencesToVariable("-d Books -l en -m 1 -i -p -pa".split())
        self.assertEqual(var, '\n# Books/xml/en/Hugo_Victor-Notre_Dame_de_Paris.xml\n\nSource|NN|source :|:|: ' + \
                         'Project|NNP|Project GutenbergTranslation|NNP :|:|: Isabel|NNP|Isabel F.|NNP|F. HapgoodAudiobook|NNP ' + \
                         'available|NN|available here|RB|here\n')

    def test_print_annotations_all_attributes(self):
        var = self.printSentencesToVariable("-d Books -l en -m 1 -i -p -pa -sa all_attrs".split())
        self.assertEqual(var, '\n# Books/xml/en/Hugo_Victor-Notre_Dame_de_Paris.xml\n\nSource|NN|w1.1|source|NN|NN ' + \
                         ':|:|w1.2|:|:|: Project|NNP|w1.3|Project|NNP|NP GutenbergTranslation|NNP|w1.4|NNP|NP ' + \
                         ':|:|w1.5|:|:|: Isabel|NNP|w1.6|Isabel|NNP|NP F.|NNP|w1.7|F.|NNP|NP HapgoodAudiobook|NNP|w1.8|NNP|NP ' + \
                         'available|JJ|w1.9|available|NN|JJ here|RB|w1.10|here|RB|RB\n')

    def test_print_xml(self):
        var = self.printSentencesToVariable("-d Books -l eo -m 1".split())
        self.assertEqual(var[-53:], '\n <w id="w1.8">,</w> \n <w id="w1.9">M.A.</w>\n</s>\n  \n')
        
    def test_printing_specific_file(self):
        var = self.printSentencesToVariable(["-d", "Books", "-l", "eo", "-m", "1", "-i", "-p", "-f",
                                             "Books/xml/eo/Carroll_Lewis-Alice_in_wonderland.xml"])
        self.assertEqual(var, '\n# Books/xml/eo/Carroll_Lewis-Alice_in_wonderland.xml\n\nSource : Project GutenbergTranslation : E.L. KEARNEY , M.A.\n')
        
if __name__ == "__main__":
    unittest.main()
