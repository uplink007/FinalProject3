import numpy as np
import spacy
import os
from stanfordcorenlp import StanfordCoreNLP
from collections import defaultdict
from sklearn.utils import shuffle
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import precision_score as precision
from sklearn.metrics import recall_score as recall
from sklearn.metrics import f1_score


from DataModule import DataClass
from word2vec_module import MyWord2vec
from PreprocessDataModule import PreprocessClass
from DLModule import DLClass


if __name__ == '__main__':
    is_it_test = True
    path_to_word_2_vec = ""
    path_to_data = ""
    path_to_nlp = ""
    if os.name == "nt":
        if is_it_test :
            path_to_word_2_vec = r"E:\FinalProject3\GoogleNews-vectors-negative300.bin"
        else:
            path_to_word_2_vec = r"E:\FinalProject3\wiki.en.vec"
        path_to_data = r"E:\FinalProject3\data"
        path_to_nlp = r'E:\FinalProject3\stanford-corenlp-full-2018-02-27'
    else:
        if is_it_test :
            path_to_word_2_vec = "/home/ubuntu/Projet/FinalProject3/GoogleNews-vectors-negative300.bin"
        else:
            path_to_word_2_vec = "/home/ubuntu/Projet/FinalProject3/wiki.en.vec"
        path_to_data = "/home/ubuntu/Projet/FinalProject3/data/"
        path_to_nlp = "/home/ubuntu/Projet/FinalProject3/stanford-corenlp-full-2018-02-27"

    nlp = StanfordCoreNLP(path_to_nlp)
    dataset = DataClass(path_to_data)
    dataset.laod_data()
    modelwords = MyWord2vec(path_to_word_2_vec)
    # ("/home/ubuntu/Project/FinalProject/", "wiki.en.vec")
    modelwords.load_embeddings()
    try:
        modelwords.model["check"]
    except:
        print('word2vec not configure')

    preprocessData = PreprocessClass(dataset, modelwords, nlp,"ml")
    preprocessData.getMaxLength()
    preprocessData.preprocessing_data()
    preprocessData.set_depth()
    
    preprocessData.X,preprocessData.classified_output = shuffle(preprocessData.X,
                                                                preprocessData.classified_output,
                                                                random_state=0)
    kfold = StratifiedKFold(n_splits=10,shuffle=True,random_state=42)

    scores=defaultdict(int)
    nlp.close()
    for train,test in kfold.split(preprocessData.X,preprocessData.classified_output):
        nnmodel=DLClass()
        nnmodel.build_model(preprocessData.X[train],preprocessData.classified_output[train],"cblstm")
        print('Predicting...')
        preds=np.array([i[0] for i in nnmodel.model.predict_classes(preprocessData.X[test])])
        p=precision(preds,preprocessData.classified_output[test])
        r=recall(preds,preprocessData.classified_output[test])
        f1=f1_score(preds,preprocessData.classified_output[test])
        print('(Fold) Precision: ',p,' | Recall: ',r,' | F: ',f1)
        scores['Precision']+=p
        scores['Recall']+=r
        scores['F1']+=f1
    
    print('Overall scores:')
    for n,sc in scores.items():
        print(n,'-> ',sc/10*1.0)

