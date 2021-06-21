import errno
import getopt
import io
import os
import re
import sys

from keywords import extract_keywords


def get_arguments():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "d:o:r:w:h",
                                   ["directory=", "output=", "ratio=", "words=", "help"])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        sys.exit(2)
    path = None
    out_path = "keywords/"
    ratio = 0.2
    words = None
    for o, a in opts:
        if o in ("-d", "--directory"):
            path = a
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-o", "--output"):
            out_path = a
        elif o in ("-w", "--words"):
            words = int(a)
        elif o in ("-r", "--ratio"):
            ratio = float(a)
        else:
            assert False, "unhandled option"

    return path, out_path, ratio, words


help_text = """Usage: python textrank_directory.py -d DOCS_DIRECTORY
-d DOCS_DIRECTORY, --directory=DOCS_DIRECTORY:
\tPath to directory with documents
-o OUT_DIRECTORY, --output=OUT_DIRECTORY:
\tPath to directory with result keywords
-r RATIO, --ratio=RATIO:
\tFloat number (0,1] that defines the length of the summary. It's a proportion of the original text. Default value: 0.2.
-w WORDS, --words=WORDS:
\tNumber to limit the length of the summary. The length option is ignored if the word limit is set.
-h, --help:
\tprints this help
"""


def usage():
    print(help_text)


def write_file(keyphrases, file_name, out_path):
    "outputs the keyphrases to appropriate files"
    base_file_name = os.path.splitext(file_name)[0]
    try:
        os.makedirs(out_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(out_path):
            pass
        else:
            raise
    print("Generating output to " + out_path + base_file_name + '.key')
    keyphrase_file = io.open(out_path + base_file_name + '.key', 'w')
    for keyphrase in keyphrases:
        keyphrase_file.write(keyphrase)
    keyphrase_file.close()
    print("-")


def main():
    path, out_path, ratio, words = get_arguments()

    documents = os.listdir(path)
    r = re.compile('.*.txt')
    documents = filter(r.match, documents)

    for doc_name in documents:
        print('Reading ' + path + doc_name)
        doc_file = io.open(path + doc_name, 'r')
        text = doc_file.read()
        doc_keywords = extract_keywords(text, ratio, words)
        write_file(doc_keywords, doc_name, out_path)


if __name__ == "__main__":
    main()
