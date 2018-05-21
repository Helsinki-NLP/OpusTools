import unittest
import io
import sys
import opus_read

class TestOpusRead(unittest.TestCase):

	@classmethod
	def setUpClass(self):
		self.opr = opus_read.PairPrinter(["-d", "Books", "-s", "en", "-t", "fi"])
		self.opr.par.initializeSentenceParsers({"fromDoc": "en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz",\
											 "toDoc": "fi/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz"})
	
	@classmethod
	def tearDownClass(self):
		self.opr.par.sPar.document.close()
		self.opr.par.tPar.document.close()
		self.opr.par.closeFiles()
	
	def pairPrinterToValue(self, arguments):
		printout = io.StringIO()
		sys.stdout = printout
		opr = opus_read.PairPrinter(arguments).printPairs()
		sys.stdout = sys.__stdout__
		return printout

	def test_ExhaustiveSentenceParser_initializing(self):
		self.assertEqual(len(self.opr.par.sPar.sentences), 3831)
		self.assertEqual(len(self.opr.par.tPar.sentences), 3757)

	def test_ExhaustiveSentenceParser_getSentence(self):
		self.assertEqual(self.opr.par.sPar.getSentence("s1"), "Source : manybooks.netAudiobook available here")
		self.assertEqual(self.opr.par.tPar.getSentence("s1"), "Source : Project Gutenberg")

		self.assertEqual(self.opr.par.sPar.getSentence("s4"), "Chapter 1 Mr. Sherlock Holmes")
		self.assertEqual(self.opr.par.tPar.getSentence("s4"), "Herra Sherlock Holmes .")

		self.assertEqual(self.opr.par.sPar.getSentence("s5.4"), '" To James Mortimer , M.R.C.S. , from his friends of the C.C.H. , " was engraved upon it , with the date " 1884 . "')
		self.assertEqual(self.opr.par.tPar.getSentence("s5.5"), "James Mortimerille ystäviltänsä C. C. H : ssa ' oli kaiverrettu tuuman-levyiselle , kädensijan alapuolella olevalle hopealevylle , sekä vielä vuosiluku 1884 .")

	def test_ExhaustiveSentenceParser_readSentence_format(self):
		self.assertEqual(self.opr.par.sPar.readSentence(["s1"]), '(src)="s1">Source : manybooks.netAudiobook available here')
		self.assertEqual(self.opr.par.tPar.readSentence(["s1"]), '(trg)="s1">Source : Project Gutenberg')
		self.assertEqual(self.opr.par.sPar.readSentence(["s11.0", "s11.1"]), '(src)="s11.0">" Good ! " said Holmes .\n(src)="s11.1">" Excellent ! "')

'''
	def test_basic_usage(self):
		printout = self.pairPrinterToValue(["-d", "Books", "-s", "en", "-t", "fi"])
		self.assertEqual(printout.getvalue()[-350:], """===============================
(src)="s1493.9">Might I trouble you then to be ready in half an hour , and we can stop at Marcini 's for a little dinner on the way ? "
(trg)="s1493.9">Saanko sitten pyytää sinua laittautumaan valmiiksi puolessa tunnissa , niin menemme samalla tiellä Marciniin syömään päivällistä ? "
================================
""")

	def test_fast_mode(self):
		printout = self.pairPrinterToValue(["-d", "Books", "-s", "en", "-t", "fi", "-f"])
		self.assertEqual(printout.getvalue()[-350:], """===============================
(src)="s1493.9">Might I trouble you then to be ready in half an hour , and we can stop at Marcini 's for a little dinner on the way ? "
(trg)="s1493.9">Saanko sitten pyytää sinua laittautumaan valmiiksi puolessa tunnissa , niin menemme samalla tiellä Marciniin syömään päivällistä ? "
================================
""")

	def test_maximum_number_of_alignments(self):
		printout = self.pairPrinterToValue(["-d", "Books", "-s", "en", "-t", "fi", "-m", "20"])
		self.assertEqual(printout.getvalue()[-199:], """================================
(src)="s11.0">" Good ! " said Holmes .
(src)="s11.1">" Excellent ! "
(trg)="s11">" Se on hyvä " , sanoi Holmes , " erittäin hyvä . "
================================
""")

	def test_maximum_number_of_alignments_fast_mode(self):
		printout = self.pairPrinterToValue(["-d", "Books", "-s", "en", "-t", "fi", "-m", "20", "-f"])
		self.assertEqual(printout.getvalue()[-199:], """================================
(src)="s11.0">" Good ! " said Holmes .
(src)="s11.1">" Excellent ! "
(trg)="s11">" Se on hyvä " , sanoi Holmes , " erittäin hyvä . "
================================
""")
'''
	
		
if __name__ == "__main__":
	unittest.main()
