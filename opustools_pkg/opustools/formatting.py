import html


def file_header_type(wmode, write, source_lang):
    """Select function for adding file header"""

    tmxheader = ('<?xml version="1.0" encoding="utf-8"?>\n<tmx '
        'version="1.4.">\n<header srclang="' + source_lang +
        '"\n\tadminlang="en"\n\tsegtype="sentence"\n\tdatatype='
        '"PlainText" />\n\t<body>\n')
    linkheader = ('<?xml version="1.0" encoding="utf-8"?>\n'
        '<!DOCTYPE cesAlign PUBLIC "-//CES//DTD XML cesAlign//EN" "">\n'
        '<cesAlign version="1.0">\n')

    def tmx_write(resultfile):
        resultfile.write(tmxheader)
    def tmx_print(resultfile):
        print(tmxheader, end='')
    def link_write(resultfile):
        resultfile.write(linkheader)
    def link_print(resultfile):
        print(linkheader, end='')
    def nothing(resultfile):
        pass

    if write:
        if wmode == 'tmx':
            return tmx_write
        if wmode == 'links':
            return link_write
    else:
        if wmode == 'tmx':
            return tmx_print
        if wmode == 'links':
            return link_print
    return nothing

def doc_name_type(wmode, write, print_file_names):
    """Select function for adding doc names"""

    normal_temp = '\n# {}\n# {}\n'
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

def doc_ending_type(wmode, write):
    """Select function for adding document ending"""

    linkend = ' </linkGrp>\n'
    normalend = '\n================================\n'

    def normal_write(resultfile):
        resultfile.write(normalend)
    def normal_print(resultfile):
        print(normalend, end='')
    def link_write(resultfile):
        resultfile.write(linkend)
    def link_print(resultfile):
        print(linkend, end='')
    def nothing(resultfile):
        pass

    if write:
        if wmode == 'normal':
            return normal_write
        if wmode == 'links':
            return link_write
    else:
        if wmode == 'normal':
            return normal_print
        if wmode == 'links':
            return link_print
    return nothing

def file_ending_type(wmode, write):
    """Select function for adding file ending"""
    tmxend = '\t</body>\n</tmx>\n'
    linkend = '</cesAlign>\n'

    def tmx_write(resultfile):
        resultfile.write(tmxend)
    def tmx_print(resultfile):
        print(tmxend, end='')
    def link_write(resultfile):
        resultfile.write(linkend)
    def link_print(resultfile):
        print(linkend, end='')
    def nothing(resultfile):
        pass

    if write:
        if wmode == 'tmx':
            return tmx_write
        if wmode == 'links':
            return link_write
    else:
        if wmode == 'tmx':
            return tmx_print
        if wmode == 'links':
            return link_print
    return nothing



def write_id_line_type(switch_langs, attribute):
    """Select function for writing id lines"""

    id_temp = '{}\t{}\t{}\t{}\t{}\n'

    def normal(link_a, id_file, src_doc, trg_doc):
        ids = link_a['xtargets'].split(';')
        if attribute in link_a.keys():
            id_file.write(id_temp.format(
                src_doc, trg_doc, ids[0], ids[1], link_a[attribute]))
        else:
            id_file.write(id_temp.format(
                src_doc, trg_doc, ids[0], ids[1], 'None'))

    def normal_no_attr(link_a, id_file, src_doc, trg_doc):
        ids = link_a['xtargets'].split(';')
        id_file.write(id_temp.format(
            src_doc, trg_doc, ids[0], ids[1], 'None'))

    def switch(link_a, id_file, src_doc, trg_doc):
        ids = link_a['xtargets'].split(';')
        if attribute in link_a.keys():
            id_file.write(id_temp.format(
                trg_doc, src_doc, ids[1], ids[0], link_a[attribute]))
        else:
            id_file.write(id_temp.format(
                trg_doc, src_doc, ids[1], ids[0], 'None'))

    def switch_no_attr(link_a, id_file, src_doc, trg_doc):
        ids = link_a['xtargets'].split(';')
        id_file.write(id_temp.format(
            trg_doc, src_doc, ids[1], ids[0], 'None'))

    if switch_langs:
        if attribute:
            return switch
        else:
            return switch_no_attr
    else:
        if attribute:
            return normal
        else:
            return normal_no_attr

