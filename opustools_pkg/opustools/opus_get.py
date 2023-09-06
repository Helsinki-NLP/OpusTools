import urllib.request
import json
import argparse
import sys
import os.path
import gzip

from .db_operations import DbOperations

class OpusGet:

    def __init__(self, source=None, target=None, directory=None,
            release='latest', preprocess='xml', list_resources=False,
            list_languages=False, list_corpora=False, download_dir='.',
            local_db=False, suppress_prompts=False, database=None):
        """Download files from OPUS.

        Keyword arguments:
        source -- Source language
        target -- Target language
        directory -- Corpus directory name
        release -- Corpus release version (default latest)
        preprocess -- Corpus preprocessing type (default xml)
        list_resource -- List resources instead of downloading
        list_languages -- List available languages
        list_corpora -- List available corpora
        local_db -- Search resources from the local database instead of the online OPUS-API.
        download_dir -- Directory where files will be downloaded (default .)
        suppress_prompts -- Download files without prompting "(y/n)"
        database -- Use custom sqlite db file
        """

        if database:
            DB_FILE = database
        else:
            DB_FILE = os.path.join(os.path.dirname(__file__), 'opusdata.db')
            if not os.path.isfile(DB_FILE):
                with gzip.open(DB_FILE+'.gz') as gzfile:
                    data = gzfile.read()
                with open(DB_FILE, 'wb') as outfile:
                    outfile.write(data)

        self.dbo = DbOperations(db_file=DB_FILE)

        self.list_languages = list_languages
        self.list_corpora = list_corpora
        self.local_db = local_db

        if source and target:
            self.fromto = [source, target]
            self.fromto.sort()

        self.url = 'http://opus.nlpl.eu/opusapi/?'
        #self.url = 'http://127.0.0.1:5000/?'

        urlparts = [(source, 'source'), (target, 'target'),
            (directory, 'corpus'), (release, 'version'),
            (preprocess, 'preprocessing')]
        self.parameters = {}

        for a in urlparts:
            if a[0]:
                self.parameters[a[1]] = a[0]
                if a[0] == ' ':
                    self.url += a[1] + '=&'
                else:
                    self.url += a[1] + '=' + a[0] + '&'

        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        self.release = release
        self.preprocess = preprocess
        self.download_dir = download_dir
        self.target = target
        self.list_resources = list_resources
        self.suppress_prompts = suppress_prompts

    def round_size(self, size, length, unit):
        """Round file size."""
        last_n = str(size)[-length]
        size = int(str(size)[:-length])
        if int(last_n) >= 5:
            size += 1
        size = str(size) + unit
        return size

    def format_size(self, size):
        """Format file size."""
        if len(str(size)) > 9:
            size = self.round_size(size, 9, ' TB')
        elif len(str(size)) > 6:
            size = self.round_size(size, 6, ' GB')
        elif len(str(size)) > 3:
            size = self.round_size(size, 3, ' MB')
        else:
            size = str(size) + ' KB'
        return size

    def get_response(self, url):
        """Return data from a url."""
        response = urllib.request.urlopen(url[:-1])
        result = response.read().decode('utf-8')
        data = json.loads(result)

        return data

    def make_file_name(self, c):
        """Return file name based on corpus data."""
        filename = c['url'].replace('/', '_').replace(
            'https:__object.pouta.csc.fi_OPUS-', '')
        if self.release == 'latest':
            filename = filename.replace(
                '_'+c['version']+'_', '_latest_')
        return os.path.join(self.download_dir, filename)

    def get_corpora_data(self):
        """Receive corpus data."""
        total_size = 0

        if self.local_db:
            corpora = self.dbo.get_corpora(self.parameters)
        else:
            data = self.get_response(self.url)
            corpora = data['corpora']

        ret_corpora = []
        for c in corpora:
            filename = self.make_file_name(c)
            fileinfo = self.get_file_info_output(c)
            if os.path.isfile(filename):
                if self.list_resources:
                    print(f'        {filename} already exists | {fileinfo}')
            else:
                ret_corpora.append(c)
                total_size += c['size']

        total_size = self.format_size(total_size)

        return ret_corpora, total_size

    def progress_status(self, count, blockSize, totalSize):
        """Report download progress."""
        percent = int(count*blockSize*100/totalSize)
        if percent > 100:
            percent = 100
        print('\r{0} ... {1}% of {2}'.format(self.filename, percent,
            self.filesize), end='', flush=True)

    def download(self, corpora, total_size):
        """Download files."""
        if self.suppress_prompts == False:
            answer = input(('Downloading ' + str(len(corpora)) + ' file(s) with the '
                'total size of ' + total_size + '. Continue? (y/n) '))
        else:
            answer = 'y'

        if answer in ['y', '']:
            for c in corpora:
                self.filename = self.make_file_name(c)
                self.filesize = self.format_size(c['size'])
                try:
                    urllib.request.urlretrieve(c['url'], self.filename,
                        reporthook=self.progress_status)
                    print('')
                except urllib.error.URLError as e:
                    print('Unable to retrieve the data.')
                    return

    def get_file_info_output(self, c):
        doc_name = f"{c['documents']} documents, "
        if c['documents'] == '':
            doc_name = ''
        seg_name = 'alignment pairs'
        src_tok_name = 'source '
        target_tokens = f", {c['target_tokens']} target tokens"
        if c['target_tokens'] == '':
            seg_name = 'sentences'
            src_tok_name, target_tokens = '', ''
        output = f"{doc_name}{c['alignment_pairs']} {seg_name}, {c['source_tokens']} {src_tok_name}tokens{target_tokens} (id {c['id']})"
        return output

    def print_files(self, corpora, total_size):
        """Print file list."""
        for c in corpora:
            output = '{0:>7} {1:s}'.format(self.format_size(c['size']), c['url'])
            print(f'{output} | {self.get_file_info_output(c)}')
        print('\n{0:>7} {1:s}'.format(total_size, 'Total size'))

    def get_files(self):
        """Output corpus file information/data."""
        try:
            if self.list_languages:
                if self.local_db:
                    languages = self.dbo.run_languages_query(self.parameters)
                else:
                    languages = self.get_response(self.url+'languages=True')['languages']
                print(', '.join([str(l) for l in languages]))
                return
            elif self.list_corpora:
                if self.local_db:
                    corpus_list = self.dbo.run_corpora_query(self.parameters)
                else:
                    corpus_list = self.get_response(self.url+'corpora=True')['corpora']
                print(', '.join([str(c) for c in corpus_list]))
                return
            else:
                corpora, total_size = self.get_corpora_data()
        except urllib.error.URLError as e:
            print('Unable to retrieve the data.')
            return

        if not self.list_resources:
            self.download(corpora, total_size)
        else:
            self.print_files(corpora, total_size)

