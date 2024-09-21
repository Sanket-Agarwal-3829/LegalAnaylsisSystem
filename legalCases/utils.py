from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from transformers import PegasusForConditionalGeneration, PegasusTokenizer, Trainer, TrainingArguments
import glob
from nltk import tokenize
import nltk
import transformers
from torch.utils.data import DataLoader, TensorDataset, random_split, RandomSampler, Dataset
import pandas as pd
import numpy as np
import torch.nn.functional as F
import torch
import pandas as pd
import numpy as np
import glob
import sys
sys.path.insert(0, '../')
# from utilities import *
import os
import nltk

import spacy
from multi_rake import Rake

from sentence_transformers import util , SentenceTransformer


import re
import string
from gensim.models import Word2Vec
from nltk.tokenize import sent_tokenize as nlkt_sent_tokenize
from nltk.tokenize import word_tokenize as nlkt_word_tokenize
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from nltk.corpus import stopwords
from scipy.spatial.distance import cosine



import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import spacy

# nltk.download('stopwords')
def Summary_score (summary_input,summary):
    # print("45",summary_input)
    model = SentenceTransformer('bert-base-nli-mean-tokens')
    embedding1 = model.encode(summary_input, convert_to_tensor=True)
    embedding2 = model.encode(summary, convert_to_tensor=True)
    cosine_scores = util.pytorch_cos_sim(embedding1,embedding2)
    scores = cosine_scores.tolist()
    print("51",scores)

    # scores = list()
    # for i in summary:
    #     embedding2 = model.encode(i, convert_to_tensor=True)
    #     cosine_scores = util.pytorch_cos_sim(embedding1,embedding2)
    #     scores.append(cosine_scores.tolist())
    # print(scores)
    return scores

def Punctuation(string):
 
    # punctuation marks
    punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
 
    # traverse the given string and if any punctuation
    # marks occur replace it with null
    for x in string.lower():
        if x in punctuations:
            string = string.replace(x, "")
#     print(string)
    # Print string without punctuation
    return(string)

def tokenization(sentence):
    stop_words = set(stopwords.words('english'))
    word_tokens= []
    filtered_sentence = ''
    for w in sentence.split():
        if w not in stop_words:
            filtered_sentence += w
            filtered_sentence += ' '
#     print(filtered_sentence)    
    nlp =  spacy.load("en_core_web_sm")
    doc = nlp(filtered_sentence)
    for i in doc:
        word_tokens.append( i.lemma_)
#         print(i.lemma_)
#     print(word_tokens)
    return(word_tokens)

def NLP_Processing(summary_input , summary_list):
    print("In Nlp Processing")
    summary_scores = []
    summ = []

    summary_input = ' ' .join(tokenization(Punctuation(summary_input)))
    print("98",summary_input)
    for i in summary_list:
        try:
            summary= ' ' .join(tokenization(Punctuation(i)))
            print(summary)
            summ.append(summary)
        except Exception as e:
            print(i,"ssjs")
            print(e)
            summ.append('')
            pass
        print("109 ***********************************")
    return (Summary_score(summary_input,summ))


def nest_sentences(document,chunk_length):
    '''
    function to chunk a document
    input:  document           - Input document
            chunk_length        - chunk length
    output: list of chunks. Each chunk is a string.
    '''
    nested = []
    sent = []
    length = 0
    for sentence in nltk.sent_tokenize(document):
        length += len(sentence.split(" "))
        if length < chunk_length:
            sent.append(sentence)
        else:
            nested.append(" ".join(sent))
            sent = []
            sent.append(sentence)
            length = 0
    if len(sent)>0:
        nested.append(" ".join(sent))
    return nested

def summerize_doc(nested_sentences, p):
    '''
    Function to generate summary using chunking based Pegasus
    input:  nested_sentences - chunks
            p - Number of words in summaries per word in the document
    output: document summary
    '''
    print("model Inilization")
    tokenizer = AutoTokenizer.from_pretrained("nsi319/legal-pegasus")  
    model = AutoModelForSeq2SeqLM.from_pretrained("nsi319/legal-pegasus")
    print("model Inilization done")
    device = 'cuda'
    result = []
    for nested in nested_sentences:
        l = int(p * len(nested.split(" ")))
        max_len = l
        min_len = l-5
        print(max_len,min_len)
        result.append(summerize(nested, max_len, min_len,tokenizer,model))
        print("next")
    return result

def summerize(text, max_len, min_len,tokenizer,model):
    '''
    Function to generate summary using Pegasus
    input:  nested_sentences - chunks
            max_l - Maximum length
            min_l - Minimum length
    output: document summary
    '''
    

    try:
        input_tokenized = tokenizer.encode(text, return_tensors='pt',max_length=512,truncation=True)
        summary_ids = model.generate(input_tokenized,
                                          num_beams=2,
                                          length_penalty=0.1,
                                          min_length=min_len,
                                          max_length=max_len,
                                    )
        summary = [tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=False) for g in summary_ids][0]
        print("done")
        return summary
    except Exception as e:
        print("error", e)
        return ""
    
def score(query_df):
    final_score = []
    for i in range(len(query_df)):
        score = 0
        for j in range(1 , len(query_df.columns)):
            if query_df.iloc[i][j] == True:
                score += 1
            else :
                pass
        if score != 0:
            final_score.append((score*100)/(len(query_df.columns) - 1))
        else:
            final_score.append(0)
    query_df['score'] = final_score
    return(query_df)

