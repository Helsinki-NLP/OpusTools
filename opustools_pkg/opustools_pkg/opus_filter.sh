#!/bin/bash

corpus=$1
slan=$2
tlan=$3

python opus_filter.py -d $corpus -s $slan -t $tlan

clean-corpus-n.perl pairs $slan $tlan clean 1 50

python check_clean.py $slan $tlan

#python ~/appl_taito/eflomal/makepriors.py -i pairs.${slan}-${tlan} -f ${slan}-${tlan}.fwd -r ${slan}-${tlan}.rev --priors ${slan}-${tlan}.priors
#python ~/appl_taito/eflomal/align.py -i pairs.${slan}-${tlan}.small --priors ${slan}-${tlan}.priors --model 3 -f ${slan}-${tlan}.small.fwd -r ${slan}-${tlan}.small.rev
python ~/appl_taito/eflomal/align.py -i pairs.${slan}-${tlan} -m 3 -M 3 -F ${slan}-${tlan}.fwd -R ${slan}-${tlan}.rev

subword-nmt learn-bpe -s 37000 < pairs.${slan} > ${slan}.bpe
subword-nmt apply-bpe -c ${slan}.bpe < pairs.${slan} > pairs.seg.${slan}

subword-nmt learn-bpe -s 37000 < pairs.${tlan} > ${tlan}.bpe
subword-nmt apply-bpe -c ${tlan}.bpe < pairs.${tlan} > pairs.seg.${tlan}
