##########################################################################
# Representation:                                                        #
##########################################################################
# Original XML                                                           #
#   "<link id="SL72" xtargets="74 75;72" overlap="0.964">":              #
##########################################################################
# Alignment.source                                                       #
#   [{'id':74, 'text':'ars longa ,'}, {'id':75, 'text':'vita brevis .'}] #
# Alignment.target                                                       #
#   [{'id':72, 'text':'art is long , life is short .'}]                  #
# Alignment.overlap                                                      #
#   0.964                                                                #
##########################################################################

from operator import itemgetter


class Alignment:
    def __init__(self, raw_line, parses):
        src_parses, trg_parses = parses

        self.source = [{'id': int(p.split('(src)="')[1].split('"')[0]), 'text': p.split('>')[1]} for p in src_parses.split('\n')]
        self.target = [{'id': int(p.split('(trg)="')[1].split('"')[0]), 'text': p.split('>')[1]} for p in trg_parses.split('\n')]

        overlap = str(raw_line).split('overlap="')[1].split('"')[0]

        self.overlap = float(overlap)

    def __parses_to_str(self, parses):
        texts = []

        for parse in sorted(parses, key=itemgetter('id')):
            texts.append(parse['text'])

        return ' '.join(texts)

    def source_str(self):
        return self.__parses_to_str(self.source)

    def target_str(self):
        return self.__parses_to_str(self.target)