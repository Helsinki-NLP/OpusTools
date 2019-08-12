import sys

slan = sys.argv[1]
tlan = sys.argv[2]

with open('pairs.{}'.format(slan), 'r') as pairs_file:
    with open('clean.{}'.format(slan), 'r') as clean_file:
        with open('clean_score.{0}-{1}'.format(slan, tlan), 'w') as output_file:
            for cline in clean_file:
                while True:
                    pline = pairs_file.readline()
                    if pline == cline:
                        output_file.write('1\n')
                        break
                    else:
                        output_file.write('0\n')
