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

    def download_files(self):
        print('The following files are available for downloading:\n')
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

    def open_alignment_file(self, align_name):
        """Open alignment file. Look first for specified file, then
        look for pre-downloaded local file, and finally, download
        missing files"""

        local_align_name = os.path.join(self.download_dir,
                self.directory+'_'+ self.release+'_xml_'+self.fromto[0]+'-'+
                self.fromto[1]+'.xml.gz')
        if self.verbose: print('Reading alignment file ', end='')

        if os.path.isfile(align_name):
            if self.verbose: print('"{}"'.format(align_name))
            alignment = file_open(align_name, mode='r', encoding='utf-8')
        elif os.path.isfile(local_align_name):
            if self.verbose: print('"{}"'.format(local_align_name))
            alignment = file_open(local_align_name, mode='r', encoding='utf-8')
        else:
            print('No alignment file "{default}" or "{downloaded}" found'.format(
                default=align_name, downloaded=local_align_name))
            self.download_files()
            if os.path.isfile(local_align_name):
                if self.verbose: print('"{}"'.format(local_align_name))
                alignment = file_open(
                    local_align_name, mode='r', encoding='utf-8')
            else:
                raise FileNotFoundError('No alignment file "{default}" or'
                        ' "{downloaded}" found'.format(
                        default=align_name, downloaded=local_align_name))

        return alignment

    def open_specific_zips(self, src_zip_name, trg_zip_name):
        if self.verbose:
            print('Opening zip archive "{}" ... '.format(src_zip_name),
                    end='')
        src_zip = zipfile.ZipFile(src_zip_name, 'r')
        if self.verbose:
            print('Done')
            print('Opening zip archive "{}" ... '.format(trg_zip_name),
                    end='')
        trg_zip = zipfile.ZipFile(trg_zip_name, 'r')
        if self.verbose:
            print('Done')
        return src_zip, trg_zip

    def open_zipfiles(self):
        """Open zip files. Look first for specified zip files, then
        look for pre-downloaded local files, and finally, download
        missing files"""

        local_src_name = os.path.join(self.download_dir, self.directory+'_'+
                self.release+'_'+ self.preprocess+'_'+self.fromto[0]+'.zip')
        local_trg_name = os.path.join(self.download_dir, self.directory+'_'+
                self.release+'_'+ self.preprocess+'_'+self.fromto[1]+'.zip')

        if os.path.isfile(self.src_zip_name) and os.path.isfile(self.trg_zip_name):
            self.src_zip, self.trg_zip = self.open_specific_zips(
                    self.src_zip_name, self.trg_zip_name)
        elif os.path.isfile(local_src_name) and os.path.isfile(local_trg_name):
            self.src_zip, self.trg_zip = self.open_specific_zips(
                    local_src_name, local_trg_name)
        else:
            print('No zip files found.')
            self.download_files()
            if os.path.isfile(local_src_name) and os.path.isfile(local_src_name):
                self.src_zip, self.trg_zip = self.open_specific_zips(
                        local_src_name, local_trg_name)
            else:
                raise FileNotFoundError('No zip files "{}" and "{}" OR'
                        ' "{}" and "{}" found'.format(
                        self.src_zip_name, self.trg_zip_name,
                        local_src_name, local_trg_name))

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

        try:
            if direction == 'src':
                if opus_doc_name in self.src_zip.namelist():
                    doc = self.src_zip.open(opus_doc_name, 'r')
                else:
                    doc = self.src_zip.open(doc_name, 'r')
        except KeyError as e:
            raise KeyError(e.args[0]+" '"+self.src_zip_name+"'")
        try:
            if direction == 'trg':
                if opus_doc_name in self.trg_zip.namelist():
                    doc = self.trg_zip.open(opus_doc_name, 'r')
                else:
                    doc = self.trg_zip.open(doc_name, 'r')
        except KeyError as e:
            raise KeyError(e.args[0]+" '"+self.trg_zip_name+"'")
        return doc

    def close_zipfiles(self):
        if self.zip_opened:
            self.src_zip.close()
            self.trg_zip.close()

