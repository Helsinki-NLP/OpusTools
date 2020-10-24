# OpusTools

Tools for accessing and processing OPUS data.

* opus_read: read parallel data sets and convert to different output formats
* opus_express: Create test/dev/train sets from OPUS data.
* opus_cat: extract given OPUS document from release data
* opus_get: download files from OPUS
* opus_langid: add language ids to sentences in xml files in zip archives

### Installation:

`pip install opustools`

---

## opus_read

### Usage

```
usage: opus_read [-h] -d corpus_name -s langid -t langid [-r version]
                 [-p {raw,xml,parsed}] [-m M] [-S S] [-T T] [-a attribute]
                 [-tr TR] [-ln] [-w file_name [file_name ...]]
                 [-wm {normal,moses,tmx,links}] [-pn] [-rd path_to_dir]
                 [-af path_to_file] [-sz path_to_zip] [-tz path_to_zip]
                 [-cm delimiter] [-pa] [-sa attribute [attribute ...]]
                 [-ta attribute [attribute ...]] [-ca delimiter]
                 [--src_cld2 lang_id score] [--trg_cld2 lang_id score]
                 [--src_langid lang_id score] [--trg_langid lang_id score]
                 [-id file_name] [-q] [-dl DOWNLOAD_DIR] [-pi] [-n regex]
                 [-N regex] [-v]
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
-m MAXIMUM, --maximum MAXIMUM   Maximum number of alignments
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
-rd path_to_dir, --root_directory path_to_dir
                    Change root directory (default=/projappl/nlpl/data/OPUS)
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
                    attributes use -sa all_attrs (default=pos lem)
-ta attribute [attribute ...], --target_annotations attribute [attribute ...]
                    Set target sentence annotation attributes to be
                    printed, e.g. -ta pos lem. To print all available
                    attributes use -ta all_attrs (default=pos lem)
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
-n regex              Get only documents that match the regex
-N regex              Skip all documents that match the regex
-v, --verbose       Print prorgess messages
```

### Description

`opus_read` is a script to read sentence alignments stored in XCES align format and print the aligned sentences to STDOUT. It requires monolingual alignments of sentences in linked XML files. Linked XML files are specified in the "toDoc" and "fromDoc" attributes (see below).

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

**Examples:**

Read sentence alignment in XCES align format. Necessary files will be downloaded if they are not found locally:

`opus_read --directory RF --source en --target sv`

Read sentences with specific preprocessing type. (default is xml, which is tokenized text):

`opus_read --directory RF --source en --target sv --preprocess raw`

Leave non-alignments (pairs with no sentences on one side) out

```
opus_read --directory RF \
    --source en \
    --target sv \
    --preprocess raw\
    --leave_non_alignments_out
```

Print first 10 alignment pairs:

`opus_read --directory RF --source en --target sv -m 10`

Print XCES align format of all 1:1 sentence alignments:

```
opus_read --directory RF \
    --source en \
    --target sv \
    --src_range 1 \
    --tgt_range 1
```

Print alignments with alignment certainty greater than 1.1:

```
opus_read --directory RF \
    --source en \
    --target sv \
    --attribute certainty \
    --threshold 1.1
```

Write results to file:

`opus_read --directory RF --source en --target sv --write result.txt`

Write with different output format:

```
opus_read --directory RF \
    --source en \
    --target sv \
    --write result.tmx\
    --write_mode tmx
```

Write moses format to one file:

```
opus_read --directory RF \
    --source en \
    --target sv \
    --write en-sv.txt\
    --write_mode moses
```

or to two files:

```
opus_read --directory RF \
    --source en \
    --target sv \
    --write en-sv.en en-sv.sv \
    --write_mode moses
```

Read sentences using your alignment file. First create an alignment file, for example:

```
opus_read --directory RF \
    --source en \
    --target sv \
    --attribute certainty \
    --threshold 1.1 \
    --write_mode links \
    --write en-sv.links
```

Then use the created alignment file:

`opus_read --directory RF --source en --target sv --alignment_file en-sv.links`

