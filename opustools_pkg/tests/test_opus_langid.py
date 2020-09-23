import os
import unittest
import zipfile
import shutil
import tempfile

from opustools.opus_langid import OpusLangid

class TestOpusLangid(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.tempdir = tempfile.mkdtemp()

        with open(os.path.join(self.tempdir, 'xml_fi.xml'), 'w') as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n<text>\n '
            '<head>\n  <meta> The Hound of the Baskervilles \n by Sir '
            'Arthur Conan Doyle \n Aligned by: András Farkas (fully '
            'reviewed) \n </meta>\n </head>\n <body>\n<s id="s1" '
            'test="test">\n <w id="w1.1">Source</w>\n <w id="w1.2">:</w> '
            '\n <w id="w1.3">Project</w> \n <w id="w1.4">Gutenberg</w>\n<'
            '/s>\n  \n<s id="s2">\n <w id="w2.1">BASKERVILLEN</w> \n <w '
            'id="w2.2">KOIRA</w>\n</s>\n  \n<s id="s3">\n <w '
            'id="w3.1">A.</w> \n <w id="w3.2">Conan</w> \n <w '
            'id="w3.3">Doyle</w> \n <w id="w3.4">ENSIMMÄINEN</w> \n '
            '<w id="w3.5">LUKU</w>\n <w id="w3.6">.</w>\n</s>\n '
            '</body>\n</text>\n')

        with open(os.path.join(self.tempdir, 'raw_fi.xml'), 'w') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n\n<text>\n '
            '<head>\n  <meta> The Hound of the Baskervilles \n by Sir '
            'Arthur Conan Doyle \n Aligned by: András Farkas '
            '(fully reviewed) \n </meta>\n </head>\n <body>\n  <s '
            'id="s1">Source: Project Gutenberg</s>\n  <s '
            'id="s2">BASKERVILLEN KOIRA</s>\n  <s id="s3">A. Conan '
            'Doyle ENSIMMÄINEN LUKU.</s>\n  <s id="s4">Herra Sherlock '
            'Holmes.</s>\n  <p id="p5">\n   <s id="s5.0">Herra Sherlock '
            'Holmes, joka tavallisesti nousi hyvin myöhään ylös aamusin, '
            'paitsi niissä kylläkin useissa tapauksissa, jolloin hän oli '
            'valvonut koko yön, istui aamiaisella.</s>\n   '
            '<s id="s5.1">Minä seisoin matolla tulisijan edessä pitäen '
            'kädessäni keppiä, jonka eräs edellisenä iltana luonamme '
            'käynyt herra oli unohtanut.</s>\n   <s id="s5.2">Se oli '
            'jokseenkin soma ja tukeva, se oli varustettu '
            'sipulinmuotoisella kädensijalla ja näytti oikealta '
            '"tuomarin sauvalta."</s>\n   <s id="s5.3">\'M.R.C.S.</s>\n   '
            '<s id="s5.4">[M.R.C.S. Member of the Royal College of '
            'Surgeons = kuninkaallisen kirurgi-kollegion jäsen.]</s>\n   '
            '<s id="s5.5">James Mortimerille ystäviltänsä C. C. H:ssa\' '
            'oli kaiverrettu tuuman-levyiselle, kädensijan alapuolella '
            'olevalle hopealevylle, sekä vielä vuosiluku 1884.</s>\n   <s '
            'id="s5.6">Juuri sellaista keppiä käyttävät tavallisesti '
            'vanhat perhelääkärit -- se näytti arvokkaalta, vakavalta '
            'ja luottamusta herättävältä.</s>\n  </p>\n </body>\n</text>\n')

        with open(os.path.join(self.tempdir, 'osrawfi.xml'), 'w') as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n<document '
            'id="5763965">\n  <s id="1">\n    <time id="T1S" '
            'value="00:01:48,446" />\nHitto, tämä vuotaa.\n    '
            '<time id="T1E" value="00:01:51,324" />\n  </s>\n  '
            '<s id="2">\n    <time id="T2S" value="00:01:51,366" />\nVoi '
            'itku. \n  </s>\n  <s id="3">\nHaavasta valuu aivokudosta.\n    '
            '<time id="T2E" value="00:01:54,403" />\n  </s>\n  '
            '<s id="4">\n    <time id="T3S" value="00:01:54,446" />\nAntakaa '
            '100 grammaa Mannitolia.\n    <time id="T3E" value="00:01:57,165" '
            '/>\n  </s>\n  <s id="5">\n    <time id="T4S" value="00:01:57,206" '
            '/>\nEntä purskevaimentuma?\n    <time id="T4E" '
            'value="00:01:59,162" />\n  </s>\n  <s id="6">\n    '
            '<time id="T5S" value="00:01:59,206" />\n- Mikä hänen '
            'verenpaineensa on?\n  </s>\n  <meta>\n    <conversion>\n      '
            '<unknown_words>0</unknown_words>\n      '
            '<ignored_blocks>0</ignored_blocks>\n      '
            '<encoding>windows-1252</encoding>\n      '
            '<truecased_words>0</truecased_words>\n      '
            '<sentences>723</sentences>\n      '
            '<corrected_words>0</corrected_words>\n      '
            '<tokens>3762</tokens>\n    </conversion>\n    <subtitle>\n      '
            '<date>2014-07-23</date>\n      '
            '<machine_translated>0</machine_translated>\n      '
            '<duration>00:47:58,675</duration>\n      '
            '<confidence>1.0</confidence>\n      <blocks>546</blocks>\n      '
            '<rating>1.0</rating>\n      <language>Finnish</language>\n      '
            '<version>1</version>\n    </subtitle>\n    <source>\n      '
            '<genre>Comedy,Drama</genre>\n      <duration>60</duration>\n      '
            '<HD>1</HD>\n      <cds>1/1</cds>\n      <year>2003</year>\n    '
            '</source>\n  </meta>\n</document>\n')

        with zipfile.ZipFile(os.path.join(self.tempdir, 'xml_fi.zip'),
                'w') as xmlzip:
            xmlzip.write(os.path.join(self.tempdir, 'xml_fi.xml'))

        with zipfile.ZipFile(os.path.join(self.tempdir, 'raw_fi.zip'),
                'w') as xmlzip:
            xmlzip.write(os.path.join(self.tempdir, 'raw_fi.xml'))

        with zipfile.ZipFile(os.path.join(self.tempdir, 'osrawfi.zip'),
                'w') as xmlzip:
            xmlzip.write(os.path.join(self.tempdir, 'osrawfi.xml'))

    @classmethod
    def tearDownClass(self):
        shutil.rmtree(self.tempdir)

    def run_opuslangid_and_assertEqual(self, source, target, lines, iszip,
            preprocess, correct_line):
        source = os.path.join(self.tempdir, source)
        if target != None:
            target = os.path.join(self.tempdir, target)
            arguments = {'file_path': source, 'target_file_path': target,
                    'preprocess': preprocess}
            result = target
        else:
            arguments = {'file_path': source, 'preprocess': preprocess}
            result = source

        langids = OpusLangid(**arguments)
        langids.processFiles()

        if iszip:
            with zipfile.ZipFile(result, 'r') as zip_arc:
                with zip_arc.open(zip_arc.filelist[0]) as xml_file:
                    for i in range(lines):
                        line = xml_file.readline()
                self.assertEqual(line, correct_line)
        else:
            with open(result, 'r') as result:
                for i in range(lines):
                    line = result.readline()
            self.assertEqual(line, correct_line)

    def test_plain_xml(self):
        self.run_opuslangid_and_assertEqual('xml_fi.xml', 'result.xml', 10,
                False, 'xml', '<s cld2="en" cld2conf="0.96" langid="de" '
                    'langidconf="0.66" id="s1" test="test">\n')

        self.run_opuslangid_and_assertEqual('result.xml', None, 10, False, 'xml',
                '<s cld2="en" cld2conf="0.96" langid="de" '
                    'langidconf="0.66" id="s1" test="test">\n')

    def test_plain_raw(self):
        self.run_opuslangid_and_assertEqual('raw_fi.xml', 'result.xml', 11,
                False, 'raw', '  <s cld2="en" cld2conf="0.96" langid="de" '
                    'langidconf="0.66" id="s1">Source: Project Gutenberg</s>\n')

        self.run_opuslangid_and_assertEqual('result.xml', None, 11, False, 'raw',
                '  <s cld2="en" cld2conf="0.96" langid="de" '
                    'langidconf="0.66" id="s1">Source: Project Gutenberg</s>\n')

    def test_plain_osraw(self):
        self.run_opuslangid_and_assertEqual('osrawfi.xml', 'result.xml', 12,
                False, 'raw', '  <s cld2="fi" cld2conf="0.96" langid="fi" '
                    'langidconf="0.99" id="3">\n')

        self.run_opuslangid_and_assertEqual('result.xml', None, 12, False, 'raw',
                '  <s cld2="fi" cld2conf="0.96" langid="fi" '
                'langidconf="0.99" id="3">\n')

    def test_zip_xml(self):
        self.run_opuslangid_and_assertEqual('xml_fi.zip', 'result.zip', 10,
                True, 'xml', b'<s cld2="en" cld2conf="0.96" langid="de" '
                    b'langidconf="0.66" id="s1" test="test">\n')

        self.run_opuslangid_and_assertEqual('result.zip', None, 10, True, 'xml',
                b'<s cld2="en" cld2conf="0.96" langid="de" '
                    b'langidconf="0.66" id="s1" test="test">\n')

    def test_zip_raw(self):
        self.run_opuslangid_and_assertEqual('raw_fi.zip', 'result.zip', 11,
                True, 'raw', b'  <s cld2="en" cld2conf="0.96" langid="de" '
                    b'langidconf="0.66" id="s1">Source: Project Gutenberg</s>\n')

        self.run_opuslangid_and_assertEqual('result.zip', None, 11, True, 'raw',
                b'  <s cld2="en" cld2conf="0.96" langid="de" '
                    b'langidconf="0.66" id="s1">Source: Project Gutenberg</s>\n')

    def test_zip_osraw(self):
        self.run_opuslangid_and_assertEqual('osrawfi.zip', 'result.zip', 12,
                True, 'raw', b'  <s cld2="fi" cld2conf="0.96" langid="fi" '
                    b'langidconf="0.99" id="3">\n')

        self.run_opuslangid_and_assertEqual('result.zip', None, 12, True, 'raw',
                b'  <s cld2="fi" cld2conf="0.96" langid="fi" '
                b'langidconf="0.99" id="3">\n')

if __name__ == '__main__':
    unittest.main()
