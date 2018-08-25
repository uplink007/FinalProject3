import os
import sys
import numpy as np


class DataClass(object):
    def __init__(self,path):
        self.path=path
        self.instances=[]
        self.labels=[]
        #self.os=

    def laod_data(self):
        for root, subdirs, files in os.walk(self.path):
            for filename in files:
                if filename.startswith('wiki_'):
                    print('Load f: ', filename)
                    label=filename.split('_')[-1].replace('.txt', '')
                    doc = os.path.join(root, filename)
                    lines = open(doc, 'r', encoding='utf-8').readlines()
                    for idx,line in enumerate(lines):
                        if line.startswith('#'):
                            target = lines[idx+1].split(':')[0]
                            if target[0] == "!":
                                target = target[1:]
                            sent = line[2:].replace('TARGET', target).strip().lower()
                            if label == 'good':
                                self.labels.append(1)
                            else:
                                self.labels.append(0)
                            self.instances.append(sent)
                # if filename.startswith('definitions'):
                #     print('f: ',filename)
                #     label=filename.split('_')[-1].replace('.txt','')
                #     doc=os.path.join(root,filename)
                #     lines = open(doc, 'r',encoding='utf-8').readlines()
                #     for idx,line in enumerate(lines):
                #         sent=line.strip().lower()
                #         if label=='good':
                #             self.labels.append(1)
                #         else:
                #             self.labels.append(0)
                #         self.instances.append(sent)
        print("Loading Succeeded")
        self.labels = np.array(self.labels)
