import string

import pke
from nltk.corpus import stopwords


class MultipartiterankExtractor:
    def __init__(self, source_name):
        self.extractor = pke.unsupervised.MultipartiteRank()
        self.source_name = source_name
        self.stoplist = list(string.punctuation)
        self.stoplist += ['-lrb-', '-rrb-', '-lcb-', '-rcb-', '-lsb-', '-rsb-']
        self.stoplist += stopwords.words('russian')
        self.pos = {'NOUN', 'PROPN', 'ADJ'}

    def extract(self, article, n=10):
        self.extractor = pke.unsupervised.MultipartiteRank()
        self.extractor.load_document(input=article['full_text'], language='ru', normalization="stemming")
        self.extractor.candidate_selection(pos=self.pos, stoplist=self.stoplist)
        self.extractor.candidate_weighting(alpha=1.1, threshold=0.74, method='average')
        return [keyphrase for (keyphrase, score) in self.extractor.get_n_best(n=n)]
