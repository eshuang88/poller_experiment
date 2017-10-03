# poller_experiment
Wordcloud, NLP playground.

## GOAL
- PTT and Facebook are the most popular social media sites in Taiwan, a traditional Chinese speaking country.
- We would like to figure out the trending topics and terms on these sites.
- Here's how it works:
  1. Split the article titles and contents into terms, using jieba, a Chinese word segmentation module.
  	- You can find it here: https://pypi.python.org/pypi/jieba/
  2. Calculate the popularity score, weighted term frequency (WTF), for each term.
  	- For instance, there are three articles, A, B, and C.
  	  - (article, comments) is (A, 120), (B, 250), (C, 60)
  	    - if "柴犬"(Shiba Inu) appears in A, B
  	      - wtf of 柴犬 = 370
  	    - if "哈士奇"(Husky) appears in B, C
  	      - wtf of 哈士奇 = 310
  3. The final output should be a 2-dimensional array of ("term", wtf).


## Datasets
- PTT_dataset.csv
  - Sampled from PTT articles published in September 2017.
  - Size: 10,000 articles
  	- Note that the column of comments is a json-formatted string, {"total_counts": 294}
  	  - We use `ast.literal_eval` method to clean it. Any other suggestions are welcome.

## dict.txt.big.txt
- Terms to be recognized by jieba.


## poller_FB_wtf.txt
- Source code of Poller's wordcloud experiment.
  - **WTF** : Weighted Term Frequency, the index that evaluates the importance of a term.
  - **5foreach** : The 5 most important articles for each term.
    - Note that in the source code there's a module named "Purewords". It's not available. Please use jieba instead.

## poller_FB_wtf.txt
- Source code of Poller's wordcloud experiment.
  - **WTF** : Weighted Term Frequency, the index that evaluates the importance of a term.
  - **5foreach** : The 5 most important articles for each term.

## poller_filter.txt
- Terms to be removed from Poller's wordcloud.
