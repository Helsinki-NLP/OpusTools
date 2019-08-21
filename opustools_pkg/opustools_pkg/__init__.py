from .opus_cat import OpusCat
from .opus_read import OpusRead
from .opus_get import OpusGet

class OpusGetSents(OpusRead):

    def __init__(self, arguments):
        super().__init__(arguments)
        self.sents = []

    def sendPairOutput(self, wpair):
        self.sents.append(wpair)

