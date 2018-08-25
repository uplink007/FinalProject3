# -*- coding: utf-8 -*-
"""
Created on Fri Aug 10 19:43:00 2018

@author: evgen
"""
import json
from bs4 import BeautifulSoup as soup
import re
from urllib.request import urlopen as uReq
from data import *
from definitions.url_Parse_Definitions import *
import pypandoc
from tools.general import *
import os.path
from stanfordcorenlp import StanfordCoreNLP
nlp = StanfordCoreNLP(r'D:\stanford-corenlp-full-2018-02-27\stanford-corenlp-full-2018-02-27')

#=========Function to open JSON file and replace spaces with '_' in all links========
#=========Return URL's as list
def OpenJson(Jfile):
    result = []
    with open(Jfile) as f:
        d = json.load(f)
    for key in d.keys():
        key = key.replace(" ","_")
        result.append(key)
    return result

#=========Function get URL's list and replace them to WiKi source URL's
#=========Return URL's as list
def Create_URL_List(ToAppend):
    result = []
    for line in ToAppend:
        line = 'https://groupprops.subwiki.org/w/index.php?title=' + line + '&action=edit'
        result.append(line)
    return result

#=========Parsing text from URL function
#=========Function get text area devided to Statement/Definiton area
    #=====Flag that define if Definition or Statement area
    #=====Current URL
    #=====Index for counting URL's from JSON file
    #=====Function will write to files parsed text
def parse2file(sentences, DorS, url, index):
    if os.path.isfile('Definitions.txt'):
        f1='a'
    else:
        f1='w'
    if os.path.isfile('DefinitionsURLs.txt'):
        f2='a'
    else:
        f2='w'
    if os.path.isfile('StatementsFromDefinitionsJSON.txt'):
        f3='a'
    else:
        f3='w'
    if os.path.isfile('StatementsFromDefinitionsJSON_URLs.txt'):
        f4='a'
    else:
        f4='w'
    filename =  open('Definitions.txt', f1, encoding = 'utf-8')
    filename1 =  open('DefinitionsURLs.txt', f2, encoding = 'utf-8')
    filename2 =  open('StatementsFromDefinitionsJSON.txt', f3, encoding = 'utf-8')
    filename3 =  open('StatementsFromDefinitionsJSON_URLs.txt', f4, encoding = 'utf-8')

    props={'annotators': 'ssplit','pipelineLanguage':'en','outputFormat':'JSON'}
    text2convert = pypandoc.convert_text(sentences, 'plain', format = 'mediawiki')
    if re.search('$', text2convert) is not None:
        text2convert = pypandoc.convert_text(text2convert, 'plain', format = 'vimwiki')
    js = json.loads(nlp.annotate(text2convert, properties=props))
    for sentence, sentences in enumerate(js['sentences']):
        result = ''
        for i, originalText in enumerate(js['sentences'][sentence]['tokens']):
            if i < len(js['sentences'][sentence]['tokens'])-1 :        
                result += originalText['originalText'] + ' '
            elif i >= len(js['sentences'][sentence]['tokens']) - 1 :
                result += originalText['originalText']
        if DorS == 'D':
            filename.write(result + '\n')
            filename1.write(result + '\n')
        if DorS == 'S':
            filename2.write(result + '\n')
            filename3.write(result + '\n')
    if DorS == 'D':
        filename.close()
        filename1.write(str(index) + '\n')
        filename1.write(url + '\n')
        filename1.close()
    if DorS == 'S':
        filename2.close()
        filename3.write(str(index) + '\n')
        filename3.write(url + '\n')
        filename3.close()

#=========================Real run+++++++++++++++
f = open('Definitions.txt', 'w')
f.close()
f = open('DefinitionsURLs.txt','w')
f.close()
f = open('StatementsFromDefinitionsJSON.txt', 'w')
f.close()
f = open('StatementsFromDefinitionsJSON_URLs.txt','w')
f.close()
fileName = open('AllText.txt' ,'w',  encoding = 'utf-8')
fileName.close()
res = Create_URL_List(OpenJson('data\\SubWiki.json'))
for indx, line in enumerate(res):
    string_ = url_Parse_Definitions(line)
    if string_.string[1] == True:
        parse2file(string_.string[0], string_.string[2], line, indx)

#=========================For Testing one URL Only+++++++++++++++
#f = open('test1.txt', 'w')
#f.close()
#f = open('test2.txt','w')
#f.close()
#f = open('test3.txt', 'w')
#f.close()
#f = open('test4.txt','w')
#f.close()
#
#url='https://groupprops.subwiki.org/w/index.php?title=Characterization_of_free_Lie_ring_in_terms_of_eigenspaces_of_Dynkin_operator&action=edit'
#string_ = url_Parse_Definitions(url)
#
#if string_.string[1] == True:
#    parse2file(string_.string[0], string_.string[2], url, 0)