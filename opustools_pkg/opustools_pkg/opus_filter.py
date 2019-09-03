import os
import argparse
import json
import subprocess
import logging

from yaml import load, Loader

from . import OpusRead
from .filter.pipeline import FilterPipeline


class OpusFilter:

    def __init__(self, configuration):
        self.configuration = configuration
        self.output_dir = configuration['output_directory']
        if not os.path.isdir(self.output_dir):
            logging.warning(
                'Directory "{}" does not exist.'.format(self.output_dir))

        for corpus, settings in configuration['corpora'].items():
            if settings['type'] == 'OPUS':
                parameters = settings['parameters']
                fromto = sorted([parameters['source_language'],
                    parameters['target_language']])
                src_lan = fromto[0]
                tgt_lan = fromto[1]

                opus_reader = OpusRead('-d {corpus_name} -s {src} -t {tgt} '
                    '-r {version} -p {preprocessing} -wm moses '
                    '-w {result_dir}/sents.{corpus_name}.{src} '
                    '{result_dir}/sents.{corpus_name}.{tgt} -ln'.format(
                        corpus_name=parameters['corpus_name'], src=src_lan,
                        tgt=tgt_lan, version=parameters['release'],
                        preprocessing=parameters['preprocessing'],
                        result_dir=self.output_dir).split())

                opus_reader.printPairs()

    def get_pairs(self, corpus_name, src, tgt):
        source_file = open('{result_dir}/sents.{corpus_name}.{src}'.format(
            result_dir=self.output_dir, corpus_name=corpus_name, src=src))
        target_file = open('{result_dir}/sents.{corpus_name}.{tgt}'.format(
            result_dir=self.output_dir, corpus_name=corpus_name, tgt=tgt))
        for src_line in source_file:
            tgt_line = target_file.readline()
            yield (src_line.rstrip(), tgt_line.rstrip())
        source_file.close()
        target_file.close()

    def clean_data(self):
        for corpus, settings in self.configuration['filtering'].items():
            clean_file= open('{result_dir}/{output_file}'.format(
                result_dir=self.output_dir,
                output_file=settings['output']), 'w')

            filter_pipe = FilterPipeline.from_config(settings['filters'])
            corpus_parameters = (self.configuration['corpora'][corpus]
                    ['parameters'])
            corpus_name = corpus_parameters['corpus_name']
            source_language = corpus_parameters['source_language']
            target_language = corpus_parameters['target_language']
            pairs_gen = self.get_pairs(corpus_name, source_language,
                    target_language)
            pairs = filter_pipe.filter(pairs_gen)

            for pair in pairs:
                clean_file.write('{} ||| {}\n'.format(pair[0], pair[1]))
            clean_file.close()

    def score_data(self):
        for corpus, settings in self.configuration['filtering'].items():
            corpus_parameters = (self.configuration['corpora'][corpus]
                    ['parameters'])
            corpus_name = corpus_parameters['corpus_name']
            source_language = corpus_parameters['source_language']
            target_language = corpus_parameters['target_language']
            pairs_gen = self.get_pairs(corpus_name, source_language,
                    target_language)

            filter_pipe = FilterPipeline.from_config(settings['filters'])
            scores_gen = filter_pipe.score(pairs_gen)
            scores = [score for score in scores_gen]

            score_file = open(
                '{result_dir}/scores.{corpus_name}.{src}-{tgt}.json'.format(
                    result_dir=self.output_dir, corpus_name=corpus_name,
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

    def segment_file(self, input_file, output_file, char=False):
        with open(input_file, 'r') as infile:
            with open(output_file, 'w') as outfile:
                for line in infile:
                    if char:
                        new_line = self.segment_line_char(line)
                    else:
                        new_line = self.segment_line(line)
                    outfile.write(new_line)

