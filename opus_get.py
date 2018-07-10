import urllib.request, json, argparse

class OpusGet:

    def __init__(self, arguments):
        parser = argparse.ArgumentParser(prog="opus-get", description="Download files from OPUS")
        parser.add_argument("-s", help="Source language", required=True)
        parser.add_argument("-t", help="Target language")
        parser.add_argument("-d", help="Corpus name")
        parser.add_argument("-r", help="Release")
        parser.add_argument("-p", help="Pre-process type")
        parser.add_argument("-l", help="List resources", action="store_true")

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

        
    def format_size(self, size):
        if len(str(size)) > 9:
            size = str(size)[:-9] + " TB"
        elif len(str(size)) > 6:
            size = str(size)[:-6] + " GB"
        elif len(str(size)) > 3:
            size = str(size)[:-3] + " MB"
        else:
            size = str(size) + " B"
        return(size)


    def get_response(self, url):
        response = urllib.request.urlopen(url[:-1])

        data = json.loads(response.read())

        return data

    def print_results(self):
        file_n = 0
        total_size = 0
        
        data = self.get_response(self.url)
        
        for c in data["corpora"]:
            file_n += 1
            total_size += c["size"]

        total_size = self.format_size(total_size)

        if not self.args.l:
            answer = input("Are you sure you want to download " + str(file_n) + " file(s) with total size of " + total_size + " ? (y/n) ")

            if answer == "y":
                for c in data["corpora"]:
                    print("{0:>7} {1:s}".format(self.format_size(c["size"]), c["url"]))
        else:
            for c in data["corpora"]:
                print("{0:>7} {1:s}".format(self.format_size(c["size"]), c["url"]))
            print("\n{0:>7} {1:s}".format(total_size, "total size"))

