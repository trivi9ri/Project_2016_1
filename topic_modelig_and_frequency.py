import nltk
import sys
from nltk.corpus import conll2000 
import pandas
from collections import Counter
import operator
import itertools
import numpy as np
import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn import decomposition
import time


reload(sys)
sys.setdefaultencoding('utf-8')
test_sents = conll2000.chunked_sents('test.txt', chunk_types=['NP']) 
train_sents = conll2000.chunked_sents('train.txt', chunk_types=['NP'])

class ChunkParser(nltk.ChunkParserI): 
    def __init__(self, train_sents): 
        train_data = [[(t,c) for w,t,c in nltk.chunk.tree2conlltags(sent)] for sent in train_sents] 
        self.tagger = nltk.TrigramTagger(train_data) 

    def parse(self, sentence): 
        pos_tags = [pos for (word,pos) in sentence] 
        tagged_pos_tags = self.tagger.tag(pos_tags) 
        chunktags = [chunktag for (pos, chunktag) in tagged_pos_tags] 
        conlltags = [(word, pos, chunktag) for ((word,pos),chunktag) in zip(sentence, chunktags)] 
        return nltk.chunk.conlltags2tree(conlltags)
        
patterns = """
    NP:  {<JJ>*<NN>}
        {<NN>+}
        {<DT|PP\$>?<JJ>*<NN>}
        
        """

NPChunker_conll2000 = ChunkParser(train_sents)
NPChunker_patterns = nltk.RegexpParser(patterns)

directory = '/home/yung/download/'

filename =  'output_EWSN12.txt'

file_dir = directory + filename


rawtext = open(file_dir).read()
sentences = nltk.sent_tokenize(rawtext)
sentences = [sent.lower() for sent in sentences]
sentences = [sent.decode('utf-8') for sent in sentences]
sentences = [nltk.word_tokenize(sent) for sent in sentences]
sentences = [nltk.pos_tag(sent) for sent in sentences]

except_list = ['you ','that ','i ','what ','this ','it ','a ','we ','he ','she ','that ','there ',
                'where ','which ','such ','many ','much ']


def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def traverse(t, np_list):
    try:
        t.label()
    except AttributeError:
        return
    else:
        if t.label() == 'NP': 
            temp = nltk.chunk.tree2conlltags(t)
            np_chunk = ''
            for a in range(len(temp)):
                np_chunk += temp[a][0] +' '
                
            if (np_chunk not in except_list) & (len(np_chunk) > 3) & (isNumber(np_chunk[:-1]) == False):
                np_list.append(np_chunk)

        else:
            for child in t:
                traverse(child, np_list)

np_list_conll2000 = []
np_list_patterns = []
np_list_result = []

for sent in sentences:
    result_conll2000 = NPChunker_conll2000.parse(sent)
    result_patterns = NPChunker_patterns.parse(sent)
    traverse(result_conll2000, np_list_conll2000)
    traverse(result_patterns, np_list_patterns)


df_conll2000 = pandas.DataFrame(np_list_conll2000, columns = ['NP Chunk'])
df_patterns = pandas.DataFrame(np_list_patterns, columns = ['NP Chunk'])


unique_np_chunk_conll2000 = df_conll2000['NP Chunk'].value_counts().keys()
unique_np_chunk_patterns = df_patterns['NP Chunk'].value_counts().keys()

#print unique_np_chunk_conll2000[:50]
#print unique_np_chunk_patterns[:50]
counts_conll2000 = df_conll2000['NP Chunk'].value_counts()
counts_patterns = df_patterns['NP Chunk'].value_counts()

def frequcncy(counts):
    frequcncy = 0
    for i in range(len(counts)):
        if (counts[i] > 1):
            frequcncy += 1
    return frequcncy

frequcncy_c = frequcncy(counts_conll2000)
frequcncy_p = frequcncy(counts_patterns)

print frequcncy_c, frequcncy_p

max_counts = 50
for i in range(frequcncy_c ):
    for j in range(frequcncy_p):
        if ((unique_np_chunk_patterns[i] in unique_np_chunk_conll2000[j])|
            (unique_np_chunk_conll2000[j] in unique_np_chunk_patterns[i])|
           (unique_np_chunk_patterns[i] == unique_np_chunk_conll2000[j])):

                np_list_result.append(unique_np_chunk_patterns[i].encode("utf-8"))
                np_list_result.append(unique_np_chunk_conll2000[j].encode("utf-8"))


df_result = pandas.DataFrame(np_list_result,columns = ['NP Chunk'])
list_unique = []
list_unique = df_result['NP Chunk'].unique()

df_unique = pandas.DataFrame(list_unique, columns = ['NP Chunk'])




