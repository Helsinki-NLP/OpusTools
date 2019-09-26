# OpusTools

Tools for accessing and processing OPUS data.

* opus_read: read parallel data sets and convert to different output formats
* opus_express: Create test/dev/train sets from OPUS data.
* opus_cat: extract given OPUS document from release data
* opus_get: download files from OPUS
* opus_langid: add language ids to sentences in xml files in zip archives

## opus_read

### Usage

```
usage: opus_read [-h] -d corpus_name -s langid -t langid [-r version]
                 [-p {raw,xml,parsed}] [-m M] [-S S] [-T T] [-a attribute]
                 [-tr TR] [-ln] [-w file_name [file_name ...]]
                 [-wm {normal,moses,tmx,links}] [-pn] [-f] [-rd path_to_dir]
                 [-af path_to_file] [-sz path_to_zip] [-tz path_to_zip]
                 [-cm delimiter] [-pa] [-sa attribute [attribute ...]]
                 [-ta attribute [attribute ...]] [-ca delimiter]
                 [--src_cld2 lang_id score] [--trg_cld2 lang_id score]
                 [--src_langid lang_id score] [--trg_langid lang_id score]
                 [-id file_name] [-q] [-dl DOWNLOAD_DIR] [-pi]
```

arguments:

```
-h, --help          show this help message and exit
-d corpus_name, --directory corpus_name
                    Corpus name
-s langid, --source langid
                    Source language
-t langid, --target langid
                    Target language
-r version, --release version
                    Release (default=latest)
-p {raw,xml,parsed}, --preprocess {raw,xml,parsed}
                    Preprocess-type (raw, xml or parsed, default=xml)
-m MAX, --max MAX   Maximum number of alignments
-S SRC_RANGE, --src_range SRC_RANGE
                    Number of source sentences in alignments (range is
                    allowed, eg. -S 1-2)
-T TGT_RANGE, --tgt_range TGT_RANGE
                    Number of target sentences in alignments (range is
                    allowed, eg. -T 1-2)
-a attribute, --attribute attribute
                    Set attribute for filttering
-tr THRESHOLD, --threshold THRESHOLD
                    Set threshold for an attribute
-ln, --leave_non_alignments_out
                    Leave non-alignments out
-w file_name [file_name ...], --write file_name [file_name ...]
                    Write to file. To print moses format in separate
                    files, enter two file names. Otherwise enter one file
                    name.
-wm {normal,moses,tmx,links}, --write_mode {normal,moses,tmx,links}
                    Set write mode
-pn, --print_file_names
                    Print file names when using moses format
-f, --fast          Fast parsing. Faster than normal parsing, if you print
                    a small part of the whole corpus, but requires the
                    sentence ids in alignment files to be in sequence.
-rd path_to_dir, --root_directory path_to_dir
                    Change root directory (default=/proj/nlpl/data/OPUS/)
-af path_to_file, --alignment_file path_to_file
                    Use given alignment file
-sz path_to_zip, --source_zip path_to_zip
                    Use given source zip file
-tz path_to_zip, --target_zip path_to_zip
                    Use given target zip file
-cm delimiter, --change_moses_delimiter delimiter
                    Change moses delimiter (default=tab)
-pa, --print_annotations
                    Print annotations, if they exist
-sa attribute [attribute ...], --source_annotations attribute [attribute ...]
                    Set source sentence annotation attributes to be
                    printed, e.g. -sa pos lem. To print all available
                    attributes use -sa all_attrs (default=pos,lem)
-ta attribute [attribute ...], --target_annotations attribute [attribute ...]
                    Set target sentence annotation attributes to be
                    printed, e.g. -ta pos lem. To print all available
                    attributes use -ta all_attrs (default=pos,lem)
-ca delimiter, --change_annotation_delimiter delimiter
                    Change annotation delimiter (default=|)
--src_cld2 lang_id score
                    Filter source sentences by their cld2 language id
                    labels and confidence score, e.g. en 0.9
--trg_cld2 lang_id score
                    Filter target sentences by their cld2 language id
                    labels and confidence score, e.g. en 0.9
--src_langid lang_id score
                    Filter source sentences by their langid.py language id
                    labels and confidence score, e.g. en 0.9
--trg_langid lang_id score
                    Filter target sentences by their langid.py language id
                    labels and confidence score, e.g. en 0.9
-id file_name, --write_ids file_name
                    Write sentence ids to a file.
-q, --suppress_prompts
                    Download necessary files without prompting "(y/n)"
-dl DOWNLOAD_DIR, --download_dir DOWNLOAD_DIR
                    Set download directory (default=current directory)
-pi, --preserve_inline_tags
                    Preserve inline tags within sentences
```


