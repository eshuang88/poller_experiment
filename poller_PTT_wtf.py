# encoding: utf-8
import sys
from collections import defaultdict

import pandas as pd
import json

import jieba

from tqdm import tqdm
from joblib import Parallel, delayed


class TrieNode(object):
    '''Trie - https://en.wikipedia.org/wiki/Trie'''

    def __init__(self):
        self.final = False
        self.children = {}

    def __contains__(self, letters, index=0):
        if index < 0 and len(letters) < index:
            return False
        if len(letters) == index:
            return self.final
        elif letters[index] in self.children:
            return self.children[letters[index]].__contains__(
                letters,
                index + 1
            )
        else:
            return False

    def add(self, letters, index=0):
        if index < 0 and len(letters) < index:
            return
        if len(letters) == index:
            self.final = True
        else:
            if letters[index] not in self.children:
                self.children[letters[index]] = TrieNode()
            self.children[letters[index]].add(
                letters,
                index + 1
            )


# ============data cleaning starts here================

data = pd.read_csv('PTT_dataset.csv')

# merge column "title" and column "body" as a string
# create a column named "allText"
data = data.assign(
    allText=(data['title'].astype(str) + data['body'].astype(str))
)

# compute article popularity as total comments
# each 'comments' is a dict, thus we need use json
data = data.assign(
    totalComments=data['comments'].apply(
        lambda x: json.loads(x)['total_count']),
)

# ============data cleaning ends here================

# ============term score calculation starts here================

# create a customized term filter for Poller
# DO NOT MESS WITH purewords/config/stopwords.text. Must create another filter.


word_filter = TrieNode()

with open('poller_filter.txt') as f:
    # word_filter = f.read().splitlines()
    for eword in f.read().splitlines():
        word_filter.add(eword)

# create a baba of "weighted term frequency(wtf)"
# prolly looks like this: ('柯文哲': 2819730), ('馬英九': 467383)
# sort by word_count_sorted


def clean_text(allText):
    return set(e for e in jieba.lcut(allText) if e not in word_filter)


print("Starting parallel jobs..")

try:
    cleaned_text = Parallel(n_jobs=-1)(
        delayed(clean_text)
        (erow['allText']) for i, erow in tqdm(data.iterrows())
    )
except KeyboardInterrupt:
    print("\n\nExiting..")
    sys.exit(1)

wtf_data = defaultdict(int)

for i, erow in tqdm(data.iterrows()):
    for eword in cleaned_text[i]:
        wtf_data[eword] += erow['totalComments']


term_final_list = list(wtf_data.items())
term_final_list.sort(key=lambda x: (x[1], x[0]), reverse=True)

# ============term score calculation ends here================

# export the dataframe as csv!
final_data = pd.DataFrame(term_final_list, columns=['PTT_term', 'PTT_wtf'])
final_data.to_csv('PTT_WTF_numpytry_gossiping.csv', header=True, index=False)
