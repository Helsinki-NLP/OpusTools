from filter.alignment_reader import AlignmentReader
from filter.alignment_writer import AlignmentWriter


for (s_lang, t_lang) in [('de', 'en'), ('en', 'fr')]:
    reader = AlignmentReader('OpenSubtitles', s_lang, t_lang)

    with AlignmentWriter('subsHiConf.' + s_lang + '-' + t_lang + '.' + s_lang,
                         'subsHiConf.' + s_lang + '-' + t_lang + '.' + t_lang) as writer:
        while reader.has_next():
            alignment = reader.next()

            if alignment is not None:
                if len(alignment.source) == 1 and len(alignment.target) == 1 and alignment.overlap > 0.9:
                    writer.write(alignment)

        writer.flush()
