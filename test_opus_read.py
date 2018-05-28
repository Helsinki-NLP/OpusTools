import unittest
import io
import sys
import opus_read
import xml.parsers.expat

class TestOpusRead(unittest.TestCase):

	@classmethod
	def setUpClass(self):
		self.opr = opus_read.PairPrinter(["-d", "Books", "-s", "en", "-t", "fi"])
		self.opr.par.initializeSentenceParsers({"fromDoc": "en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz",\
											 "toDoc": "fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz"})
		self.fastopr = opus_read.PairPrinter(["-d", "Books", "-s", "en", "-t", "fi", "-f"])
		self.fastopr.par.initializeSentenceParsers({"fromDoc": "en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz",\
											 "toDoc": "fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz"})

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

	def pairPrinterToVariable(self, arguments):
		printout = io.StringIO()
		sys.stdout = printout
		opus_read.PairPrinter(arguments).printPairs()
		sys.stdout = sys.__stdout__
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
		rawprint = opus_read.PairPrinter(["-d", "Books", "-s", "en", "-t", "fi", "-p", "raw"])
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
		fastprinter = opus_read.PairPrinter(["-d", "Books", "-s", "en", "-t", "fi", "-p", "raw", "-f"])
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
		self.assertEqual(self.opr.printPair(sPair), """Chapter 1 Mr. Sherlock Holmes	Herra Sherlock Holmes .""")

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
		self.assertEqual(self.opr.writePair(sPair), ('Chapter 1 Mr. Sherlock Holmes\n',	'Herra Sherlock Holmes .\n'))

	def test_PairPrinter_writePair_links(self):
		self.opr.par.args.wm = "links"
		sPair = '<link xtargets="s4;s4" id="SL4"/>'
		self.assertEqual(self.opr.writePair(sPair), ('<link xtargets="s4;s4" id="SL4"/>\n', ''))

	def test_PairPrinter_writePair_empty(self):
		sPair = ('(src)="3">Director PARK Jae-sik', '')
		self.assertEqual(self.opr.writePair(sPair), ('(src)="3">Director PARK Jae-sik\n\n' + \
													'================================\n', ''))
	
if __name__ == "__main__":
	unittest.main()