def out_put_type(wmode, write, write_ids, switch_langs, attribute, moses_del):
    """Select function for outputting sentence pairs"""

    #args = (src_result, trg_result, resultfile, mosessrc, mosestrg, link_a,
    #       id_file, src_doc_name, trg_doc_name)
    def normal_write(*args):
        args[2].write(args[0]+args[1])
    def normal_print(*args):
        print(args[0]+args[1], end='')
    def moses_write(*args):
        src = args[0].rstrip('\n').replace('\n', ' ')
        tgt = args[1].rstrip('\n').replace('\n', ' ')
        args[2].write(src + moses_del + tgt + '\n')
    def moses_write_2(*args):
        src = args[0].rstrip('\n').replace('\n', ' ')
        tgt = args[1].rstrip('\n').replace('\n', ' ')
        args[3].write(src + '\n')
        args[4].write(tgt + '\n')
    def moses_print(*args):
        src = args[0].rstrip('\n').replace('\n', ' ')
        tgt = args[1].rstrip('\n').replace('\n', ' ')
        print(src + moses_del + tgt)
    def links_write(*args):
        str_link = '<link {} />\n'.format(' '.join(
            ['{}="{}"'.format(k, v) for k, v in args[5].items()]))
        args[2].write(str_link)
    def links_print(*args):
        str_link = '<link {} />\n'.format(' '.join(
            ['{}="{}"'.format(k, v) for k, v in args[5].items()]))
        print(str_link, end='')

    write_id_line = write_id_line_type(switch_langs, attribute)

    def normal_write_id(*args):
        args[2].write(args[0]+args[1])
        write_id_line(args[5], args[6], args[7], args[8])
    def normal_print_id(*args):
        print(args[0]+args[1], end='')
        write_id_line(args[5], args[6], args[7], args[8])
    def moses_write_id(*args):
        src = args[0].rstrip('\n').replace('\n', ' ')
        tgt = args[1].rstrip('\n').replace('\n', ' ')
        args[2].write(src + moses_del + tgt + '\n')
        write_id_line(args[5], args[6], args[7], args[8])
    def moses_write_2_id(*args):
        src = args[0].rstrip('\n').replace('\n', ' ')
        tgt = args[1].rstrip('\n').replace('\n', ' ')
        args[3].write(src + '\n')
        args[4].write(tgt + '\n')
        write_id_line(args[5], args[6], args[7], args[8])
    def moses_print_id(*args):
        src = args[0].rstrip('\n').replace('\n', ' ')
        tgt = args[1].rstrip('\n').replace('\n', ' ')
        print(src + moses_del + tgt)
        write_id_line(args[5], args[6], args[7], args[8])
    def links_write_id(*args):
        str_link = '<link {} />\n'.format(' '.join(
            ['{}="{}"'.format(k, v) for k, v in args[5].items()]))
        args[2].write(str_link)
        write_id_line(args[5], args[6], args[7], args[8])
    def links_print_id(*args):
        str_link = '<link {} />\n'.format(' '.join(
            ['{}="{}"'.format(k, v) for k, v in args[5].items()]))
        print(str_link, end='')
        write_id_line(args[5], args[6], args[7], args[8])

    def nothing(*args):
        pass

    if write_ids:
        if wmode in ['normal', 'tmx'] and write:
            return normal_write_ids
        if wmode in ['normal', 'tmx'] and not write:
            return normal_print_id
        if wmode == 'moses' and not write:
            return moses_print_id
        if wmode == 'moses' and len(write) == 1:
            return moses_write_id
        if wmode == 'moses' and len(write) == 2:
            return moses_write_2_id
        if wmode == 'links'and write:
            return links_write_id
        if wmode == 'links'and not write:
            return links_print_id
    else:
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

