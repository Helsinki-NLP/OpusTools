import urllib.error
import urllib.request
import json
import argparse
import sys
import os
import gzip
from urllib.parse import urlencode

from .db_operations import DbOperations

class OpusGet:

    def __init__(self, source=None, target=None, directory=None,
            release='latest', preprocess='xml', list_resources=False,
            list_languages=False, list_corpora=False, download_dir='.',
            local_db=False, suppress_prompts=False,
            database='~/.OpusTools/opusdata.db', synthetic=False):
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
        database -- Sqlite db file location (default ~/.OpusTools/opusdata.db)
        download_dir -- Directory where files will be downloaded (default .)
        suppress_prompts -- Download files without prompting "(y/n)"
        synthetic -- Use the synthetic corpus API instead of the default OPUS API.
        """

        if synthetic and local_db:
            raise ValueError('synthetic and local_db cannot be combined')
        if synthetic and preprocess not in ('xml', 'raw'):
            raise ValueError('synthetic API supports only xml and raw preprocessing')

        self.list_languages = list_languages
        self.list_corpora = list_corpora
        self.local_db = local_db
        self.synthetic = synthetic

        database = os.path.expanduser(database)
        if self.local_db:
            if not os.path.isfile(database):
                compressed_db = os.path.join(os.path.dirname(__file__), 'opusdata.db.gz')
                with gzip.open(compressed_db) as gzfile:
                    data = gzfile.read()
                os.makedirs(os.path.dirname(database), exist_ok=True)
                with open(database, 'wb') as outfile:
                    outfile.write(data)
        self.dbo = DbOperations(db_file=database)

        if source and target:
            self.fromto = [source, target]
            self.fromto.sort()

        if self.synthetic:
            self.base_url = 'https://opus.nlpl.eu/synthetic-api'
            urlparts = [(directory, 'name'),
                        (None if release == 'latest' else release, 'version'),
                        (source, 'src'), (target, 'tgt')]
            self.items_url = self.base_url + '/items'
            self.languages_url = self.base_url + '/languages'
            self.collections_url = self.base_url + '/collections'
        else:
            self.base_url = 'https://opus.nlpl.eu/opusapi'
            urlparts = [(source, 'source'), (target, 'target'),
                        (directory, 'corpus'), (release, 'version'),
                        (preprocess, 'preprocessing')]

        self.parameters = {}
        for value, name in urlparts:
            if value:
                self.parameters[name] = value

        if self.synthetic:
            self.url = self._build_url(self.items_url, self.parameters)
        else:
            self.url = self._build_url(self.base_url, self.parameters)

        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        self.release = release
        self.preprocess = preprocess
        self.download_dir = download_dir
        self.directory = directory
        self.source = source
        self.target = target
        self.list_resources = list_resources
        self.suppress_prompts = suppress_prompts

    @staticmethod
    def _build_url(base_url, parameters):
        """Return base_url with url-encoded parameters."""
        if not parameters:
            return base_url
        return base_url + '?' + urlencode(parameters)

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
        response = urllib.request.urlopen(url)
        result = response.read().decode('utf-8')
        data = json.loads(result)

        return data

    def make_file_name(self, c):
        """Return file name based on corpus data."""
        if 'filename' in c:
            return c['filename']
        filename = c['url'].replace('/', '_').replace(
            'https:__object.pouta.csc.fi_OPUS-', '')
        if self.release == 'latest':
            filename = filename.replace(
                '_'+c['version']+'_', '_latest_')
        return os.path.join(self.download_dir, filename)

    def _latest_synthetic_items(self, items):
        """Return the newest item for each synthetic collection/language pair."""
        latest = {}
        for item in items:
            key = (item['name'], item['src_lang'], item['tgt_lang'])
            item_sort_key = (item.get('updated_at', ''), item.get('version', ''))
            current = latest.get(key)
            if current is None or item_sort_key > (
                    current.get('updated_at', ''), current.get('version', '')):
                latest[key] = item
        return list(latest.values())

    def _synthetic_filename(self, item, kind):
        """Return the local file name for a synthetic download."""
        version = 'latest' if self.release == 'latest' else item['version']
        if kind == 'alignment':
            filename = ('{}_{}_xml_{}-{}.xml.gz'.format(
                item['name'], version, item['src_lang'], item['tgt_lang']))
        elif kind == 'source':
            filename = ('{}_{}_{}_{}.zip'.format(
                item['name'], version, self.preprocess, item['src_lang']))
        else:
            filename = ('{}_{}_{}_{}.zip'.format(
                item['name'], version, self.preprocess, item['tgt_lang']))
        return os.path.join(self.download_dir, filename)

    @staticmethod
    def _valid_synthetic_download(download):
        """Return whether a synthetic download has a usable URL."""
        return bool(download and download.get('url'))

    @staticmethod
    def _synthetic_size(download):
        """Convert a synthetic byte size to the KB units used by OpusGet."""
        return round((download.get('size') or 0) / 1024)

    def _synthetic_rows(self, data):
        """Convert synthetic API items into default-API-style corpus rows."""
        items = data.get('items', [])
        if self.directory:
            items = [item for item in items if item['name'] == self.directory]
        if self.source:
            items = [item for item in items if item['src_lang'] == self.source]
        if self.target:
            items = [item for item in items if item['tgt_lang'] == self.target]
        if self.release != 'latest':
            items = [item for item in items if item['version'] == self.release]
        elif self.release == 'latest':
            items = self._latest_synthetic_items(items)

        include_source = bool(self.source) or not bool(self.target)
        include_target = bool(self.target) or not bool(self.source)
        rows = []

        for item in items:
            downloads = item.get('downloads', {})
            common = {
                'id': item.get('id'),
                'corpus': item['name'],
                'version': item['version'],
                'documents': item.get('files', 0),
            }

            if self.source and self.target:
                download = downloads.get('alignments')
                if self.preprocess != 'raw' and self._valid_synthetic_download(download):
                    row = dict(common)
                    row.update({
                        'source': item['src_lang'],
                        'target': item['tgt_lang'],
                        'alignment_pairs': item.get('alignments', 0),
                        'source_tokens': item.get('src_tokens', 0),
                        'target_tokens': item.get('tgt_tokens', 0),
                        'size': self._synthetic_size(download),
                        'url': download['url'],
                        'filename': self._synthetic_filename(item, 'alignment'),
                    })
                    rows.append(row)

            download = downloads.get('source_language')
            if include_source and self._valid_synthetic_download(download):
                row = dict(common)
                row.update({
                    'source': item['src_lang'],
                    'target': '',
                    'alignment_pairs': item.get('files', 0),
                    'source_tokens': item.get('src_tokens', 0),
                    'target_tokens': '',
                    'size': self._synthetic_size(download),
                    'url': download['url'],
                    'filename': self._synthetic_filename(item, 'source'),
                })
                rows.append(row)

            download = downloads.get('target_language')
            if include_target and self._valid_synthetic_download(download):
                row = dict(common)
                row.update({
                    'source': item['tgt_lang'],
                    'target': '',
                    'alignment_pairs': item.get('files', 0),
                    'source_tokens': item.get('tgt_tokens', 0),
                    'target_tokens': '',
                    'size': self._synthetic_size(download),
                    'url': download['url'],
                    'filename': self._synthetic_filename(item, 'target'),
                })
                rows.append(row)

        return rows

    def get_corpora_data(self):
        """Receive corpus data."""
        total_size = 0

        if self.local_db:
            corpora = self.dbo.get_corpora(self.parameters)
        else:
            data = self.get_response(self.url)
            if self.synthetic:
                corpora = self._synthetic_rows(data)
            else:
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
                    print(f'Unable to retrieve the data from {self.url}: {e}')
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
                elif self.synthetic:
                    url = self._build_url(self.languages_url, self.parameters)
                    languages = self.get_response(url)['languages']
                else:
                    parameters = dict(self.parameters)
                    parameters['languages'] = 'True'
                    url = self._build_url(self.base_url, parameters)
                    languages = self.get_response(url)['languages']
                print(', '.join([str(l) for l in languages]))
                return
            elif self.list_corpora:
                if self.local_db:
                    corpus_list = self.dbo.run_corpora_query(self.parameters)
                elif self.synthetic:
                    url = self._build_url(self.collections_url, self.parameters)
                    collections = self.get_response(url)['collections']
                    corpus_list = [c['name'] for c in collections]
                else:
                    parameters = dict(self.parameters)
                    parameters['corpora'] = 'True'
                    url = self._build_url(self.base_url, parameters)
                    corpus_list = self.get_response(url)['corpora']
                print(', '.join([str(c) for c in corpus_list]))
                return
            else:
                corpora, total_size = self.get_corpora_data()
        except urllib.error.URLError as e:
            print(f'Unable to retrieve the data from {self.url}: {e}')
            return

        if not self.list_resources:
            self.download(corpora, total_size)
        else:
            self.print_files(corpora, total_size)