Annotations can be printed with `--print_annotations` if they are included in the sentence files. To print all annotation attributes, specify this with `--source_annotations` and `--target_annotations` flags:

```
opus_read --directory RF \
    --source en \
    --target sv \
    --print_annotations \
    --source_annotations all_attrs \
    --target_annotations all_attrs
```

Sentences can be filtered by their language id labels and confidence score. First, the language ids need to be added to the sentence files with `opus_langid`. If you have run the previous examples, you should have `RF_latest_xml_en.zip` and `RF_latest_xml_sv.zip` in your current working directory. Apply `opus_langid` to these files:

```
opus_langid --file_path RF_latest_xml_en.zip
opus_langid --file_path RF_latest_xml_sv.zip
```

If you want to add language labels and scores to raw sentence files, you have to use the `--preprocess raw` flag:

```
opus_langid --file_path RF_latest_raw_en.zip --preprocess raw
opus_langid --file_path RF_latest_raw_sv.zip --preprocess raw
```

Now you can filter by language ids. This example uses both cld2 and langid.py language detection confidence scores:

```
opus_read --directory RF \
    --source en \
    --target sv \
    --src_cld2 en 0.99 \
    --trg_cld2 sv 0.99 \
    --src_langid en 1 \
    --trg_langid sv 1
```

**You can also import the module to your python script:**

In `your_script.py`, first import the package:

`import opustools`

Initialize OpusRead:

```
opus_reader = opustools.OpusRead(
    directory='Books',
    source='en',
    target='fi')
opus_reader.printPairs()
```

and then run:

`python3 your_script.py`

---

## opus_express

### Usage

```
usage: opus_express [-h] [-f] -s lang_id -t lang_id
                    [-c [coll_name [coll_name ...]]]
                    [--root-dir /path/to/OPUS] [--download-dir /path/to/dir]
                    [--test-override /path/to/file] [--test-quota num_sents]
                    [--dev-quota num_sents] [--doc-bounds] [--quality-aware]
                    [--overlap-threshold min_pct] [--preserve-inline-tags]
                    [--shuffle] [--test-set filename] [--dev-set filename]
                    [--train-set filename] [-q]
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
                      (Check http://opus.nlpl.eu/opusapi/?corpora=True for 
                      an up-to-date list)
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
                      (default:`/projappl/nlpl/data/OPUS')
