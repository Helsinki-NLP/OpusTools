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


class OpusFilter:

    def __init__(self, configuration):
        self.configuration = configuration
        self.output_dir = configuration['output_directory']
        if not os.path.isdir(self.output_dir):
            logging.warning(
                'Directory "{}" does not exist. Writing files to current '
                'directory.'.format(self.output_dir))
            self.output_dir = '.'

        for corpus, settings in configuration['corpora'].items():
            if settings['type'] == 'OPUS':
                parameters = settings['parameters']
                fromto = sorted([parameters['source_language'],
                    parameters['target_language']])
                src_lan = fromto[0]
                tgt_lan = fromto[1]

                opus_reader = OpusRead('-d {corpus_name} -s {src} -t {tgt} '
                    '-r {version} -p {preprocessing} -wm moses '
                    '-w {result_dir}/sents.{corpus}.{src} '
                    '{result_dir}/sents.{corpus}.{tgt} -ln'.format(
                        corpus_name=parameters['corpus_name'], src=src_lan,
                        tgt=tgt_lan, version=parameters['release'],
                        preprocessing=parameters['preprocessing'],
                        result_dir=self.output_dir, corpus=corpus).split())

                opus_reader.printPairs()

        for corpus, settings in configuration['scoring'].items():
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

    def pair_generator(self, source_file_name, target_file_name):
        with open(source_file_name) as source_file, \
                open(target_file_name) as target_file:
            for src_line in source_file:
                tgt_line = target_file.readline()
                yield (src_line.rstrip(), tgt_line.rstrip())

    def get_pairs(self, corpus_name, src, tgt):
        source_file_name = '{result_dir}/sents.{corpus_name}.{src}'.format(
            result_dir=self.output_dir, corpus_name=corpus_name, src=src)
        target_file_name = '{result_dir}/sents.{corpus_name}.{tgt}'.format(
            result_dir=self.output_dir, corpus_name=corpus_name, tgt=tgt)

        return self.pair_generator(source_file_name, target_file_name)

    def clean_data(self):
        for corpus, settings in self.configuration['filtering'].items():

            filter_pipe = FilterPipeline.from_config(settings['filters'])
            corpus_parameters = (self.configuration['corpora'][corpus]
                    ['parameters'])
            source_language = corpus_parameters['source_language']
            target_language = corpus_parameters['target_language']
            pairs_gen = self.get_pairs(corpus, source_language,
                    target_language)
            pairs = filter_pipe.filter(pairs_gen)

            source_file_name = '{result_dir}/{filtered_name}'.format(
                result_dir=self.output_dir,
                filtered_name=settings['src_output'])
            target_file_name = '{result_dir}/{filtered_name}'.format(
                result_dir=self.output_dir,
                filtered_name=settings['tgt_output'])

            with open(source_file_name, 'w') as source_file, \
                    open(target_file_name, 'w') as target_file:
                for pair in pairs:
                    source_file.write(pair[0]+'\n')
                    target_file.write(pair[1]+'\n')

    def train_lms_and_priors(self):
        for model in self.configuration['models']:
            if model['type'] == 'ngram':
                if model['parameters']['segmentation']['type'] == 'char':
                    data_name = model['data']
                    seg_name = data_name + '.seg'
                    self.segment_file(
                        '{}/{}'.format(self.output_dir, data_name),
                        '{}/{}'.format(self.output_dir, seg_name))
                    model['data'] = seg_name

                train_args = argparse.Namespace()
                for key, default in lm._VARIKN_TRAINING_PARAMS.items():
                    setattr(train_args, key, default)
                for key, value in model.items():
                    if key in ['data', 'output', 'model']:
                        value = '{}/{}'.format(self.output_dir, value)
                    setattr(train_args, key, value)
                lm.train(train_args)
            if model['type'] == 'alignment':
                pair_gen = self.pair_generator(
                        '{}/{}'.format(self.output_dir, model['src_data']),
                        '{}/{}'.format(self.output_dir, model['tgt_data']))
                word_alignment.make_priors(
                        pair_gen,
                        '{}/{}'.format(self.output_dir, model['output']),
                        model=model['parameters']['model'])

    def score_data(self):
        for corpus, settings in self.configuration['scoring'].items():
            corpus_parameters = (self.configuration['corpora'][corpus]
                    ['parameters'])
            source_language = corpus_parameters['source_language']
            target_language = corpus_parameters['target_language']
            pairs_gen = self.get_pairs(corpus, source_language,
                    target_language)

            filter_pipe = FilterPipeline.from_config(settings['filters'])
            scores_gen = filter_pipe.score(pairs_gen)
            scores = [score for score in scores_gen]

            score_file = open(
                '{result_dir}/scores.{corpus_name}.{src}-{tgt}.json'.format(
                    result_dir=self.output_dir, corpus_name=corpus,
                    src=source_language, tgt=target_language) , 'w')
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

    def segment_line_char(self, line):
        return '<s> <w> {} <w> </s> \n'.format(
                ' '.join(line.rstrip()).replace('   ', ' <w> '))

    def segment_file(self, input_file, output_file, char=True):
        with open(input_file, 'r') as infile:
            with open(output_file, 'w') as outfile:
                for line in infile:
                    if char:
                        new_line = self.segment_line_char(line)
                    else:
                        new_line = self.segment_line(line)
                    outfile.write(new_line)

