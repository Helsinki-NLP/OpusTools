import unittest
import tempfile
import shutil
import os

from opustools.parse.block_parser import BlockParser
from opustools.parse.new_alignment_parser import NewAlignmentParser

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

    @classmethod
    def tearDownClass(self):
        shutil.rmtree(self.tempdir)

    def test_get_link(self):
        ap = NewAlignmentParser(self.align_path)
        link = ap.get_link()
        self.assertEqual(link.attributes['xtargets'], 's1;s1')
        self.assertEqual(link.parent.attributes['fromDoc'],
            'en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz')
        self.assertEqual(link.parent.attributes['toDoc'],
            'fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz')

        link = ap.get_link()
        self.assertEqual(link.attributes['xtargets'], ';s2')
        self.assertEqual(link.parent.attributes['fromDoc'],
            'en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz')
        self.assertEqual(link.parent.attributes['toDoc'],
            'fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz')

        link = ap.get_link()
        self.assertEqual(link.attributes['xtargets'], 's21;')
        self.assertEqual(link.parent.attributes['fromDoc'], 'en/2.xml.gz')
        self.assertEqual(link.parent.attributes['toDoc'], 'fi/2.xml.gz')

        link = ap.get_link()
        self.assertEqual(link.attributes['xtargets'], 's0 s1;s2 s3')
        self.assertEqual(link.parent.attributes['fromDoc'], 'en/2.xml.gz')
        self.assertEqual(link.parent.attributes['toDoc'], 'fi/2.xml.gz')
