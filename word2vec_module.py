import sys
import gensim


class MyWord2vec(object):
    def __init__(self, path):
        self.path = path
        self.model = None
        self.vocab = None
        self.dims = None
        self.vocab = None

    def load_embeddings(self):
        try:
            print("" + self.path)
            self.model = gensim.models.Word2Vec.load(self.path)
        except:
            try:
                self.model = gensim.models.KeyedVectors.load_word2vec_format(self.path)
            except:
                try:
                    self.model = gensim.models.KeyedVectors.load_word2vec_format(self.path, binary=True)
                except:
                    try:
                        self.model = gensim.models.Word2Vec.load_word2vec_format(self.path, binary=True)
                    except:
                        sys.exit('Couldnt load embeddings')
        self.vocab=self.model.index2word
        self.dims=self.model.__getitem__(self.vocab[0]).shape[0]
        self.vocab=set(self.vocab)