**Examples:**

Read sentence alignment in XCES align format:

`opus_read -d Books -s en -t fi`

Print alignments with alignment certainty > LinkThr=0:

`opus_read -d MultiUN -s en -t es -a certainty -tr 0`

Print first 10 alignment pairs:

`opus_read -d Books -s en -t fi -m 10`

Print XCES align format of all 1:1 sentence alignments:

`opus_read -d Books -s en -t fi -S 1 -T 1 -wm links`


**You can also import the module to your python script:**

In `your_script.py`, first import the package:

`import opustools_pkg`

If you want to give the arguments on command line, initialize `OpusRead` with an empty argument list:

```
opus_reader = opustools_pkg.OpusRead([])
opus_reader.printPairs()
```

and then run:

`python3 your_script.py -d Books -s en -t fi`

You can alternatively initialize `OpusRead` with arguments in a list:

```
opus_reader = opustools_pkg.OpusRead(["-d", "Books", "-s", "en", "-t", "fi"])
opus_reader.printPairs()
```

and then run:

`python3 your_script.py`

### Description

`opus_read` is a script to read sentence alignments stored in XCES align format and prints the aligned sentences to STDOUT. It requires monolingual alignments of sentences in linked XML files. Linked XML files are specified in the "toDoc" and "fromDoc" attributes (see below).

```
<cesAlign version="1.0">
 <linkGrp targType="s" toDoc="source1.xml" fromDoc="target1.xml">
   <link certainty="0.88" xtargets="s1.1 s1.2;s1.1" id="SL1" />
   ....
 <linkGrp targType="s" toDoc="source2.xml" fromDoc="target2.xml">
   <link certainty="0.88" xtargets="s1.1;s1.1" id="SL1" />
```

Several parameters can be set to filter the alignments and to print only certain types of alignments.

`opus_read` can also be used to filter the XCES alignment files and to print the remaining links in the same
XCES align format. Set the "-wm" flag to "links" to enable this mode.

`opus_read` reads the alignments from zip files. Starting up the script might take some time, if the zip files are large (for example OpenSubtitles in OPUS).

`opus_read` uses `ExhaustiveSentenceParser` by default. This means that each time a `<linkGrp>` tag is found, the corresponding source and target documents are read through and each sentence is stored in a hashmap with the sentence id as the key. This allows the reader to read alignment files that have sentence ids in non-sequential order. Each time a `<linkGrp>` tag is found, the script pauses printing for a second to read through the source and target documents. The duration of the pause depends on the size of the source and target documents.

Using the "-f" flag allows the usage of `SentenceParser`, which is faster than ExhaustiveSentenceParser in cases where only a small part of a corpus is read. `SentenceParser` does not store the sentences in a hashmap. Rather, when it finds a `<link>` tag, it iterates through a sentence file until a sentence id is matched with the sentence id found in the `<link>` tag. SentenceParser can't go backwards, which means that if the ids are not in sequential order in the alignment file, the parser will not find alignment pairs after the sentence id sequence breaks. `SentenceParser` is less reliable than `ExhaustiveSentenceParser`, but using the "-f" flag is beneficial when the whole corpus does not need to be scanned, in other words, when using the "-m" flag.

## opus_express

### Usage

```
usage: opus_express [-h] [-f] -s lang_id -t lang_id
                    [-c [coll_name [coll_name ...]]]
                    [--root-dir /path/to/OPUS] [--test-override /path/to/file]
                    [--test-quota num_sents] [--dev-quota num_sents]
                    [--doc-bounds] [--quality-aware]
                    [--overlap-threshold min_pct] [--shuffle]
                    [--test-set filename] [--dev-set filename]
                    [--train-set filename]
```

arguments:

```
-h, --help            show this help message and exit
-f, --force           suppress warnings (default: False)
-s lang_id, --src-lang lang_id
                      source language (e.g. `en')
