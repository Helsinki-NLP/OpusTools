import os
import argparse
import json
import subprocess
import logging

from yaml import load, Loader

from . import OpusRead
from .filter.pipeline import FilterPipeline


class OpusFilter:

    def __init__(self, args):
        fromto = sorted([args.s, args.t])
        self.src_lan = fromto[0]
        self.tgt_lan = fromto[1]

        if not os.path.isdir(args.rd):
            logging.warning('Directory "{}" does not exist.'.format(args.rd))

        opus_reader = OpusRead('-d {corpus} -s {src} -t {tgt} -r {version} '
            '-p {preprocessing} -wm moses -w {result_dir}/sents.{src} '
            '{result_dir}/sents.{tgt} -ln'.format(
                corpus=args.d, src=args.s, tgt=args.t, version=args.r,
                preprocessing=args.p, result_dir=args.rd).split())

        self.args = args

        opus_reader.printPairs()

    def get_pairs(self, src, tgt):
        source_file = open('{result_dir}/sents.{src}'.format(
            result_dir=self.args.rd, src=self.src_lan))
        target_file = open('{result_dir}/sents.{tgt}'.format(
            result_dir=self.args.rd, tgt=self.tgt_lan))
        for src_line in source_file:
            tgt_line = target_file.readline()
            yield (src_line.rstrip(), tgt_line.rstrip())
        source_file.close()
        target_file.close()

    def clean_data(self, config):
        clean_file= open('{result_dir}/clean.{src}-{tgt}'.format(
            result_dir=self.args.rd, src=self.src_lan, tgt=self.tgt_lan), 'w')

        filter_pipe = FilterPipeline.from_config(config)
        pairs_gen = self.get_pairs(self.src_lan, self.tgt_lan)
        pairs = filter_pipe.filter(pairs_gen)

        for pair in pairs:
            clean_file.write('{} ||| {}\n'.format(pair[0], pair[1]))
        clean_file.close()

    def score_data(self, config):
        pairs_gen = self.get_pairs(self.src_lan, self.tgt_lan)

        filter_pipe = FilterPipeline.from_config(config)
        scores_gen = filter_pipe.score(pairs_gen)
        scores = [score for score in scores_gen]

        score_file = open('{result_dir}/scores.{src}-{tgt}.json'.format(
            result_dir=self.args.rd, src=self.src_lan, tgt=self.tgt_lan) , 'w')
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

