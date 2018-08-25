import numpy as np
import spacy
import json
from collections import namedtuple
import pickle


class PreprocessClass(object):
    def __init__(self, datasetObject, model, nlp,depth,train=True):
        self.train = train
        self.depth = depth
        self.maxlen = 0
        self.instances = datasetObject.instances
        self.X = []
        self.my_vec_model = model
        self.classified_output = np.array(datasetObject.labels)
        self.deps2ids = {}
        self.nlp = nlp
        self.depid = 0
        self.ids2deps = None
        self.X_wordpairs = []
        self.X_deps = []

    def __set_depth(self):
        if self.depth == 'ml':
            X_enriched = np.concatenate([self.X, self.X_deps], axis=1)
        elif self.depth == 'm':
            X_enriched = np.concatenate([self.X, self.X_wordpairs], axis=1)
        else:
            X_enriched = self.X
        self.X=X_enriched

    def getMaxLength(self):
        if self.train:
            return
        print('Getting maxlen')
        maxlen_dep = 0
        for idx, sent in enumerate(self.instances):
            if idx % 100 == 0:
                print('Done ', idx, ' of ', len(self.instances))
            try:
                sent_maxlen_dep = 0
                doc = self.nlp.dependency_parse(sent)
                if len(doc) > self.maxlen:
                    self.maxlen = len(doc)
                doc_set = set([k[0] for k in doc])
                for token in doc_set:
                    if token not in self.deps2ids:
                        self.deps2ids[token] = self.depid
                        self.depid += 1
                        sent_maxlen_dep += 1
                if sent_maxlen_dep > maxlen_dep:
                    maxlen_dep = sent_maxlen_dep
            except UnicodeDecodeError:
                print('Cant process sentence: ', sent)
        self.maxlen = max(self.maxlen, maxlen_dep)
        self.ids2deps = dict([(idx, dep) for dep, idx in self.deps2ids.items()])

    def pad_words(self, tokens, append_tuple=False,predict=False):
        if not predict:
            if len(tokens) > self.maxlen:
                return tokens[:self.maxlen]
            else:
                dif = self.maxlen-len(tokens)
                for i in range(dif):
                    if not append_tuple:
                        tokens.append('UNK')
                    else:
                        tokens.append(('UNK', 'UNK'))
                return tokens
        else:
            if len(tokens) > self.maxlen:
                return tokens[:self.maxlen]
            else:
                dif = self.maxlen - len(tokens)
                for i in range(dif):
                    if not append_tuple:
                        tokens.append('UNK')
                    else:
                        tokens.append(('UNK', 'UNK'))
                return tokens

    @staticmethod
    def get_pair_words(json_object):
        result = {}
        res ={}
        [res.update({k['dependent']: k['dep']}) for k in json_object['sentences'][0]['basicDependencies']]
        for idx, k in enumerate(json_object['sentences'][0]['basicDependencies'][1:]):
            result[idx] = {'parent_word' : json_object['sentences'][0]['basicDependencies'][1:][idx]['governorGloss'],
                           'parent_dep' : res[json_object['sentences'][0]['basicDependencies'][1:][idx]['governor']],
                           'child_word' : json_object['sentences'][0]['basicDependencies'][1:][idx]['dependentGloss'],
                           'child_dep' : json_object['sentences'][0]['basicDependencies'][1:][idx]['dep']}
        return result

    def preprocessing_data(self):
        if not self.train:
            self.load_all()
            return
        for idx, sent in enumerate(self.instances):
            if idx % 100 == 0:
                print('Done ', idx, ' of ', len(self.instances))
            object_json_data = json.loads(self.nlp.annotate(sent, properties={'annotators': 'tokenize', 'outputFormat': 'json'}))
            tokens = [k['word'].lower() for k in object_json_data['tokens']]
            sent_matrix = []
            for token in self.pad_words(tokens):
                if token in self.my_vec_model.vocab:
                    # each word vector is embedding dim + length of one-hot encoded label
                    vec = np.concatenate([self.my_vec_model.model[token], np.zeros(len(self.ids2deps)+1)])
                    sent_matrix.append(vec)
                else:
                    sent_matrix.append(np.zeros(self.my_vec_model.dims + len(self.ids2deps) + 1))
            sent_matrix=np.array(sent_matrix)
            self.X.append(sent_matrix)
        self.X = np.array(self.X)

        for idx, sent in enumerate(self.instances):
            if idx % 10 == 0:
                print('Done ', idx, ' of ', len(self.instances))
            object_json_data = json.loads(self.nlp.annotate(sent, properties={'annotators': 'depparse', 'outputFormat': 'json'}))
            tokens = PreprocessClass.get_pair_words(object_json_data)
            word_pairs = []
            dep_pairs = []
            for idx2,tok in tokens.items():
                word_pairs.append((tok['parent_word'], tok['child_word']))
                dep_pairs.append((tok['parent_dep'], tok['child_dep']))
            self.pad_words(word_pairs, append_tuple=True)
            self.pad_words(dep_pairs,append_tuple=True)
            dep_labels = [j for i, j in dep_pairs]
            avg_sent_matrix = []
            avg_label_sent_matrix = []
            for idx, word_pair in enumerate(word_pairs):
                head, modifier = word_pair[0], word_pair[1]
                if head in self.my_vec_model.vocab and not head == 'UNK':
                    head_vec = self.my_vec_model.model[head]
                else:
                    head_vec = np.zeros(self.my_vec_model.dims)
                if modifier in self.my_vec_model.vocab and not modifier == 'UNK':
                    modifier_vec = self.my_vec_model.model[modifier]
                else:
                    modifier_vec = np.zeros(self.my_vec_model.dims)
                avg = np.mean(np.array([head_vec, modifier_vec]),axis=0)
                if dep_labels[idx] != 'UNK':
                    dep_idx = self.deps2ids[dep_labels[idx]]
                else:
                    dep_idx = -1
                dep_vec = np.zeros(len(self.deps2ids) + 1)
                dep_vec[dep_idx] = 1
                avg_label_vec = np.concatenate([avg, dep_vec])
                avg_sent_matrix.append(np.concatenate([avg, np.zeros(len(self.deps2ids) + 1)]))
                avg_label_sent_matrix.append(avg_label_vec)
            wp = np.array(avg_sent_matrix)
            labs = np.array(avg_label_sent_matrix)
            self.X_wordpairs.append(wp)
            self.X_deps.append(labs)

        self.X_wordpairs = np.array(self.X_wordpairs)
        self.X_deps = np.array(self.X_deps)
        self.__set_depth()
        self.save_stats()

    def preprocessed_one(self,sent,ids_len,max_length):
        object_json_data = json.loads(self.nlp.annotate(sent, properties={'annotators': 'tokenize', 'outputFormat': 'json'}))
        tokens = [k['word'].lower() for k in object_json_data['tokens']]
        sent_matrix = []
        for token in self.pad_words(tokens):
            if token in self.my_vec_model.vocab:
                # each word vector is embedding dim + length of one-hot encoded label
                vec = np.concatenate([self.my_vec_model.model[token], np.zeros(len(self.ids2deps) + 1)])
                sent_matrix.append(vec)
            else:
                sent_matrix.append(np.zeros(self.my_vec_model.dims + len(self.ids2deps) + 1))
        sent_matrix_X = np.array(sent_matrix)

        object_json_data = json.loads(self.nlp.annotate(sent, properties={'annotators': 'depparse', 'outputFormat': 'json'}))
        tokens = PreprocessClass.get_pair_words(object_json_data)
        word_pairs = []
        dep_pairs = []
        for idx2, tok in tokens.items():
            word_pairs.append((tok['parent_word'], tok['child_word']))
            dep_pairs.append((tok['parent_dep'], tok['child_dep']))
        self.pad_words(word_pairs, append_tuple=True)
        self.pad_words(dep_pairs, append_tuple=True)
        dep_labels = [j for i, j in dep_pairs]
        avg_sent_matrix = []
        avg_label_sent_matrix = []
        for idx, word_pair in enumerate(word_pairs):
            head, modifier = word_pair[0], word_pair[1]
            if head in self.my_vec_model.vocab and not head == 'UNK':
                head_vec = self.my_vec_model.model[head]
            else:
                head_vec = np.zeros(self.my_vec_model.dims)
            if modifier in self.my_vec_model.vocab and not modifier == 'UNK':
                modifier_vec = self.my_vec_model.model[modifier]
            else:
                modifier_vec = np.zeros(self.my_vec_model.dims)
            avg = np.mean(np.array([head_vec, modifier_vec]), axis=0)
            if dep_labels[idx] != 'UNK':
                dep_idx = self.deps2ids[dep_labels[idx]]
            else:
                dep_idx = -1
            dep_vec = np.zeros(len(self.deps2ids) + 1)
            dep_vec[dep_idx] = 1
            avg_label_vec = np.concatenate([avg, dep_vec])
            avg_sent_matrix.append(np.concatenate([avg, np.zeros(len(self.deps2ids) + 1)]))
            avg_label_sent_matrix.append(avg_label_vec)
        sent_wp = np.array(avg_sent_matrix)
        sent_labs = np.array(avg_label_sent_matrix)

        if self.depth == 'ml':
            sent_X = np.concatenate([sent_matrix_X, sent_labs], axis=1)
        elif self.depth == 'm':
            sent_X = np.concatenate([sent_matrix_X, sent_wp], axis=1)
        else:
            sent_X = sent_matrix_X
        return sent_X

    @staticmethod
    def save_obj(obj, name):
        with open('obj/' + name + '.pkl', 'wb') as f:
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load_obj(name):
        with open('obj/' + name + '.pkl', 'rb') as f:
            return pickle.load(f)

    def save_stats(self):
        self.save_obj(self.ids2deps,"ids2deps")
        self.save_obj(self.deps2ids,"deps2ids")
        self.save_obj(self.maxlen,"maxlen")

    def load_all(self):
        self.ids2deps = self.load_obj(self.ids2deps,"ids2deps")
        self.deps2ids = self.load_obj(self.deps2ids,"deps2ids")
        self.maxlen = self.load_obj(self.maxlen,"maxlen")






