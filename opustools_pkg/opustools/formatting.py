
def doc_name_type(wmode, write, print_file_names):
    """Select function for adding doc names"""

    normal_temp = '\n# {}\n# {}\n\n'
    moses_temp = '\n<fromDoc>{}</fromDoc>\n<toDoc>{}</toDoc>\n\n'
    link_temp = ' <linkGrp targType="s" fromDoc="{}" toDoc="{}">\n'

    #args = (src_doc_name, trg_doc_name, resultfile, mosessrc, mosestrg)
    def normal_write(*args):
        args[2].write(normal_temp.format(args[0], args[1]))
    def normal_print(*args):
        print(normal_temp.format(args[0], args[1]), end='')
    def moses_write(*args):
        args[2].write(moses_temp.format(args[0], args[1]))
    def moses_write_2(*args):
        args[3].write('\n<fromDoc>{}</fromDoc>\n\n'.format(args[0]))
        args[4].write('\n<toDoc>{}</toDoc>\n\n'.format(args[1]))
    def moses_print(*args):
        print(moses_temp.format(args[0], args[1]), end='')
    def links_write(*args):
        args[2].write(link_temp.format(args[0], args[1]))
    def links_print(*args):
        print(link_temp.format(args[0], args[1]), end='')
    def nothing(*args):
        pass

    if wmode == 'normal' and write:
        return normal_write
    if wmode == 'normal' and not write:
        return normal_print
    if wmode == 'moses' and print_file_names and not write:
        return moses_print
    if wmode == 'moses' and print_file_names and len(write) == 1:
        return moses_write
    if wmode == 'moses' and print_file_names and len(write) == 2:
        return moses_write_2
    if wmode == 'links'and write:
        return links_write
    if wmode == 'links'and not write:
        return links_print
    return nothing

def out_put_type(wmode, write):
    """Select function for outputting sentece pairs"""

    #args = (src_result, trg_result, resultfile, mosessrc, mosestrg, link_a)
    def normal_write(*args):
        args[2].write(args[0]+args[1])
    def normal_print(*args):
        print(args[0]+args[1], end='')
    def moses_write(*args):
        args[2].write(args[0][:-1]+'\t'+args[1])
    def moses_write_2(*args):
        args[3].write(args[0])
        args[4].write(args[1])
    def moses_print(*args):
        print(args[0][:-1]+'\t'+args[1], end='')
    def links_write(*args):
        str_link = '<link {} />\n'.format(' '.join(
            ['{}="{}"'.format(k, v) for k, v in args[5].items()]))
        args[2].write(str_link)
    def links_print(*args):
        str_link = '<link {} />\n'.format(' '.join(
            ['{}="{}"'.format(k, v) for k, v in args[5].items()]))
        print(str_link, end='')
    def nothing(*args):
        pass

    if wmode in ['normal', 'tmx'] and write:
        return normal_write
    if wmode in ['normal', 'tmx'] and not write:
        return normal_print
    if wmode == 'moses' and not write:
        return moses_print
    if wmode == 'moses' and len(write) == 1:
        return moses_write
    if wmode == 'moses' and len(write) == 2:
        return moses_write_2
    if wmode == 'links'and write:
        return links_write
    if wmode == 'links'and not write:
        return links_print
    return nothing

def sentence_format_type(wmode):
    """Select function for formatting sentences"""

    def normal(sentences, ids, direction, language):
        result = ''
        if len(sentences) == 0:
            result = '\n'
        if direction == 'src':
            result += '================================'
        for i, sentence in enumerate(sentences):
            result += ('\n('+direction+')="'+ids[i]+'">'+sentence)
        if direction == 'trg':
            result += '\n================================\n'
        return result

    def tmx(sentences, ids, direction, language):
        result = ''
        for sentence in sentences:
            if direction == 'src':
                result += '\t\t<tu>'
            result += ('\n\t\t\t<tuv xml:lang="' + language +
                    '"><seg>')
            result += sentence + '</seg></tuv>'
            if direction == 'trg':
                result += '\n\t\t</tu>\n'
        return result

    def moses(sentences, ids, direction, language):
        result = ' '.join(sentences) + '\n'
        return result

    format_fs = {'normal': normal, 'tmx': tmx, 'moses': moses, 'links': None}
    return format_fs[wmode]

def pair_format_type(wmode, switch_langs, format_sentences):
    """Select function for formatting sentence pairs"""

    #args = (link_a, src_parser, trg_parser, fromto)
    def normal(*args):
        str_src_ids, str_trg_ids = args[0]['xtargets'].split(';')
        src_ids = [sid for sid in str_src_ids.split(',')]
        trg_ids = [tid for tid in str_trg_ids.split(',')]

        src_sentences, src_attrs = args[1].read_sentence(src_ids)
        trg_sentences, trg_attrs = args[2].read_sentence(trg_ids)

        src_result = format_sentences(
                src_sentences, src_ids, 'src', args[3][0])
        trg_result = format_sentences(
                trg_sentences, trg_ids, 'trg', args[3][1])
        return src_result, trg_result

    def switch(*args):
        str_src_ids, str_trg_ids = args[0]['xtargets'].split(';')
        src_ids = [sid for sid in str_src_ids.split(',')]
        trg_ids = [tid for tid in str_trg_ids.split(',')]

        src_sentences, src_attrs = args[1].read_sentence(src_ids)
        trg_sentences, trg_attrs = args[2].read_sentence(trg_ids)

        src_result = format_sentences(
                trg_sentences, trg_ids, 'src', args[3][1])
        trg_result = format_sentences(
                src_sentences, src_ids, 'trg', args[3][0])
        return src_result, trg_result

    def nothing(*args):
        return None, None

    if wmode == 'links':
        return nothing
    elif switch_langs:
        return switch
    else:
        return normal
