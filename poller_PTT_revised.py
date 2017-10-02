# encoding: utf-8
from collections import Counter
import purewords as pw
import numpy as np
import pandas as pd
import ast
import csv
import jieba

from joblib import Parallel, delayed 
from tqdm import tqdm


data = pd.read_csv('/Users/y/Desktop/poller_dump/Gossiping09010930.csv')

# merge column "message" and column "description" as a string
# create a column named "allText"
data = data.assign(
    allText = (data['title'].astype(str) + data['body'].astype(str))
    )

# compute article popularity as total comments
# comments_list = ast.literal_eval(data['comments'].tolist()[5])
# comments final count
comments_home = []
comments_final = []

for c in tqdm(data['comments'].tolist()):
    parsed_c = ast.literal_eval(c)
    # get value
    comments_home.append(parsed_c)
    #print(parsed_l[-1])

# each "likes_dict" is a dict, thus we need more engineering
for comments_dict in tqdm(comments_home):
    comments_dict_list = list(comments_dict.values())[0]
    # get the first value from the list
    comments_final.append(comments_dict_list)
# now we have integers appended in the list!

data = data.assign(
    totalComments = comments_final,
    )

# done data cleaning!

#============term score calculation starts here================

# create a customized term filter for Poller
# DO NOT MESS WITH purewords/config/stopwords.text. Must create another filter.
filter_word = pd.read_csv('/Users/y/Desktop/poller_experiment/poller_filter.txt', sep=",", header=None, engine='python')
filter_words = filter_word[0].values.astype(str).tolist()
# print(filter_words.shape)
# text splitting using purewords
texts_clean = data['allText'][0:100].apply(lambda x: ' '.join(jieba.lcut(x))).str.cat(sep=' ')
print(len(texts_clean))
#texts_clean = jieba.lcut(texts)
#texts_clean = pw.clean_sentence(texts)
#print('pw')
#texts_clean = texts_clean.split()
print('split')
texts_array = texts_clean.split(' ')
print('are you dead?')
#cleaned = np.setdiff1d(texts_array.astype(str), filter_words[:, 0].astype(str))
# is an unique np array
import ipdb; ipdb.set_trace()

# create a baba of "weighted term frequency(wtf)"
# prolly looks like this: ('柯文哲': 2819730), ('馬英九': 467383)
# sort by word_count_sorted
# term_wtf_list = []
# unique_cleaned = []
data_list = []
for idx in tqdm(range(data.shape[0])[0:10]):
    data_list += [{'text': str(data[idx: idx+1]['allText'].values[0]), 
                   'score': int(data[idx: idx+1]['totalComments'].values[0])}]

def count_score(t, filter_words, data_list):
    if t not in filter_words:
        term_num = 0
        for datum in data_list:
            if t in datum['text']:
                term_num += datum['score']
        # term_num = data[data['allText'].apply(lambda x: t in x)]['totalComments'].sum()
        return t, term_num
    else:
        return t, 0
import ipdb; ipdb.set_trace() # it works!
 
# result = [] 
# for t in tqdm(list(set(texts_array))):
#     result += [count_score(t, filter_words, data)]


result = Parallel(n_jobs=-1, verbose=2)(
        delayed(count_score)(t, filter_words, data_list) for t in list(set(texts_array))
    )
import ipdb; ipdb.set_trace()


    # certain term's score in certain article
    # always reset to zero as we loop through another term
    #term_num = data[data['allText'].apply(lambda x: t in x)]['totalComments'].sum()
    # for index, article in data.iterrows():
    #     article_score = article['totalComments']
    #     if t in article['allText']:
    #         term_num += article_score
            # term_certain_tmp_list.append(term_num)
            # term_certain_max = max(term_certain_tmp_list)
    # derive max value and append it to term's list
    # term_wtf_list.append(term_certain_max)
    

print(term_wtf_list[0:10])
import ipdb; ipdb.set_trace()

# create a clean and sorted list of unique terms(sorted by wtf)
term_sorted_list = [] 
for i in cleaned:
    term_sorted_list.append(i)

# 馬英九：25071, 柯文哲：3196, 的：337202

# combine term & wtf
term_wtf_combined = list(zip(term_sorted_list, term_wtf_list))
term_final_list = sorted(term_wtf_combined, key=lambda x: x[1], reverse=True) # 完成！

# export the dataframe as csv!
final_data = pd.DataFrame(term_final_list, columns=['PTT_term', 'PTT_wtf'])
final_data.to_csv('PTT_WTF_numpytry_gossiping.csv', header=True)
