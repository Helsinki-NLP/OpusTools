import unittest
import tempfile
import shutil
import os
import gzip

from opustools.parse.block_parser import BlockParser
from opustools.parse.new_alignment_parser import AlignmentParser
from opustools.util import file_open

class TestAlignmentParser(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.tempdir = tempfile.mkdtemp()

        self.align_path = os.path.join(self.tempdir, 'align.xml')
        with open(self.align_path, 'w') as align_xml:
            align_xml.write("""<?xml version="1.0" encoding="utf-8"?>
                <!DOCTYPE cesAlign PUBLIC "-//CES//DTD XML cesAlign//EN" "">
                <cesAlign version="1.0">
                <linkGrp targType="s" fromDoc="en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz" toDoc="fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz" >
                <link xtargets="s1;s1" id="SL1"/>
                <link xtargets=";s2" id="SL2"/>
                  </linkGrp>
                <linkGrp targType="s" fromDoc="en/2.xml.gz" toDoc="fi/2.xml.gz" >
                <link xtargets="s21;" id="SL1"/>
                <link xtargets="s0 s1;s2 s3" id="SL2"/>
                  </linkGrp>
                </cesAlign>
                """)

        self.align_path_gz = os.path.join(self.tempdir, 'align.xml.gz')
        with gzip.open(self.align_path_gz, 'wb') as align_xml_gz:
            align_xml_gz.write(b"""<?xml version="1.0" encoding="utf-8"?>
                <!DOCTYPE cesAlign PUBLIC "-//CES//DTD XML cesAlign//EN" "">
                <cesAlign version="1.0">
                <linkGrp targType="s" fromDoc="en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz" toDoc="fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz" >
                <link xtargets="s1;s1" id="SL1"/>
                <link xtargets=";s2" id="SL2"/>
                  </linkGrp>
                <linkGrp targType="s" fromDoc="en/2.xml.gz" toDoc="fi/2.xml.gz" >
                <link xtargets="s21;" id="SL1"/>
                <link xtargets="s0 s1;s2 s3" id="SL2"/>
                  </linkGrp>
                </cesAlign>
                """)

    @classmethod
    def tearDownClass(self):
        shutil.rmtree(self.tempdir)

    def test_get_link(self):
        ap = AlignmentParser(file_open(self.align_path))
        link = ap.get_tag('link')
        self.assertEqual(link.attributes['xtargets'], 's1;s1')
        self.assertEqual(link.parent.attributes['fromDoc'],
            'en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz')
        self.assertEqual(link.parent.attributes['toDoc'],
            'fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz')

        link = ap.get_tag('link')
        self.assertEqual(link.attributes['xtargets'], ';s2')
        self.assertEqual(link.parent.attributes['fromDoc'],
            'en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz')
        self.assertEqual(link.parent.attributes['toDoc'],
            'fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz')

        link = ap.get_tag('link')
        self.assertEqual(link.attributes['xtargets'], 's21;')
        self.assertEqual(link.parent.attributes['fromDoc'], 'en/2.xml.gz')
        self.assertEqual(link.parent.attributes['toDoc'], 'fi/2.xml.gz')

        link = ap.get_tag('link')
        self.assertEqual(link.attributes['xtargets'], 's0 s1;s2 s3')
        self.assertEqual(link.parent.attributes['fromDoc'], 'en/2.xml.gz')
        self.assertEqual(link.parent.attributes['toDoc'], 'fi/2.xml.gz')

        ap.bp.close_document()

    def test_get_link_gz(self):
        ap = AlignmentParser(file_open(self.align_path_gz))
        link = ap.get_tag('link')
        self.assertEqual(link.attributes['xtargets'], 's1;s1')
        self.assertEqual(link.parent.attributes['fromDoc'],
            'en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz')
        self.assertEqual(link.parent.attributes['toDoc'],
            'fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz')

        link = ap.get_tag('link')
        self.assertEqual(link.attributes['xtargets'], ';s2')
        self.assertEqual(link.parent.attributes['fromDoc'],
            'en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz')
        self.assertEqual(link.parent.attributes['toDoc'],
            'fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz')

        link = ap.get_tag('link')
        self.assertEqual(link.attributes['xtargets'], 's21;')
        self.assertEqual(link.parent.attributes['fromDoc'], 'en/2.xml.gz')
        self.assertEqual(link.parent.attributes['toDoc'], 'fi/2.xml.gz')

        link = ap.get_tag('link')
        self.assertEqual(link.attributes['xtargets'], 's0 s1;s2 s3')
        self.assertEqual(link.parent.attributes['fromDoc'], 'en/2.xml.gz')
        self.assertEqual(link.parent.attributes['toDoc'], 'fi/2.xml.gz')

        ap.bp.close_document()

    def test_collect_links(self):
        ap = AlignmentParser(file_open(self.align_path))
        attrs, src_set, trg_set, last = ap.collect_links()
        self.assertEqual(attrs, [{'id': 'SL1', 'xtargets': 's1;s1'},
            {'id': 'SL2', 'xtargets': ';s2'}])
        self.assertEqual(src_set, {'s1', ''})
        self.assertEqual(trg_set, {'s1', 's2'})
        attrs, src_set, trg_set, last = ap.collect_links(last)
        self.assertEqual(attrs, [{'id': 'SL1', 'xtargets': 's21;'},
            {'id': 'SL2', 'xtargets': 's0 s1;s2 s3'}])
        self.assertEqual(src_set, {'s21', 's0', 's1'})
        self.assertEqual(trg_set, {'', 's2', 's3'})
        attrs, src_set, trg_set, last = ap.collect_links(last)
        self.assertEqual(attrs, [])
        self.assertEqual(src_set, set())
        self.assertEqual(trg_set, set())