filenames = file_dir
os_input1 = '/home/yung/mallet-2.0.7/bin/mallet import-file --input /home/yung/download/'
os_input2 = ' --output /home/yung/Python_project/topic-input-report.mallet --keep-sequence --remove-stopwords'
os_input = os_input1+filename+os_input2
os.system(os_input)
os.system('/home/yung/mallet-2.0.7/bin/mallet train-topics --input /home/yung/Python_project/topic-input-report.mallet --num-topics 15 --output-doc-topics /home/yung/Python_project/doc-topics-report.txt --output-topic-keys /home/yung/Python_project/topic-keys-report.txt --random-seed 1')


def grouper(n, iterable, fillvalue = None):
        "Collect data into fixed-length chunks or blocks"
        args = [iter(iterable)] * n
        return itertools.izip_longest(*args, fillvalue = fillvalue)

doctopic_triples = []

mallet_docnames = []

values = []

with open("/home/yung/Python_project/doc-topics-report.txt") as f:
    f.readline()
    for line in f:
        docnum, docname= line.rstrip().split('\t')[:2] #\t can change thing you want
        mallet_docnames.append(docname)
        values = ( line.rstrip().split('\t')[2:])
        

        for topic, share in grouper(2, values):
            triple = (docname, int(topic), float(share))
            doctopic_triples.append(triple)



doctopic_triples = sorted(doctopic_triples, key = operator.itemgetter(0,1))

mallet_docnames = sorted(mallet_docnames)

num_docs = len(mallet_docnames)

num_topics = len(doctopic_triples)

doctopic = np.zeros((num_docs, num_topics))

for triple in doctopic_triples:
    docname, topic, share = triple
    row_num = mallet_docnames.index(docname)
    doctopic[row_num, topic] = share


novel_names = []

for fn in filenames:
    basename = os.path.basename(fn)
    name, ext = os.path.splitext(basename)
    name = name.rstrip('0123456789')
    novel_names.append(name)


novel_names = np.asarray(novel_names)

doctopic_orig = doctopic.copy()

num_groups = len(set(novel_names))

doctopic_grouped = np.zeros((num_groups, num_topics))



doctopic = doctopic_grouped


vectorizer = CountVectorizer(input = 'filename')

# dtm = vectorizer.fit_transform(filenames)

# dtm.shape

# dtm.data.nbytes

# #dtm.toarray().data.nbytes

doctopic_orig.shape

#doctopic_orig.data.nbytes

novels = sorted(set(novel_names))

print("Top topics in ..")

for i in range(len(doctopic)):
    top_topics = np.argsort(doctopic[i, :])[::-1][0:3]
    top_topics_str = ' '.join(str(t) for t in top_topics)
    print("{}: {}".format(novels[i], top_topics_str))


with open('/home/yung/Python_project/topic-keys-report.txt') as input:
    topic_keys_lines = input.readlines()

topic_words = []


for line in topic_keys_lines:
    _,_, words = line.split('\t')
    words = words.rstrip().split(' ')
    topic_words.append(words)


N_WORDS_DISPLAY = 8

topic_words_array = []

for t in range(len(topic_words)):
    print("Topic {}: {}".format(t, ' '.join(topic_words[t][:N_WORDS_DISPLAY])))
    for h in range(10):
        topic_words_array.append(topic_words[t][h])



report_indices = []

for index, fn in enumerate(sorted(set(novel_names))):
    report_indices.append(index)


report_avg = np.mean(doctopic[report_indices, :], axis = 0)

keyness = np.abs(report_avg)

ranking = np.argsort(keyness)[::-1]


for x in range(len(list_unique)):
    list_unique[x] = list_unique[x][:-1]

keywords_list = []

for a in range(len(list_unique)):
    for b in range(len(topic_words_array)):
          if (list_unique[a] == topic_words_array[b]):
                keywords_list.append(list_unique[a])
          elif ((list_unique[a] in topic_words_array[b])|(topic_words_array[b] in list_unique[a])):
                keywords_list.append(list_unique[a])
                keywords_list.append(topic_words_array[b])

df_final = pandas.DataFrame(keywords_list,columns = ['NP Chunk'])
unique_keyword = []
unique_keyword = df_final['NP Chunk'].unique()
list_unique_keyword = unique_keyword.tolist()
for z in list_unique_keyword:
    if len(z) < 3:
        list_unique_keyword.remove(z)
keywords = pandas.DataFrame(list_unique_keyword, columns = ['NP Chunk'])
keywords["FileName"] = filename
keywords.to_csv('EWSN12.csv', sep = ',', encoding = 'utf-8')

output = 'result_'+filename

f = open(output, 'w')

for c in range(len(unique_keyword)):
    f.write(str(c)+": ")
    f.write(unique_keyword[c].encode('utf-8'))
    f.write('\n')

f.close()