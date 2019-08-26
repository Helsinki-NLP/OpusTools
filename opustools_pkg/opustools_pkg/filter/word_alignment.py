import subprocess


class WordAlignment:

    def __init__(self, eflomal_path):
        #self.eflomal_path = '/homeappl/home/miaulamo/appl_taito/eflomal'
        self.eflomal_path = eflomal_path

    def align(self, src_file=None, trg_file=None, src_fwd=None, trg_fwd=None,
            src_score=None, trg_score=None, priors=None):
        #command = ('{0}/align.py -i filter_files/clean.{1}-{2} -f '
        #    'filter_files/{1}-{2}.fwd -r filter_files/{1}-{2}.rev '
        #    '--model 3'.format(
        #        self.eflomal_path, self.src_lang, self.trg_lang).split())
        if src_score and trg_score:
            command = ('{0}/align.py -s {1} -t {2} -F {3} -R {4} '
                '--model 3 -M 3 --priors {5}'.format(self.eflomal_path,
                    src_file, trg_file, src_score, trg_score, priors).split())
        else:
            command = ('{0}/align.py -s {1} -t {2} -f {3} -r {4} '
                '--model 3'.format(self.eflomal_path, src_file, trg_file,
                    src_fwd, trg_fwd).split())

        subprocess.run(command)

    def make_priors(self, src_file=None, trg_file=None, src_fwd=None,
            trg_fwd=None, priors=None):
        command = ('{0}/makepriors.py -s {1} -t {2} -f {3} -r {4} '
            '--priors {5}'.format(self.eflomal_path, src_file, trg_file,
                src_fwd, trg_fwd, priors).split())
        subprocess.run(command)

