# OpusTools

Tools for accessing and processing OPUS data.

opus_read: read parallel data sets and convert to different output formats
opus_cat: extract given OPUS document from release data

## opus_read

### Usage

In `your_script.py`, first import the package:

`import opustools_pkg`

If you want to give the arguments on command line: initialize `OpusRead` with an empty argument list:

```
opus_reader = opustools_pkg.OpusRead([])
opus_reader.printPairs()
```

and then run in terminal:

`python3 your_script.py -d Books -s en -t fi`

You can alternatively initialize `OpusRead` with arguments in a list:

```
opus_reader = opustools_pkg.OpusRead(["-d", "Books", "-s", "en", "-t", "fi"])
opus_reader.printPairs()
```

and in terminal:

`python3 your_script.py`

Read sentence alignment in XCES align format
`python3 your_script.py -d Books -s en -t fi`

Print alignments with alignment certainty > LinkThr=0
`python3 your_script.py -d MultiUN -s en -t es -a certainty -tr 0`

Print first 10 alignment pairs:
`python3 your_script.py -d Books -s en -t fi -m 10`

Print XCES align format of all 1:1 sentence alignments:
`python3 your_script.py -d Books -s en -t fi -S 1 -T 1 -wm links`


```
python3 opus_read.py [-h] -d D -s S -t T [-r R] [-p P] [-m M] [-S S] [-T T] [-a A] [-tr TR]
			[-ln] [-w W] [-wm WM] [-f] [-rd RD] [-af AF] [-cm CM] [-pa] [-ca CA]
```

arguments:
```
-h, --help	show this help message and exit
-d D		Corpus name
-s S		Source language
-t T		Target language
-r R		Release (default=latest)
-p P		Pre-process-type (raw, xml or parsed, default=xml)
-m M		Maximum number of alignments
-S S		Maximum number of source sentences in alignments (range is allowed, eg. -S 1-2)
-T T		Maximum number of target sentences in alignments (range is allowed, eg. -T 1-2)
-a A		Set attribute for filttering
-tr TR		Set threshold for an attribute
-ln		Leave non-alignments out
-w W		Write to file. Enter two file names separated by a comma when writing in moses 
		format (e.g. -w moses.src,moses.trg). Otherwise enter one file name.
-wm WM		Set writing mode (normal, moses, tmx, links)
-f		Fast parsing. Faster than normal parsing, if you print a small part of the whole 
		corpus, but requires the sentence ids in alignment files to be in sequence.
-rd RD		Change root directory (default=/proj/nlpl/data/OPUS/)
-af AF		Use given alignment file
-cm CM		Change moses delimiter (default=tab)
-pa		Print annotations, if they exist
-ca CA		Change annotation delimiter (default=|)
```
### Description

`opus_read.py` is a simple script to read sentence alignments stored in XCES align format and prints the aligned sentences to STDOUT. It requires monolingual alignments of sentences in linked XML files. Linked XML files are specified in the "toDoc" and "fromDoc" attributes (see below).

```
<cesAlign version="1.0">
 <linkGrp targType="s" toDoc="source1.xml" fromDoc="target1.xml">
   <link certainty="0.88" xtargets="s1.1 s1.2;s1.1" id="SL1" />
   ....
 <linkGrp targType="s" toDoc="source2.xml" fromDoc="target2.xml">
   <link certainty="0.88" xtargets="s1.1;s1.1" id="SL1" />
```

Several parameters can be set to filter the alignments and to print only certain types of alignments.

`opus_read.py` can also be used to filter the XCES alignment files and to print the remaining links in the same
XCES align format. Set the "-wm" flag to "links" to enable this mode.

`opus_read.py` reads the alignments from zip files. Starting up the script might take some time, if the zip files are large (for example OpenSubtitles in OPUS)

`opus_read.py` uses `ExhaustiveSentenceParser` by default. This means that each time a `<linkGrp>` tag is found, the corresponding source and target documents are read through and each sentence is stored in a hashmap with the sentence id as the key. This allows the reader to read alignment files that have sentence ids in non-sequential order. Each time a `<linkGrp>` tag is found, the script pauses printing for a second to read through the source and target documents. The duration of the pause depends on the size of the source and target documents.

Using the "-f" flag allows the usage of `SentenceParser`, which is faster than ExhaustiveSentenceParser in cases where only a small part of a corpus is read. `SentenceParser` does not store the sentences in a hashmap. Rather, when it finds a `<link>` tag, it iterates through a sentence file until a sentence id is matched with the sentence id found in the `<link>` tag. SentenceParser can not go backwards, which means that if the ids are not in sequential order in the alignment file, the parser will not find alignment pairs after the sentence is sequence breaks. SentenceParser is less reliable than ExhaustiveSentenceParser, but using the "-f" flag is beneficial when the whole corpus does not need to be scanned, in other words, while using the "-m" flag.


## opus_cat

### Description

`opus_cat.py` reads a document from OPUS and prints it to STDOUT.

### Usage

In `your_script.py`, first import the package:

`import opustools_pkg`

If you want to give the arguments on command line: initialize `OpusCat` with an empty argument list:

```
opus_cat = opustools_pkg.OpusCat([])
opus_cat.printSentences()
```

and then run in terminal:

`python3 your_script.py -d Books -s en`

You can alternatively initialize `OpusCat` with arguments in a list:

```
opus_cat = opustools_pkg.OpusRead(["-d", "Books", "-l", "en"])
opus_cat.printSentences()
```

and in terminal:

`python3 your_script.py`

```
python3 opus_cat.py [-h] -d D -l L [-i] [-m M]
```

arguments:
```
-h, --help	show this help message and exit
-d D		Corpus name
-l L		Language
-i		Print without ids
-m M		Maximum number of sentences
```

