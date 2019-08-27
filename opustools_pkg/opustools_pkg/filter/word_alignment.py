import subprocess

#from . import FilterABC


class WordAlignment:

    def __init__(self, eflomal_path):
        #self.eflomal_path = '/homeappl/home/miaulamo/appl_taito/eflomal'
        self.eflomal_path = eflomal_path

    def align(self, clean_file=None, src_fwd=None, trg_fwd=None,
            src_score=None, trg_score=None, priors=None):
        #command = ('{0}/align.py -i filter_files/clean.{1}-{2} -f '
        #    'filter_files/{1}-{2}.fwd -r filter_files/{1}-{2}.rev '
        #    '--model 3'.format(
        #        self.eflomal_path, self.src_lang, self.trg_lang).split())
        if src_score and trg_score:
            command = ('{0}/align.py -i {1} -F {2} -R {3} '
                '--model 3 -M 3 --priors {4}'.format(self.eflomal_path,
                    clean_file, src_score, trg_score, priors).split())
        else:
            command = ('{0}/align.py -i {1} -f {2} -r {3} '
                '--model 3'.format(self.eflomal_path, clean_file,
                    src_fwd, trg_fwd).split())

        subprocess.run(command)

    def make_priors(self, clean_file=None, src_fwd=None,
            trg_fwd=None, priors=None):
        command = ('{0}/makepriors.py -i {1} -f {2} -r {3} '
            '--priors {4}'.format(self.eflomal_path, clean_file,
                src_fwd, trg_fwd, priors).split())
        subprocess.run(command)


#class WordAlignFilter(FilterABC):
#
#    def __init__(self, src_threshold=0, tgt_threshold=0, priors=None, **kwargs):
#        self.src_threshold = src_threshold
#        self.tgt_threshold = tgt_threshold
#        self.priors = priors
#        super().__init__(**kwargs)
#
#    def filter(self, sent1, sent2):
#        src, tgt = self.score(sent1, sent2)
#        return src < self.src_threshold and tgt < self.tgt_threshold
#
#    def score(self, sent1, sent2):
#        pass
