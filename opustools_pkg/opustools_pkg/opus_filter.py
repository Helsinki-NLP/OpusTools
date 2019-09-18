import os
import json
import subprocess
import logging
import argparse

from yaml import load, Loader

from . import OpusRead
from .filter.pipeline import FilterPipeline
from .filter import lm
from .filter import word_alignment
from .filter import tokenization


class OpusFilter:

    def __init__(self, configuration):
        self.configuration = configuration
        if 'output_directory' in configuration.keys():
            self.output_dir = configuration['output_directory']
            if not os.path.isdir(self.output_dir):
                logging.warning(
                    'Directory "{}" does not exist. Writing files to current '
                    'directory.'.format(self.output_dir))
                self.output_dir = '.'
        else:
            logging.warning(
                'Output directory not specified. Writing files to current '
                'directory.')
            self.output_dir = '.'

        if 'corpora' in configuration.keys():
            for corpus, settings in configuration['corpora'].items():
                #Download and read corpus from OPUS if type is 'OPUS'
                #TODO: allow other corpus types
                if settings['type'] == 'OPUS':
                    parameters = settings['parameters']
                    fromto = sorted([parameters['source_language'],
                        parameters['target_language']])
                    src_lan = fromto[0]
                    tgt_lan = fromto[1]

                    opus_reader = OpusRead('-d {corpus_name} -s {src} -t {tgt} '
                        '-r {version} -p {preprocessing} -wm moses '
                        '-w {result_dir}/{src_filename} '
                        '{result_dir}/{tgt_filename} -ln'.format(
                            corpus_name=parameters['corpus_name'], src=src_lan,
                            tgt=tgt_lan, version=parameters['release'],
                            preprocessing=parameters['preprocessing'],
                            result_dir=self.output_dir,
                            src_filename=parameters['src_filename'],
                            tgt_filename=parameters['tgt_filename']).split())

                    opus_reader.printPairs()

        #Add output directory to output file names
        for corpus, settings in self.configuration['scoring'].items():
            for f in settings['filters']:
                filter_name = next(iter(f.items()))[0]
                if filter_name == 'WordAlignFilter':
                    f[filter_name]['priors'] = '{}/{}'.format(
                            self.output_dir, f[filter_name]['priors'])
                if filter_name == 'CrossEntropyFilter':
                    src_lm_params = f[filter_name]['src_lm_params']
                    src_lm_params['filename'] = '{}/{}'.format(
                            self.output_dir, src_lm_params['filename'])
                    tgt_lm_params = f[filter_name]['tgt_lm_params']
                    tgt_lm_params['filename'] = '{}/{}'.format(
                            self.output_dir, tgt_lm_params['filename'])

    def pair_generator(self, source_file_name, target_file_name, src_tokenizer=None, tgt_tokenizer=None):
        src_tokenize = tokenization.get_tokenize(src_tokenizer)
        tgt_tokenize = tokenization.get_tokenize(tgt_tokenizer)
        with open(source_file_name) as source_file, \
                open(target_file_name) as target_file:
            for src_line in source_file:
                tgt_line = target_file.readline()
                yield (src_tokenize(src_line.rstrip()), tgt_tokenize(tgt_line.rstrip()))

    def get_pairs(self, src_filename, tgt_filename):
        source_file_name = '{result_dir}/{src_filename}'.format(
            result_dir=self.output_dir, src_filename=src_filename)
        target_file_name = '{result_dir}/{tgt_filename}'.format(
            result_dir=self.output_dir, tgt_filename=tgt_filename)

        return self.pair_generator(source_file_name, target_file_name)

    def clean_data(self):
        if 'filtering' in self.configuration.keys():
            for corpus, settings in self.configuration['filtering'].items():

                filter_pipe = FilterPipeline.from_config(settings['filters'])
                pairs_gen = self.get_pairs(settings['src_input'],
                        settings['tgt_input'])
                pairs = filter_pipe.filter(pairs_gen)

                source_file_name = '{result_dir}/{src_filtered}'.format(
                    result_dir=self.output_dir,
                    src_filtered=settings['src_output'])
                target_file_name = '{result_dir}/{tgt_filtered}'.format(
                    result_dir=self.output_dir,
                    tgt_filtered=settings['tgt_output'])

                with open(source_file_name, 'w') as source_file, \
                        open(target_file_name, 'w') as target_file:
                    for pair in pairs:
                        source_file.write(pair[0]+'\n')
                        target_file.write(pair[1]+'\n')

    def train_models(self):
        if 'models' in self.configuration.keys():
            for model in self.configuration['models']:
                if model['type'] == 'ngram':
                    data_name = model['data']
                    seg_name = data_name + '.seg'
                    tokenizer = lm.LMTokenizer(**model['parameters'])
                    with open(os.path.join(self.output_dir, data_name), 'r') as infile, \
                         open(os.path.join(self.output_dir, seg_name), 'w') as outfile:
                        for line in infile:
                            tokens = tokenizer.tokenize(line.strip())
                            outfile.write(' '.join(tokens) + '\n')
                    lm.train(os.path.join(self.output_dir, seg_name),
                             os.path.join(self.output_dir, model['model']),
                             **model['parameters'])
                if model['type'] == 'alignment':
                    pair_gen = self.pair_generator(
                            '{}/{}'.format(self.output_dir, model['src_data']),
                            '{}/{}'.format(self.output_dir, model['tgt_data']),
                            src_tokenizer=model['parameters'].get('src_tokenizer', None),
                            tgt_tokenizer=model['parameters'].get('tgt_tokenizer', None))
                    word_alignment.make_priors(
                            pair_gen,
                            '{}/{}'.format(self.output_dir, model['output']),
                            model=model['parameters']['model'])

    def score_data(self):
        if 'scoring' in self.configuration.keys():
            for corpus, settings in self.configuration['scoring'].items():
                pairs_gen = self.get_pairs(settings['src_input'],
                        settings['tgt_input'])

                filter_pipe = FilterPipeline.from_config(settings['filters'])
                scores_gen = filter_pipe.score(pairs_gen)

                score_file_name = ('{result_dir}/{scored_name}'.format(
                    result_dir=self.output_dir,
                    scored_name=settings['output']))
                with open(score_file_name, 'w') as score_file:
                    for score in scores_gen:
                        score_file.write(json.dumps(score, sort_keys=True)+'\n')
