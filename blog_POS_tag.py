#!/usr/bin/env python
# coding: utf8

import urllib
import nltk
import lxml.html
import codecs
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.tag import pos_tag, map_tag
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter

blog1 = r'/Users/Kevin/FULL TEXT.txt'
with codecs.open(blog1, 'r', 'utf-8-sig') as text_file:
	r = text_file.read()
 #Remove punctuation
tokenizer = RegexpTokenizer(r'\w+')
_tokens = tokenizer.tokenize(r)
 # Get clean tokens
english_stopwords = stopwords.words('english')    # get english stop words
tokens = [t for t in _tokens if t.lower() not in english_stopwords]

 # Process lexical diversity
st = len(set(tokens))
lt = len(tokens)
y = [st*100/lt]
print(y)
fig = plt.figure()
ax = fig.add_subplot(111)
N = 1
 # necessary variables
ind = np.arange(N)
width = 0.7
rect = ax.bar(ind, y, width, color='black') 
 # axes and labels
ax.set_xlim(-width,len(ind)+width)
ax.set_ylim(0,100)
ax.set_ylabel('Score')
ax.set_title('Lexical Diversity')
xTickMarks = ['Lexical Diversity Meter']
ax.set_xticks(ind+width)
xtickNames = ax.set_xticklabels(xTickMarks)
plt.setp(xtickNames, rotation=45, fontsize=10)
 ## add a legend
ax.legend( (rect[0], ('') ))
plt.show()

# get tagged tokens
tagged = nltk.pos_tag(tokens)
 # top words by tag (verb, noun ..etc)
counts = Counter(tag for word,tag in tagged)
 # counter data, counter is your counter object
keys = counts.keys()
y_pos = np.arange(len(keys))
 # get the counts for each key
p = [counts[k] for k in keys]
error = np.random.rand(len(keys))

# need to print p and tag with proper parts of speech

# Top 60 words
dist = nltk.FreqDist(tokens)
dist.plot(60, cumulative=False)

# Common expressions - Collocations. Expressions of multiple words which commonly co-occur
text = nltk.Text(tokens)
collocation = text.collocations(num=60)

bozo_singular = tokens.count("bozo")
bozo_caps = tokens.count("BOZO")
bozo_plural = tokens.count("bozos")
bozo_other = tokens.count("bozoness")

