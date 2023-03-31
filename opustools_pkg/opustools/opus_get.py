import urllib.request
import json
import argparse
import sys
import os.path

from .db_operations import clean_up_parameters, run_corpora_query, run_languages_query, get_corpora

class OpusGet:

    def __init__(self, source=None, target=None, directory=None,
            release='latest', preprocess='xml', list_resources=False,
            list_languages=False, list_corpora=False, download_dir='.',
            online_api=False, suppress_prompts=False):
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
        online_api -- Search resource from the online OPUS-API instead of the local database.
        download_dir -- Directory where files will be downloaded (default .)
        suppress_prompts -- Download files without prompting "(y/n)"
        """

        self.list_languages = list_languages
        self.list_corpora = list_corpora
        self.online_api = online_api

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

        if self.online_api:
            data = self.get_response(self.url)
            corpora = data['corpora']
        else:
            corpora = get_corpora(self.parameters)

        ret_corpora = []
        for c in corpora:
            filename = self.make_file_name(c)
            if os.path.isfile(filename):
                if self.list_resources:
                    print('        {} already exists'.format(filename))
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

    def print_files(self, corpora, total_size):
        """Print file list."""
        for c in corpora:
            print('{0:>7} {1:s}'.format(self.format_size(c['size']), c['url']))
        print('\n{0:>7} {1:s}'.format(total_size, 'Total size'))

    def get_files(self):
        """Output corpus file information/data."""
        try:
            if self.list_languages:
                if self.online_api:
                    languages = self.get_response(self.url+'languages=True')['languages']
                else:
                    languages = run_languages_query(self.parameters)
                print(', '.join([str(l) for l in languages]))
                return
            elif self.list_corpora:
                if self.online_api:
                    corpus_list = self.get_response(self.url+'corpora=True')['corpora']
                else:
                    corpus_list = run_corpora_query(self.parameters)
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

