import pke
from nltk.corpus import stopwords


class KeaExtractor:
    def __init__(self, source_name):
        self.stoplist = stopwords.words('russian')
        self.extractor = pke.supervised.Kea()
        self.source_name = source_name
        self.df = pke.load_document_frequency_file(input_file=f'source_names/{self.source_name}_kea_frequency.gz')

    def extract(self, article, n=10):
        self.extractor = pke.supervised.Kea()
        # 2. load the content of the document.
        self.extractor.load_document(input=article['full_text'], language='ru', normalization="stemming")

        self.extractor.candidate_selection(stoplist=self.stoplist)

        # 4. classify candidates as keyphrase or not keyphrase.
        self.extractor.candidate_weighting(model_file=f'source_names/{self.source_name}_kea_model.pickle', df=self.df)

        # 5. get the 10-highest scored candidates as keyphrases
        return [keyphrase for (keyphrase, score) in self.extractor.get_n_best(n=n)]