--download-dir /path/to/dir
                      Directory for downloaded OPUS corpus files
                      (default:`.')
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
--preserve-inline-tags
                      preserve inline timestamp tags in aligned samples
                      (default: False)
--shuffle             shuffle samples (incompatible with `--doc-bounds')
                      (default: False)
--test-set filename   filename stub for output test set (default: `test')
--dev-set filename    filename stub for output development set (default:
                      `dev')
--train-set filename  filename stub for output training set (default:
                      `train')
-q                    Download necessary files without prompting "(y/n)"
                      (default: False)
```

### Description

All aboard the OPUS Express! Create test/dev/train sets from OPUS data.

---

## opus_cat

### Usage

```
usage: opus_cat [-h] -d DIRECTORY -l LANGUAGE [-i] [-m MAXIMUM] [-p]
                [-f FILE_NAME] [-r RELEASE] [-pa]
                [-sa SET_ATTRIBUTE [SET_ATTRIBUTE ...]]
                [-ca CHANGE_ANNOTATION_DELIMITER] [-rd path_to_dir]
                [-dl DOWNLOAD_DIR]
```

arguments:

```
-h, --help            show this help message and exit
-d DIRECTORY, --directory DIRECTORY
                      Corpus name
-l LANGUAGE, --language LANGUAGE
                      Language
-i, --no_ids          Print without ids when using -p
-m MAXIMUM, --maximum MAXIMUM
                      Maximum number of sentences
-p, --plain           Print in plain txt
-f FILE_NAME, --file_name FILE_NAME
                      File name (if not given, prints all files)
-r RELEASE, --release RELEASE
                      Release (default=latest)
-pa, --print_annotations
                      Print annotations, if they exist
-sa SET_ATTRIBUTE [SET_ATTRIBUTE ...], --set_attribute SET_ATTRIBUTE [SET_ATTRIBUTE ...]
                      Set sentence annotation attributes to be printed, e.g.
                      -sa pos lem. To print all available attributes use -sa
                      all_attrs (default=pos,lem)
-ca CHANGE_ANNOTATION_DELIMITER, --change_annotation_delimiter CHANGE_ANNOTATION_DELIMITER
                      Change annotation delimiter (default=|)
-rd path_to_dir, --root_directory path_to_dir
                      Change root directory (default=/proj/nlpl/data/OPUS)
-dl DOWNLOAD_DIR, --download_dir DOWNLOAD_DIR
                      Set download directory (default=current directory)
```

### Description

Read a document from OPUS and print to STDOUT

**Examples:**

Read a corpus:

```
opus_cat --directory RF --language en
```

Read with output in plain text:

```
opus_cat --directory RF --language en --plain
```

Read with output in plain text including annotations:

```
opus_cat --directory RF --language en --plain --print_annotations
```

Read a specific file in a corpus:

```
opus_cat --directory RF --language en --file_name RF/xml/en/1996.xml
```

---

## opus_get

### Usage

```
usage: opus_get [-h] [-s SOURCE] [-t TARGET] [-d DIRECTORY] [-r RELEASE]
                [-p {raw,xml,parsed}] [-l] [-dl DOWNLOAD_DIR] [-q]
```

arguments:

```
-h, --help            show this help message and exit
-s SOURCE, --source SOURCE
                      Source language
-t TARGET, --target TARGET
                      Target language
-d DIRECTORY, --directory DIRECTORY
                      Corpus name
-r RELEASE, --release RELEASE
                      Release
-p {raw,xml,parsed}, --preprocess {raw,xml,parsed}
                      Preprocess type
-l, --list_resources  List resources
-dl DOWNLOAD_DIR, --download_dir DOWNLOAD_DIR
                      Set download directory (default=current directory)
-q, --suppress_prompts
                      Download necessary files without prompting "(y/n)"
```

### Description

Download files from OPUS

**Examples:**

List available files in RF corpus for en-sv language pair:

```
opus_get --directory RF --source en --target sv --list
```

Download RF corpus for en-sv:

```
opus_get --directory RF --source en --target sv
```

You can specify the directory to which the files will be downloaded:

```
opus_get --directory RF --source en --target sv --download_dir RF_files
```

List all files in RF that include English:

```
opus_get --directory RF --source en --list
```

List all files for all language pairs in RF:

```
opus_get --directory RF --list
```

List all en-sv files in the whole OPUS:

```
opus_get --source en --target sv --list
```

---

## opus_langid

### Usage

```
usage: opus_langid [-h] -f FILE_PATH [-t TARGET_FILE_PATH] [-v] [-s]
```

arguments:

```
-h, --help            show this help message and exit
-f FILE_PATH, --file_path FILE_PATH
                      File path
-t TARGET_FILE_PATH, --target_file_path TARGET_FILE_PATH
                      Target file path. By default, the original file is
                      edited
-v, --verbosity       Verbosity. -v: print current xml file
-s, --suppress_errors
                      Suppress error messages in language detection
```

### Description

Add language ids to sentences in plain xml files or xml files in zip archives using [pycld2](https://pypi.org/project/pycld2/) and [langid.py](https://github.com/saffsd/langid.py). This is required in order to be able to filter sentences by their language ids and confidence scores as described in the examples of `opus_read`.

If you have run the `opus_read` examples, you should have `RF_latest_xml_en.zip` and `RF_latest_xml_sv.zip` in your current working directory. Apply `opus_langid` to these files:

```
opus_langid --file_path RF_latest_xml_en.zip
opus_langid --file_path RF_latest_xml_sv.zip
```

If you want to add language labels and scores to raw sentence files, you have to use the `--preprocess raw` flag:

```
opus_langid --file_path RF_latest_raw_en.zip --preprocess raw
opus_langid --file_path RF_latest_raw_sv.zip --preprocess raw
```

