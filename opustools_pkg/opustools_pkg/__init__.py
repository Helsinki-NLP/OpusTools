from .opus_cat import OpusCat
from .opus_read import OpusRead

class OpusGetSents(OpusRead):

    def __init__(self, arguments):
        super().__init__(arguments)
        self.sents = []

    def sendPairOutput(self, wpair):
        self.sents.append(wpair)

