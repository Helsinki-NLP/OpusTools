
import urllib.request, json, argparse, sys

class OpusGet:

    def __init__(self, arguments):
        parser = argparse.ArgumentParser(prog="opus-get", description="Download files from OPUS")
        parser.add_argument("-s", help="Source language", required=True)
        parser.add_argument("-t", help="Target language")
        parser.add_argument("-d", help="Corpus name")
        parser.add_argument("-r", help="Release")
        parser.add_argument("-p", help="Pre-process type")
        parser.add_argument("-l", help="List resources", action="store_true")
        parser.add_argument("-dl", help="Set download directory (default=current directory)", default="")

        if len(arguments) == 0:
            self.args = parser.parse_args()
        else:
            self.args = parser.parse_args(arguments)

        self.url = "https://vm1617.kaj.pouta.csc.fi/opusapi/?"
        urlparts = {"s": "source", "t": "target", "d": "corpus", "r": "version", "p": "preprocessing"}

        for a in urlparts.keys():
            if self.args.__dict__[a]:
                if self.args.__dict__[a] == " ":
                    self.url += urlparts[a] + "=&"
                else:
                    self.url += urlparts[a] + "=" + self.args.__dict__[a] + "&"

    def round_size(self, size, length, unit):
        last_n = str(size)[-length]
        size = int(str(size)[:-length])
        if int(last_n) >= 5:
            size += 1
        size = str(size) + unit
        return size
        
    def format_size(self, size):
        if len(str(size)) > 9:
            size = self.round_size(size, 9, " TB")
        elif len(str(size)) > 6:
            size = self.round_size(size, 6, " GB")
        elif len(str(size)) > 3:
            size = self.round_size(size, 3, " MB")
        else:
            size = str(size) + " KB"
        return(size)


    def get_response(self, url):
        response = urllib.request.urlopen(url[:-1])
        data = json.loads(response.read())

        return data

    def add_data_with_aligment(self, tempdata, retdata):
        for i in tempdata:
            if i["preprocessing"] == "xml" and i["source"] == self.args.s and i["target"] == self.args.t:
                retdata += tempdata
                break
        return retdata
            
    def remove_data_with_no_alignment(self, data):
        retdata = []
        tempdata = []
        prev_directory = ""
        
        for c in data["corpora"]:
            directory = "/{0}/{1}".format(c["corpus"], c["version"])
            if prev_directory != "" and prev_directory!=directory:
                retdata = self.add_data_with_aligment(tempdata, retdata)
                tempdata = []
            tempdata.append(c)
            prev_directory = directory

        retdata = self.add_data_with_aligment(tempdata, retdata)
        return retdata

    def get_corpora_data(self):
        file_n = 0
        total_size = 0

        data = self.get_response(self.url)

        if self.args.t and self.args.t != " " and not self.args.p:
            corpora = self.remove_data_with_no_alignment(data)
        else:
            corpora = data["corpora"]

        for c in corpora:
            file_n += 1
            total_size += c["size"]

        total_size = self.format_size(total_size)

        return corpora, file_n, total_size

    def progress_status(self, count, blockSize, totalSize):
        percent = int(count*blockSize*100/totalSize)
        print("\r{0} ... {1}% of {2}".format(self.filename, percent, self.filesize), end="", flush=True)
    
    def download(self, corpora, file_n, total_size):
        answer = input("Downloading " + str(file_n) + " file(s) with the total size of " + total_size + ". Continue? (y/n) ")
            
        if answer == "y":
            for c in corpora:
                self.filename = c["url"].replace("/", "_")
                self.filesize = self.format_size(c["size"])
                try:
                    urllib.request.urlretrieve("https://object.pouta.csc.fi/OPUS/" + c["url"],
                                               self.args.dl + self.filename, reporthook=self.progress_status)
                    print("")
                except urllib.error.URLError as e:
                    print("Unable the retrieve the data.")
                    return

    def print_files(self, corpora, file_n, total_size):
        for c in corpora:
            print("{0:>7} {1:s}".format(self.format_size(c["size"]), c["url"]))
        print("\n{0:>7} {1:s}".format(total_size, "Total size"))

    
    def get_files(self):
        try:
            corpora, file_n, total_size = self.get_corpora_data()
        except urllib.error.URLError as e:
            print("Unable to retrieve the data.")
            return

        if not self.args.l:
            self.download(corpora, file_n, total_size)
        else:
            self.print_files(corpora, file_n, total_size)

