import os
import sys
import zipfile

from .util import file_open
from .opus_get import OpusGet

class OpusFileHandler:

    def __init__(self, download_dir, source_zip, target_zip, directory,
            release, preprocess, fromto, verbose, suppress_prompts):

        self.directory = directory
        self.release = release
        self.preprocess = preprocess
        self.fromto = fromto

        self.verbose = verbose
        self.suppress_prompts = suppress_prompts

        self.download_dir = download_dir

        self.src_zip_name = source_zip
        self.trg_zip_name = target_zip

        self.zip_opened = False

    def open_alignment_file(self, alignment):
        if self.verbose: print('Reading alignment file ', end='')
        try:
            if self.verbose: print('"{}"'.format(alignment))
            alignment = file_open(alignment, mode='r', encoding='utf-8')
        except FileNotFoundError:
            arguments = {'source': self.fromto[0],
                    'target': self.fromto[1], 'directory': self.directory,
                    'release': self.release, 'preprocess': self.preprocess,
                    'download_dir': self.download_dir, 'list_resources': True}
            og = OpusGet(**arguments)
            og.get_files()
            arguments['list_resources'] = False
            if self.suppress_prompts:
                arguments['suppress_prompts'] = True
            og = OpusGet(**arguments)
            og.get_files()
            local_align_name = os.path.join(self.download_dir,
                    self.directory+'_'+ self.release+'_xml_'+self.fromto[0]+'-'+
                    self.fromto[1]+'.xml.gz')
            if os.path.isfile(local_align_name):
                if self.verbose: print('"{}"'.format(local_align_name))
                alignment = file_open(
                    local_align_name, mode='r', encoding='utf-8')
            else:
                raise FileNotFoundError('No alignment file "{default}" or'
                        ' "{downloaded}" found'.format(
                        default=alignment, downloaded=local_align_name))

        return alignment

    def open_zipfiles(self):
        if self.verbose:
            print('Opening zip archive "{}" ... '.format(self.src_zip_name),
                    end='')
        self.src_zip = zipfile.ZipFile(self.src_zip_name, 'r')
        if self.verbose:
            print('Done')
            print('Opening zip archive "{}" ... '.format(self.trg_zip_name),
                    end='')
        self.trg_zip = zipfile.ZipFile(self.trg_zip_name, 'r')
        if self.verbose:
            print('Done')

        self.zip_opened = True

    def open_sentence_file(self, doc_name, direction):
        local_doc = os.path.join(self.download_dir, doc_name)
        try:
            return file_open(local_doc)
        except FileNotFoundError:
            pass

        if not self.zip_opened:
            self.open_zipfiles()

        #In OPUS, directory and preprocessing information need to be added and
        #the ".gz" ending needs to be removed.
        opus_doc_name = self.directory+'/'+self.preprocess+'/'+doc_name[:-3]

        if self.verbose: print('Reading {}_file "{}"'.format(
            direction, opus_doc_name))

        if direction == 'src':
            if opus_doc_name in self.src_zip.namelist():
                doc = self.src_zip.open(opus_doc_name, 'r')
            else:
                doc = self.src_zip.open(doc_name, 'r')
        if direction == 'trg':
            if opus_doc_name in self.trg_zip.namelist():
                doc = self.trg_zip.open(opus_doc_name, 'r')
            else:
                doc = self.trg_zip.open(doc_name, 'r')
        return doc

    def close_zipfiles(self):
        if self.zip_opened:
            self.src_zip.close()
            self.trg_zip.close()