def sentence_format_type(wmode, fromto):
    """Select function for formatting sentences"""

    def normal_src(sentences, ids):
        result = '\n================================'
        for i, sentence in enumerate(sentences):
            result += ('\n(src)="'+ids[i]+'">'+sentence)
        return result

    def normal_trg(sentences, ids):
        result = ''
        for i, sentence in enumerate(sentences):
            result += ('\n(trg)="'+ids[i]+'">'+sentence)
        return result

    def tmx_src(sentences, ids):
        result = ''
        for sentence in sentences:
            result += '\t\t<tu>'
            result += ('\n\t\t\t<tuv xml:lang="' + fromto[0] + '"><seg>')
            result += html.escape(sentence, quote=False) + '</seg></tuv>'
        return result

    def tmx_trg(sentences, ids):
        result = ''
        for sentence in sentences:
            result += ('\n\t\t\t<tuv xml:lang="' + fromto[1] + '"><seg>')
            result += html.escape(sentence, quote=False) + '</seg></tuv>'
            result += '\n\t\t</tu>\n'
        return result

    def moses(sentences, ids):
        result = ' '.join(sentences) + '\n'
        return result

    format_fs = {'normal': (normal_src, normal_trg),
            'tmx': (tmx_src, tmx_trg),
            'moses': (moses, moses),
            'links': (None, None)}

    return format_fs[wmode]

def check_lang_confs(lang_filters, attrs):
    names = ('cld2', 'langid')
    for attr in attrs:
        for i, lf in enumerate(lang_filters):
            if lf:
                label = attr[names[i]]
                true_label = lf[0]
                if label != true_label:
                    return False
                score = attr[names[i]+'conf']
                threshold = lf[1]
                if score < threshold:
                    return False
    return True

def check_lang_conf_type(lang_filters):
    def check(src_attrs, trg_attrs):
        return (not check_lang_confs(lang_filters[:2], src_attrs) or
                not check_lang_confs(lang_filters[2:], trg_attrs))
    def no_check(src_attrs, trg_attrs):
        return False

    if any(lang_filters):
        return check, True
    else:
        return no_check, False

def pair_format_type(wmode, switch_langs, check_filters, check_lang,
        format_sentences):
    """Select function for formatting sentence pairs"""

    #args = (link_a, src_parser, trg_parser, fromto)
    def normal(*args):
        str_src_ids, str_trg_ids = args[0]['xtargets'].split(';')
        src_ids = str_src_ids.split()
        trg_ids = str_trg_ids.split()

        src_sentences, src_attrs = args[1].read_sentence(src_ids)
        trg_sentences, trg_attrs = args[2].read_sentence(trg_ids)

        if check_filters(src_attrs, trg_attrs):
            return -1, -1

        src_result = format_sentences[0](src_sentences, src_ids)
        trg_result = format_sentences[1](trg_sentences, trg_ids)
        return src_result, trg_result

    def switch(*args):
        str_src_ids, str_trg_ids = args[0]['xtargets'].split(';')
        src_ids = str_src_ids.split()
        trg_ids = str_trg_ids.split()

        src_sentences, src_attrs = args[1].read_sentence(src_ids)
        trg_sentences, trg_attrs = args[2].read_sentence(trg_ids)

        if check_filters(src_attrs, trg_attrs):
            return -1, -1

        src_result = format_sentences[0](trg_sentences, trg_ids)
        trg_result = format_sentences[1](src_sentences, src_ids)
        return src_result, trg_result

    def link_with_filter(*args):
        str_src_ids, str_trg_ids = args[0]['xtargets'].split(';')
        src_ids = str_src_ids.split()
        trg_ids = str_trg_ids.split()

        src_sentences, src_attrs = args[1].read_sentence(src_ids)
        trg_sentences, trg_attrs = args[2].read_sentence(trg_ids)

        if check_filters(src_attrs, trg_attrs):
            return -1, -1
        return None, None

    def nothing(*args):
        return None, None

    if wmode == 'links':
        if check_lang:
            return link_with_filter
        else:
            return nothing
    elif switch_langs:
        return switch
    else:
        return normal

