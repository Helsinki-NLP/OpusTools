import unittest
import zipfile

from opustools_pkg.opus_langid import OpusLangid

class TestOpusLangid(unittest.TestCase):

    def run_opuslangid_and_assertEqual(self, source, target, lines, iszip,
            correct_line):
        if target != None:
            command = '-f {0} -t {1}'.format(source, target)
            result = target
        else:
            command = '-f ' + source
            result = source

        langids = OpusLangid(command.split())
        langids.processFiles()

        if iszip:
            with zipfile.ZipFile(source, 'r') as zip_arc:
                with zip_arc.open(zip_arc.filelist[0]) as xml_file:
                    for i in range(lines):
                        line = xml_file.readline()
        else:
            with open(result, 'r') as result:
                for i in range(lines):
                    line = result.readline()
            self.assertEqual(line, correct_line)

    def test_plain_xml(self):
        self.run_opuslangid_and_assertEqual('xml_fi.xml', 'result.xml', 10,
                False, ('<s id="s1" cld2="en" cld2conf="0.96" langid="de" '
                    'langidconf="0.66">\n'))

        self.run_opuslangid_and_assertEqual('result.xml', None, 10, False,
                ('<s id="s1" cld2="en" cld2conf="0.96" langid="de" '
                    'langidconf="0.66">\n'))

    def test_plain_raw(self):
        self.run_opuslangid_and_assertEqual('raw_fi.xml', 'result.xml', 11,
                False, ('  <s id="s1" cld2="en" cld2conf="0.96" langid="de" '
                    'langidconf="0.66">Source: Project Gutenberg</s>\n'))

        self.run_opuslangid_and_assertEqual('result.xml', None, 11, False,
                ('  <s id="s1" cld2="en" cld2conf="0.96" langid="de" '
                    'langidconf="0.66">Source: Project Gutenberg</s>\n'))

    def test_plain_osraw(self):
        self.run_opuslangid_and_assertEqual('osrawfi.xml', 'result.xml', 12,
                False, ('  <s id="3" cld2="fi" cld2conf="0.96" langid="fi" '
                    'langidconf="1.0">\n'))

        self.run_opuslangid_and_assertEqual('result.xml', None, 12, False,
                ('  <s id="3" cld2="fi" cld2conf="0.96" langid="fi" '
                'langidconf="1.0">\n'))

    def test_zip_xml(self):
        self.run_opuslangid_and_assertEqual('xml_fi.zip', 'result.zip', 10,
                True, ('<s id="s1" cld2="en" cld2conf="0.96" langid="de" '
                    'langidconf="0.66">\n'))

        self.run_opuslangid_and_assertEqual('result.zip', None, 10, True,
                ('<s id="s1" cld2="en" cld2conf="0.96" langid="de" '
                    'langidconf="0.66">\n'))

    def test_zip_raw(self):
        self.run_opuslangid_and_assertEqual('raw_fi.zip', 'result.zip', 11,
                True, ('  <s id="s1" cld2="en" cld2conf="0.96" langid="de" '
                    'langidconf="0.66">Source: Project Gutenberg</s>\n'))

        self.run_opuslangid_and_assertEqual('result.zip', None, 11, True,
                ('  <s id="s1" cld2="en" cld2conf="0.96" langid="de" '
                    'langidconf="0.66">Source: Project Gutenberg</s>\n'))

    def test_zip_osraw(self):
        self.run_opuslangid_and_assertEqual('osrawfi.zip', 'result.zip', 12,
                True, ('  <s id="3" cld2="fi" cld2conf="0.96" langid="fi" '
                    'langidconf="1.0">\n'))

        self.run_opuslangid_and_assertEqual('result.zip', None, 12, True,
                ('  <s id="3" cld2="fi" cld2conf="0.96" langid="fi" '
                'langidconf="1.0">\n'))

if __name__ == '__main__':
    unittest.main()
