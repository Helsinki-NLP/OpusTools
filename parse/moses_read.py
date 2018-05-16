import zipfile


class MosesRead:

    def __init__(self, path, corpus, src, trg):
        self.documents = zipfile.ZipFile(path, "r")
        self.source = self.documents.open(corpus + "." + src + "-" + trg + "." + src, "r")
        self.target = self.documents.open(corpus + "." + src + "-" + trg + "." + trg, "r")

    def readPair(self):
        return "(src)>" + self.source.readline().decode("utf-8") + \
               "(trg)>" + self.target.readline().decode("utf-8") + "================================"

    def printAll(self):
        for srcline in self.source:
            trgline = self.target.readline()
            print("(src)>" + srcline.decode("utf-8") + \
                  "(trg)>" + trgline.decode("utf-8") + "================================")

    def closeFiles(self):
        self.documents.close()
