###################################################################
# Usage:                                                          #
###################################################################
# reader = AlignmentReader('OpenSubtitles', 'de', 'en')           #
#                                                                 #
# with AlignmentWriter('out.de-en.de', 'out.de-en.en') as writer: #
#     while reader.has_next():                                    #
#         alignment = reader.next()                               #
#         writer.write(alignment)                                 #
###################################################################


class AlignmentWriter:
    def __init__(self, src_path, trg_path, batch_size=1000):
        self.__buffer = []
        self.__batch_size = batch_size
        self.__src_path = src_path
        self.__trg_path = trg_path

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.flush()

    def flush(self):
        with open(self.__src_path, 'a') as src_file:
            with open(self.__trg_path, 'a') as trg_file:
                for alignment in self.__buffer:
                    src_file.write(alignment.source_str() + '\n')
                    trg_file.write(alignment.target_str() + '\n')

        self.__buffer.clear()

    def write(self, alignment):
        self.__buffer.append(alignment)
        if len(self.__buffer) >= self.__batch_size:
            self.flush()
