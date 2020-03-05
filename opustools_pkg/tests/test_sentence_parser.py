import unittest
import tempfile
import shutil
import os

from opustools.parse.block_parser import BlockParser
from opustools.parse.exhaustive_sentence_parser import ExhaustiveSentenceParser

class TestSentenceParser(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.tempdir = tempfile.mkdtemp()

        self.books_path = os.path.join(self.tempdir, 'books.xml')
        with open(self.books_path, 'w') as books_xml:
            books_xml.write("""<?xml version="1.0" encoding="utf-8"?>
                <text><head>
                <meta id="1">
                 <w id="w1.1">Notre-Dame</w>
                 <w id="w1.2">de</w>
                 <w id="w1.3">Paris</w>
                 <w id="w1.4">by</w>
                 <w id="w1.5">Victor</w>
                 <w id="w1.6">Hugo</w>
                 <w id="w1.7">Aligned</w>
                 <w id="w1.8">by</w>
                 <w id="w1.9">:</w>
                 <w id="w1.10">Unknown</w>
                 <w id="w1.11">&amp;</w>
                 <w id="w1.12">András</w>
                 <w id="w1.13">Farkas</w>
                 <w id="w1.14">(</w>
                 <w id="w1.15">fully</w>
                 <w id="w1.16">reviewed</w>
                 <w id="w1.17">)</w>
                </meta></head><body>
                <s id="s1">
                 <chunk type="NP" id="c1-1">
                  <w hun="NN" tree="NN" lem="source" pos="NN" id="w1.1">Source</w>
                 </chunk>
                 <w hun=":" tree=":" lem=":" pos=":" id="w1.2">:</w>
                 <chunk type="NP" id="c1-3">
                  <w hun="NNP" tree="NP" lem="Project" pos="NNP" id="w1.3">Project</w>
                  <w hun="NNP" tree="NP" pos="NNP" id="w1.4">GutenbergTranslation</w>
                 </chunk>
                </s>
                """)

        self.books_raw_path = os.path.join(self.tempdir, 'books_raw.xml')
        with open(self.books_raw_path, 'w') as books_raw_xml:
            books_raw_xml.write("""<?xml version="1.0" encoding="UTF-8"?>

                <text>
                 <head>
                  <meta> Notre-Dame de Paris
                 by Victor Hugo
                 Aligned by: Unknown &amp; András Farkas (fully reviewed)
                 </meta>
                 </head>
                 <body>
                  <s id="s1">Source: Project GutenbergTranslation: Isabel F. HapgoodAudiobook available here</s>
                  <s id="s2">Hunchback of Notre-Dame</s>
                  <s id="s3">Victor Hugo</s>
                """)

        self.os_path = os.path.join(self.tempdir, 'os.xml')
        with open(self.os_path, 'w') as os_xml:
            os_xml.write("""<?xml version="1.0" encoding="utf-8"?>
                <document id="4296906">
                  <s id="1">
                    <time id="T1S" value="00:00:05,897" />
                    <w id="1.1">-</w>
                    <w id="1.2">How</w>
                    <w id="1.3">'d</w>
                    <w id="1.4">you</w>
                    <w id="1.5">score</w>
                    <w id="1.6">that</w>
                    <w id="1.7">?</w>
                  </s>
                  <s id="2">
                    <w id="2.1">-</w>
                    <w id="2.2">Mike</w>
                    <w id="2.3">the</w>
                    <w id="2.4">groundskeeper</w>
                    <w id="2.5">.</w>
                    <time id="T1E" value="00:00:08,654" />
                  </s>
                  """)

        self.os_raw_path = os.path.join(self.tempdir, 'os_raw.xml')
        with open(self.os_raw_path, 'w') as os_raw_xml:
            os_raw_xml.write("""<?xml version="1.0" encoding="utf-8"?>
                <document id="4296906">
                  <s id="1">
                    <time id="T1S" value="00:00:05,897" />
                - How'd you score that?
                  </s>
                  <s id="2">
                - Mike the groundskeeper.
                    <time id="T1E" value="00:00:08,654" />
                  </s>
                  """)


    @classmethod
    def tearDownClass(self):
        shutil.rmtree(self.tempdir)

    def test_storeSentences(self):
        sp = ExhaustiveSentenceParser(self.books_path)
        sp.storeSentences()
        self.assertEqual(sp.sentences['s1'][0],
                'Source : Project GutenbergTranslation')
        sp = ExhaustiveSentenceParser(self.books_raw_path, preprocessing='raw')
        sp.storeSentences()
        self.assertEqual(sp.sentences['s1'][0],
                'Source: Project GutenbergTranslation: Isabel F. '
                'HapgoodAudiobook available here')
        sp = ExhaustiveSentenceParser(self.os_path)
        sp.storeSentences()
        self.assertEqual(sp.sentences['1'][0], "- How 'd you score that ?")
        sp = ExhaustiveSentenceParser(self.os_raw_path, preprocessing='raw')
        sp.storeSentences()
        self.assertEqual(sp.sentences['1'][0], "- How'd you score that?")

    def test_getAnnotations(self):
        bp = BlockParser(self.books_path)
        sp = ExhaustiveSentenceParser(self.books_path)
        for i in range(19):
            blocks = bp.get_complete_blocks()
        self.assertEqual(sp.getAnnotations(blocks[0]), '|NN|w1.1|source|NN|NN')
        bp = BlockParser(self.books_path)
        sp = ExhaustiveSentenceParser(self.books_path, anno_attrs=['pos'])
        for i in range(19):
            blocks = bp.get_complete_blocks()
        self.assertEqual(sp.getAnnotations(blocks[0]), '|NN')
