import urllib.request
import json
import argparse
import sys
import os.path

class OpusGet:

    def __init__(self, source=None, target=None, directory=None,
            release='latest', preprocess='xml', list_resources=False,
            download_dir='.', suppress_prompts=False):
        """Download files from OPUS.

        Keyword arguments:
        source -- Source language
        target -- Target language
        directory -- Corpus directory name
        release -- Corpus release version (default latest)
        preprocess -- Corpus preprocessing type (default xml)
        list_resource -- List resources instead of downloading
        download_dir -- Directory where files will be downloaded (default .)
        suppress_prompts -- Download files without prompting "(y/n)"
        """

        if target != None:
            self.fromto = [source, target]
            self.fromto.sort()

        self.url = 'http://opus.nlpl.eu/opusapi/?'

        urlparts = [(source, 'source'), (target, 'target'),
            (directory, 'corpus'), (release, 'version'),
            (preprocess, 'preprocessing')]

        for a in urlparts:
            if a[0]:
                if a[0] == ' ':
                    self.url += a[1] + '=&'
                else:
                    self.url += a[1] + '=' + a[0] + '&'

        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        self.release = release
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

    def add_data_with_aligment(self, tempdata, retdata):
        """Add tempdata, that has an alignment file for the
        current language pair, to retdata."""
        for i in tempdata:
            if (i['preprocessing'] == 'xml' and i['source'] == self.fromto[0]
                    and i['target'] == self.fromto[1]):
                retdata += tempdata
                break
        return retdata

    def remove_data_with_no_alignment(self, data):
        """Remove corpus data, that are missing an alignment file for
        the current language pair, from data.
        """
        retdata = []
        tempdata = []
        prev_directory = ''

        #Put all files from one directory to tempfile, and
        #when the directory changes, add the files to retdata,
        #if the files contain an alignment file for the current
        #language pair.
        for c in data['corpora']:
            directory = '/{0}/{1}'.format(c['corpus'], c['version'])
            if prev_directory != '' and prev_directory!=directory:
                retdata = self.add_data_with_aligment(tempdata, retdata)
                tempdata = []
            tempdata.append(c)
            prev_directory = directory

        retdata = self.add_data_with_aligment(tempdata, retdata)
        return retdata

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
        file_n = 0
        total_size = 0
        data = self.get_response(self.url)

        if self.target and self.target != ' ':
            corpora = self.remove_data_with_no_alignment(data)
        else:
            corpora = data['corpora']

        ret_corpora = []
        for c in corpora:
            filename = self.make_file_name(c)
            if os.path.isfile(filename):
                if self.list_resources:
                    print('        {} already exists'.format(filename))
            else:
                ret_corpora.append(c)
                file_n += 1
                total_size += c['size']

        total_size = self.format_size(total_size)

        return ret_corpora, file_n, total_size

    def progress_status(self, count, blockSize, totalSize):
        """Report download progress."""
        percent = int(count*blockSize*100/totalSize)
        if percent > 100:
            percent = 100
        print('\r{0} ... {1}% of {2}'.format(self.filename, percent,
            self.filesize), end='', flush=True)

    def download(self, corpora, file_n, total_size):
        """Download files."""
        if self.suppress_prompts == False:
            answer = input(('Downloading ' + str(file_n) + ' file(s) with the '
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

    def print_files(self, corpora, file_n, total_size):
        """Print file list."""
        for c in corpora:
            print('{0:>7} {1:s}'.format(self.format_size(c['size']), c['url']))
        print('\n{0:>7} {1:s}'.format(total_size, 'Total size'))

    def get_files(self):
        """Output corpus file information/data."""
        try:
            corpora, file_n, total_size = self.get_corpora_data()
        except urllib.error.URLError as e:
            print('Unable to retrieve the data.')
            return

        if not self.list_resources:
            self.download(corpora, file_n, total_size)
        else:
            self.print_files(corpora, file_n, total_size)

