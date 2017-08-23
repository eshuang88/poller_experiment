# encoding: utf-8
from collections import Counter
import purewords as pw
import numpy as np
import pandas as pd
import ast
import csv

data = pd.read_csv('/Users/y/Desktop/poller_dump/0804_FB_newsDeep.csv')
# merge column "message" and column "description" as a string
# create a column named "allText"
data = data.assign(
	allText = (data['message'].astype(str) + data['description'].astype(str))
	)

# compute article popularity as L + C + 10S
# find the last data point of likes/comments/shares
likes_list = ast.literal_eval(data['likes'].tolist()[5])
comments_list = ast.literal_eval(data['comments'].tolist()[5])
shares_list = ast.literal_eval(data['shares'].tolist()[5])

# likes final count
likes_home = []
likes_final = []

for l in data['likes'].tolist():
    parsed_l = ast.literal_eval(l)
    # get value
    likes_home.append(parsed_l[-1])
    #print(parsed_l[-1])

# each "likes_dict" is a dict, thus we need some more engineering
for likes_dict in likes_home:
    likes_dict_list = list(likes_dict.values())[-2]
    likes_final.append(likes_dict_list)
# now we have integers appended in the list!

# comments final count
comments_home = []
comments_final = []

for c in data['comments'].tolist():
    parsed_c = ast.literal_eval(c)
    comments_home.append(parsed_c[-1])

for comments_dict in comments_home:
    comments_dict_list = list(comments_dict.values())[-2]
    comments_final.append(comments_dict_list)

# shares final count
shares_home = []
shares_final = []

for s in data['shares'].tolist():
    parsed_s = ast.literal_eval(s)
    shares_home.append(parsed_s[-1])

for shares_dict in shares_home:
    shares_dict_list = list(shares_dict.values())[-2]
    shares_final.append(shares_dict_list)

data = data.assign(
    likes_total = likes_final, 
    comments_total = comments_final,
    shares_total = shares_final,
    )

data = data.assign(
    L_tenC_tenS = data['likes_total'] + 10*data['comments_total'] + 10*data['shares_total']
    )

# done data cleaning!

#============term score calculation starts here================

# text splitting using purewords
texts = data['allText'].str.cat()
texts_clean = pw.clean_sentence(texts)
texts_list = texts_clean.split()
word_count = dict(Counter(texts_list)) # using Counter to get term frequency
word_count_sorted = sorted(word_count, key=word_count.get, reverse=True) # it's a list

# create a customized term filter for Poller
# DO NOT MESS WITH purewords/config/stopwords.text. Must create another filter.
filter_word = pd.read_csv('/Users/y/Desktop/poller_experiment/poller_filter.txt', sep=",", header=None, engine='python')
filter_words = filter_word[0].tolist() # is a list

# create another list named word_count_clean
# each item in word_count_clean is unique
word_count_clean = []
for i in word_count_sorted:
    if i in filter_words:
        continue
    else:
        word_count_clean.append(i)

# get the simple term frequency
'''
term_tf_term = []
term_tf_freq = []
for i in word_count_clean:
	if word_count[i] >= 3:
		term_tf_term.append(i)
        term_tf_freq.append(word_count[i])

term_tf_list = list(zip(term_tf_term, term_tf_freq))
# print(term_tf_list)
'''


# create a list of "weighted term frequency(wtf)"
# sort by word_count_sorted
term_wtf_list = []
for t in word_count_clean:
    # certain term's score in certain article
    term_certain_tmp_list = []
    # always reset to zero as we loop through another term
    term_num = 0
    for index, article in data.iterrows():
        article_score = article['L_tenC_tenS']
        if t in article['allText']:
            term_num += article_score
            term_certain_tmp_list.append(term_num)
            term_certain_max = max(term_certain_tmp_list)
    # derive max value and append it to term's list
    term_wtf_list.append(term_certain_max)

# create a clean and sorted list of unique terms(sorted by wtf)
term_sorted_list = [] 
for i in word_count_clean:
    term_sorted_list.append(i)

# 馬英九：25071, 柯文哲：3196, 的：337202

term_wtf_combined = list(zip(term_sorted_list, term_wtf_list))
term_final_list = sorted(term_wtf_combined, key=lambda x: x[1], reverse=True) # 完成！

# export the dataframe as csv!
final_data = pd.DataFrame(term_final_list, columns=['term', 'wtf'])
final_data.to_csv('FB_WTF_0804_NewsDeep.csv', header=True)
term2wtf = final_data.set_index('term')['wtf'].to_dict()
# import ipdb; ipdb.set_trace()

'''
#================article ranking starts here================

term_article_term = []
term_article_wtf = []
term_article_content = []
term_article_score = []
for i, word in final_data.iterrows():
    word = str(final_data['term'][i])
    for index, article in data.iterrows():
        if word in article['allText']:
            term_article_term.append(word)
            term_article_wtf.append(term2wtf[word])
            term_article_content.append(article['allText'])
            term_article_score.append(article['L_tenC_tenS'])

# top 5 article/per term；duplicated articles might exist
topfive = list(zip(term_article_term, term_article_wtf, term_article_content, term_article_score))
topfive_with_duplicate = pd.DataFrame(topfive, columns=['term', 'term_wtf', 'content', 'article_score'])
topfive_with_duplicate_sort = topfive_with_duplicate.sort_values(by=['term_wtf', 'article_score'], ascending=False)
topfive_with_duplicate_sort.index = np.arange(topfive_with_duplicate_sort.shape[0])
topfive_with_duplicate_result = topfive_with_duplicate_sort.groupby('term', sort=False).apply(lambda x: x[(x.index - x.index.min()) < 5])

topfive_with_duplicate_result.to_csv('FB_top5all_0805_Politics.csv')


# top 5 article/per term; drop duplicated articles
topfive_no_duplicate = topfive_with_duplicate.drop_duplicates(subset=['content'], keep='first')
topfive_no_duplicate_sort = topfive_no_duplicate.sort_values(by=['term_wtf', 'article_score'], ascending=False)
topfive_no_duplicate_sort.to_csv('FB_top5clean_0805_Politics.csv')
'''
