import gzip


from parse.alignment_parser import AlignmentParser as Parser

opus_root = '/proj/nlpl/data/OPUS'

class OpusReadArguments:
    def __init__(self, d, s, t, r='latest', p='xml', m='all', S='all', T='all', a='any', tr=0, ln='store_true', w=-1, wm='normal'):
        self.__dict__.update(d=d, s=s, t=t, r=r, p=p, m=m, S=S, T=T, a=a, tr=tr, ln=ln, w=w, wm=wm)

args = OpusReadArguments('OpenSubtitles', 'en', 'kk')

alignment_path = opus_root + '/' + args.d + '/' + args.r + '/xml/' + args.s + '-' + args.t + '.xml.gz'
source_path = opus_root + '/' + args.d + '/' + args.r + '/' + args.p + '/' + args.s + '.zip'
target_path = opus_root + '/' + args.d + '/' + args.r + '/' + args.p + '/' + args.t + '.zip'

def normalize(pair):
    return pair

with gzip.open(alignment_path) as alignment_file:
    parser = Parser(alignment_path, source_path, target_path, args, None)

    for line in alignment_file:
        parser.parseLine(line)
        if parser.start == 'link':
            pair = parser.readPair()

            parser.fromids = []
            parser.toids = []

            if pair != -1:
                print(pair)