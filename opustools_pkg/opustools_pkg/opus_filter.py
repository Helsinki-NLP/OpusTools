import os
import argparse
import json

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

    def sents_to_file(self):
        source_file = open('filter_files/sents.{}'.format(self.fromto[0]), 'w')
        target_file = open('filter_files/sents.{}'.format(self.fromto[1]), 'w')

        for pair in self.sents:
            source_file.write(pair[0] + '\n')
            target_file.write(pair[1] + '\n')

        source_file.close()
        target_file.close()

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