-t lang_id, --tgt-lang lang_id
                      target language (e.g. `pt')
-c [coll_name [coll_name ...]], --collections [coll_name [coll_name ...]]
                      OPUS collection(s) to fetch (default: `OpenSubtitles')
                      Collections list: ['ALL', 'ada83', 'Bianet', 'bible-
                      uedin', 'Books', 'CAPES', 'DGT', 'DOGC', 'ECB',
                      'EhuHac', 'Elhuyar', 'EMEA', 'EUbookshop', 'EUconst',
                      'Europarl', 'Finlex', 'fiskmo', 'giga-fren',
                      'GlobalVoices', 'GNOME', 'hrenWaC', 'JRC-Acquis',
                      'KDE4', 'KDEdoc', 'MBS', 'memat', 'MontenegrinSubs',
                      'MPC1', 'MultiUN', 'News-Commentary', 'OfisPublik',
                      'OpenOffice', 'OpenSubtitles', 'ParaCrawl', 'PHP',
                      'QED', 'RF', 'sardware', 'SciELO', 'SETIMES', 'SPC',
                      'Tanzil', 'Tatoeba', 'TED2013', 'TedTalks', 'TEP',
                      'TildeMODEL', 'Ubuntu', 'UN', 'UNPC', 'wikimedia',
                      'Wikipedia', 'WikiSource', 'WMT-News', 'XhosaNavy']
--root-dir /path/to/OPUS
                      Root directory for OPUS
                      (default:`/proj/nlpl/data/OPUS')
--test-override /path/to/file
                      path to file containing resource IDs to reserve for
                      the test set (default: None)
--test-quota num_sents
                      test set size in sentences (default: 10000)
--dev-quota num_sents
                      development set size in sentences (default: 10000)
--doc-bounds          preserve document blocks (also marks document
                      boundaries) (default: False)
--quality-aware       reserve one-to-one aligned samples with high overlap
                      for test/dev sets (incompatible with `--doc-bounds')
                      (default: False)
--overlap-threshold min_pct
                      threshold for alignment overlap in `--quality-aware'
                      mode (default: 0.8)
--shuffle             shuffle samples (incompatible with `--doc-bounds')
                      (default: False)
--test-set filename   filename stub for output test set (default: `test')
--dev-set filename    filename stub for output development set (default:
                      `dev')
--train-set filename  filename stub for output training set (default:
                      `train')
```

### Description

All aboard the OPUS Express! Create test/dev/train sets from OPUS data.

## opus_cat

### Usage

```
usage: opus_cat [-h] -d D -l L [-i] [-m M] [-p] [-f F] [-r R] [-pa]
                [-sa SA [SA ...]] [-ca CA]
```

arguments:

```
-h, --help       show this help message and exit
-d D             Corpus name
-l L             Language
-i               Print without ids when using -p
-m M             Maximum number of sentences
-p               Print in plain txt
-f F             File name (if not given, prints all files)
-r R             Release (default=latest)
-pa              Print annotations, if they exist
-sa SA [SA ...]  Set sentence annotation attributes to be printed, e.g. -sa
                 pos lem. To print all available attributes use -sa
                 all_attrs (default=pos,lem)
-ca CA           Change annotation delimiter (default=|)
```


**You can also import the module to your python script:**

In `your_script.py`, first import the package:

`import opustools_pkg`

If you want to give the arguments on command line, initialize `OpusCat` with an empty argument list:

```
opus_cat = opustools_pkg.OpusCat([])
opus_cat.printSentences()
```

and then run:

`python3 your_script.py -d Books -s en`

You can alternatively initialize `OpusCat` with arguments in a list:

```
opus_cat = opustools_pkg.OpusRead(["-d", "Books", "-l", "en"])
opus_cat.printSentences()
```

and then run:

`python3 your_script.py`

### Description

Read a document from OPUS and print to STDOUT

## opus_get

## Usage

```
opus-get [-h] -s S [-t T] [-d D] [-r R] [-p {raw,xml,parsed}] [-l]
         [-dl DL] [-q]
```

arguments:

```
-h, --help            show this help message and exit
-s S, --source S      Source language
-t T, --target T      Target language
-d D, --directory D   Corpus name
-r R, --release R     Release
-p {raw,xml,parsed}, --preprocess {raw,xml,parsed}
                      Preprocess type
-l, --list            List resources
-dl DL, --download_dir DL
                      Set download directory (default=current directory)
-q, --supress_prompts
                      Download necessary files without prompting "(y/n)"
```


### Description

Download files from OPUS

## opus_langid

## Usage

```
opus_langid [-h] -f F [-t T] [-v] [-s]
```

arguments:

```
-h, --help  show this help message and exit
-f F        File path
-t T        Target file path. By default, the original file is edited
-v          Verbosity. -v: print current xml file
-s          Suppress error messages in language detection
```


### Description

Add language ids to sentences in plain xml files or xml files in zip archives using [pycld2](https://pypi.org/project/pycld2/) and [langid.py](https://github.com/saffsd/langid.py).
