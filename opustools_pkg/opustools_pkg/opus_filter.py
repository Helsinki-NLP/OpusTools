import os
import argparse
import json
import subprocess

from yaml import load, Loader

from . import OpusRead
from .filter.pipeline import FilterPipeline

class OpusGetSents(OpusRead):

    def __init__(self, arguments):
        super().__init__(arguments)
        self.sents = []

    def sendPairOutput(self, wpair):
        self.sents.append((wpair[0].rstrip(), wpair[1].rstrip()))

class OpusFilter:

    def __init__(self, args):
        fromto = sorted([args.s, args.t])
        self.fromto = fromto

        try:
            os.mkdir('filter_files')
        except FileExistsError:
            pass

        get_sents = OpusGetSents('-d {0} -s {1} -t {2} -r {3} -p {4} -wm '
            'moses -w filter_files/temp filter_files/temp -ln'.format(
                args.d, args.s, args.t, args.r, args.p).split())

        get_sents.printPairs()

        self.sents = get_sents.sents

    def clean_data(self, config):
        clean_file= open('filter_files/clean.{0}-{1}'.format(
            self.fromto[0], self.fromto[1]), 'w')

        filter_pipe = FilterPipeline.from_config(config)
        pairs = filter_pipe.filter(self.sents)

        for pair in pairs:
            clean_file.write('{} ||| {}\n'.format(pair[0], pair[1]))
        clean_file.close()

    def score_data(self, config):
        filter_pipe = FilterPipeline.from_config(config)
        scores = filter_pipe.score(self.sents)

        score_file = open('filter_files/scores.{0}-{1}.json'.format(
            self.fromto[0], self.fromto[1]) , 'w')
        score_file.write(json.dumps(scores))
        score_file.close()

    def make_bpe(self, train_file, input_file, output_file):
        bpe_file = train_file+'.code'
        subprocess.run('subword-nmt learn-bpe -s 37000 < {} > {}'.format(
            train_file, bpe_file), shell=True)
        subprocess.run('subword-nmt apply-bpe -c {} < {} > {}'.format(
            bpe_file, input_file, output_file), shell=True)

    def segment_line(self, line):
        newli = ['<s>', '<w>']
        for w in line.split():
            newli.append(w)
            if w[-2:] != '@@':
                newli.append('<w>')
        newli.extend(['</s>', '\n'])
        return ' '.join(newli)

    def segment_file(self, input_file, output_file):
        with open(input_file, 'r') as infile:
            with open(output_file, 'w') as outfile:
                for line in infile:
                    new_line = self.segment_line(line)
                    outfile.write(new_line)

    def sents_to_file(self, bpe=False, segment=False):
        source_file_name = 'filter_files/sents.{}'.format(self.fromto[0])
        target_file_name = 'filter_files/sents.{}'.format(self.fromto[1])
        source_file = open(source_file_name, 'w')
        target_file = open(target_file_name, 'w')

        for pair in self.sents:
            source_file.write(pair[0] + '\n')
            target_file.write(pair[1] + '\n')

        source_file.close()
        target_file.close()

        if bpe:
            src_train_file_name = 'filter_files/sents.{}'.format(
                    self.fromto[0])
            source_bpe_file_name = source_file_name+'.bpe'
            self.make_bpe(
                    src_train_file_name,
                    source_file_name,
                    source_bpe_file_name
                    )
            tgt_train_file_name = 'filter_files/sents.{}'.format(
                    self.fromto[1])
            target_bpe_file_name = target_file_name+'.bpe'
            self.make_bpe(
                    tgt_train_file_name,
                    target_file_name,
                    target_bpe_file_name
                    )

        if segment:
            if bpe:
                source_file_name = source_bpe_file_name
                target_file_name = target_bpe_file_name
            source_seg_file_name = source_file_name+'.seg'
            target_seg_file_name = target_file_name+'.seg'

            self.segment_file(
                    source_file_name,
                    source_seg_file_name
                    )
            self.segment_file(
                    target_file_name,
                    target_seg_file_name
                    )

    '''
    def word_alignment_score(self):
        self.wordAlignment.align(
                clean_file='filter_files/clean.{0}-{1}'.format(
                    self.fromto[0], self.fromto[1]),
                src_fwd='filter_files/{0}-{1}.fwd'.format(self.fromto[0],
                    self.fromto[1]),
                trg_fwd='filter_files/{0}-{1}.rev'.format(self.fromto[0],
                    self.fromto[1])
            )
        self.wordAlignment.make_priors(
                clean_file='filter_files/clean.{0}-{1}'.format(
                    self.fromto[0], self.fromto[1]),
                src_fwd='filter_files/{0}-{1}.fwd'.format(self.fromto[0],
                    self.fromto[1]),
                trg_fwd='filter_files/{0}-{1}.rev'.format(self.fromto[0],
                    self.fromto[1]),
                priors='filter_files/{0}-{1}.priors'.format(self.fromto[0],
                    self.fromto[1])
            )
        self.wordAlignment.align(
                clean_file='filter_files/clean.{0}-{1}'.format(
                    self.fromto[0], self.fromto[1]),
                src_score='filter_files/{0}-{1}.fwd'.format(self.fromto[0],
                    self.fromto[1]),
                trg_score='filter_files/{0}-{1}.rev'.format(self.fromto[0],
                    self.fromto[1]),
                priors='filter_files/{0}-{1}.priors'.format(self.fromto[0],
                    self.fromto[1])
            )
    '''