def query(relation ,target ,kg_df , query_df):
  curr = set(list(kg_df.loc[kg_df['target'] == target]['source']))
  new = []
  for i in curr:
    if i in list(query_df['source']):
      query_df.loc[query_df['source'] == i ,target] = True
    else:
      new.append(i)
  print(new)
  new_dict = {'source':new , target: [True for i in range(len(new))]}
  q2 = pd.DataFrame(new_dict)
  query_df = pd.concat([query_df ,q2])
  return (query_df)


def NER(judgement,filename):
    # nlp = spacy.load("en_core_web_sm")
    print("loading")
    nlp = spacy.load("en_legal_ner_trf")
    print("loading Done")
    # text = "Section 319 Cr.P.C. contemplates a situation where the evidence adduced by the prosecution for Respondent No.3-G. Sambiah on 20th June 1984"
    doc = nlp(judgement)
    # relation =[]
    # target = []
    # source = []
    kk = pd.DataFrame(columns=["source","target","relation"])
    provision = []
    # Print indentified entites 
    for ent in doc.ents:
        print(ent)
        flag = True
        ent1= str(ent).lower()
        if ent.label_ == "PROVISION": 
            flag = False
            if (str(ent1).find("and") or str(ent1).find("&") or str(ent1).find("\n") or  str(ent1).find("/")):
                ent1 =  str(ent1).replace("and",",")
                ent1 =  str(ent1).replace("&",",")
                ent1 =  str(ent1).replace("\n",",")
                ent1 =  str(ent1).replace("/",",")
                ent1 =  str(ent1).replace("-"," ")
                    
                if ent1.count(",") > 0:
                    for en in ent1.split(","):
                        if en.lower().count("section")>0:
                            X = pd.DataFrame({"source":[filename],"target":[en.strip()],"relation":[str(ent.label_)]})
                            kk = pd.concat([kk,X]) 
                        else:
                            try:
                                en = str(int(en.strip()))
                                en = 'section ' + en
                                kk = pd.concat([kk,pd.DataFrame({"source":[filename],"target":[en.strip()],"relation":[str(ent.label_)]})]) 

                            except Exception as e:
                                if len(en)>0 and bool(re.search(r'\d', en)):
                                    kk = pd.concat([kk,pd.DataFrame({"source":[filename],"target":[en.strip()],"relation":[str(ent.label_)]})]) 
                                    pass
                else:
                    # print("section 4"+en.strip(),ent1)
                    kk = pd.concat([kk,pd.DataFrame({"source":[filename],"target":[ent1.strip()],"relation":[str(ent.label_)]})]) 
                
                    # final.add(ent1)


        if flag:
            # kk = kk.append({"source":filename,"target":str(ent1),"relation":str(ent.label_)},ignore_index=True)
            kk = pd.concat([kk,pd.DataFrame({"source":[filename],"target":[str(ent1).strip()],"relation":[str(ent.label_)]})]) 
            # print(ent,ent.label_)
            # source.append('Avinash_Mittal_vs_State_Of_Punjab_And_Another_on_11_April_2023.PDF')
            # target.append(str(ent))
            # relation.append(str(ent.label_))
    kk.reset_index(inplace=True)
    kk.drop(kk[kk['target']=="section"].index,inplace=True)
    print(len(kk))
    return(kk)


def Keywords(full_text):
  rake = Rake()
  keywords = rake.apply(full_text)
#   print(keywords    )
  keywords_input=[]
  for i in keywords:
    keywords_input.append(i[0])
  return (keywords_input)



def query(relation ,target ,kg_df , query_df):
  curr = set(list(kg_df.loc[kg_df['target'] == target]['source']))
  new = []
  for i in curr:
    if i in list(query_df['source']):
      query_df.loc[query_df['source'] == i ,target] = True
    else:
      new.append(i)
  print(new)
  new_dict = {'source':new , target: [True for i in range(len(new))]}
  q2 = pd.DataFrame(new_dict)
  query_df = pd.concat([query_df ,q2])
  return(query_df)


def Mix(t):
  return (1 / (1 + (np.exp(-t))) - 0.5) + ((np.log(1 + (np.exp(t))) - np.log(2)) ** 2)

def MinMaxScaler(t, a = 0, b = 1):
  N = (t - t.min()) * (b - a)
  D = t.max() - t.min()
  return (N / D) + a

def score1(keywords_input,keywords_saved):
  semantic_scores=[]
  print("score1")
  print("model Inilization")
  model = SentenceTransformer('bert-base-nli-mean-tokens')
  print("model Inilization done")
  print("createing embedding")
  embedding1 = model.encode(keywords_saved, convert_to_tensor=True)
  embedding2 = model.encode(keywords_input, convert_to_tensor=True)
  print("createing embedding done")
  print("calculate Similarity Score")
  cosine_scores = util.pytorch_cos_sim(embedding1,embedding2)
  scores = cosine_scores.tolist()
  print("calculate Similarity Score done")

  x_1 = np.arange(0, 1, 0.0001)
  for z in scores:
    for i in z:
      semantic_scores.append(MinMaxScaler(Mix(np.concatenate([x_1, np.array([i])])))[-1])
  count = 0
  for k in semantic_scores:
    if k >= 0.9:
      count +=1

  return count