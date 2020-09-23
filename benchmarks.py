import time
import opustools
import cProfile

print(opustools.__path__)

from opustools import OpusRead

def printResults(**arguments):
    avg_time = 0
    for i in range(3):
        start = time.time()
        eprinter = OpusRead(**arguments)
        eprinter.printPairs()
        #cProfile.runctx('eprinter.printPairs()', globals=globals(), locals=locals())
        end = time.time()
        total_time = end-start
        avg_time += total_time
        print("%.4f" % float(total_time), "s")
    print("%.4f" % (avg_time/3), 's')

print("Corpus: Books, 3654 alignment pairs, source: en, target: fi, all alignments ")
print("Exhaustive parser:")
printResults(directory='Books', source='en', target='fi', write=['books_en_fi'], write_mode='moses')

print("Corpus: Books, 129305 alignment pairs, source: en, target: fr, all alignments")
print("Exhaustive parser:")
printResults(directory='Books', source='en', target='fr', write=['books_en_fr'], write_mode='moses')

print("Corpus: Books, 3654 alignment pairs, source: en, target: fi, 10 alignments")
print("Exhaustive parser:")
printResults(directory='Books', source='en', target='fi', write=['books_en_fi_10'], maximum=10)

print("Corpus: Books, 129305 alignment pairs, source: en, target: fr, 10 alignments")
print("Exhaustive parser:")
printResults(directory='Books', source='en', target='fr', write=['books_en_fr_10'], maximum=10)

print("Corpus: Books, 3654 alignment pairs, source: en, target: fi, all alignments, preprocessing raw")
print("Exhaustive parser:")
printResults(directory='Books', source='en', target='fi', write=['books_en_fi_raw'], write_mode='moses', preprocess='raw')

print("Corpus: Books, 129305 alignment pairs, source: en, target: fr, all alignments, preprocessing raw")
print("Exhaustive parser:")
printResults(directory='Books', source='en', target='fr', write='books_en_fr_raw', write_mode='moses', preprocess='raw')

print("Corpus: Books, 3654 alignment pairs, source: en, target: fi, 10 alignments, preprocessing raw")
print("Exhaustive parser:")
printResults(directory='Books', source='en', target='fi', write=['books_en_fi_raw_10'], write_mode='moses', preprocess='raw', maximum=10)

print("Corpus: Books, 129305 alignment pairs, source: en, target: fr, 10 alignments, preprocessing raw")
print("Exhaustive parser:")
printResults(directory='Books', source='en', target='fr', write=['books_en_fr_raw_10'], write_mode='moses', preprocess='raw', maximum=10)

print("Corpus: Europarl, 1974717 alignment pairs, source: en, target: fi, all alignments, preprocessing raw")
print("Exhaustive parser:")
printResults(directory='Europarl', source='en', target='fi', write=['europarl_en_fi_raw'], write_mode='moses', release='v7', preprocess='raw')

print("Corpus: Europarl, 1974717 alignment pairs, source: en, target: fi, all alignments ")
print("Exhaustive parser:")
printResults(directory='Europarl', source='en', target='fi', write=['europarl_en_fi'], write_mode='moses', release='v7')

print("Corpus: Tatoeba, 383 alignment pairs, source: br, target: en, all alignments, preprocessing raw")
printResults(directory='Tatoeba', source='br', target='en', write=['tatoeba_br_en_raw'], write_mode='moses', preprocess='raw')

print("Corpus: Tatoeba, 383 alignment pairs, source: br, target: en, all alignments, preprocessing xml")
printResults(directory='Tatoeba', source='br', target='en', write=['tatoeba_br_en'], write_mode='moses')
