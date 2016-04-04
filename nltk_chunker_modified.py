import nltk
import sys
from nltk.corpus import conll2000 
import pandas
from collections import Counter


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


rawtext = open('/home/yung/download/output_EWSN12.txt').read()
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
        if (counts[i] > 2):
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

                np_list_result.append(unique_np_chunk_patterns[i])
                np_list_result.append(unique_np_chunk_conll2000[j])


df_result = pandas.DataFrame(np_list_result,columns = ['NP Chunk'])
list_unique = []
list_unique = df_result['NP Chunk'].unique()
df_unique = pandas.DataFrame(list_unique, columns = ['NP Chunk'])
output = '/home/yung/Python_project/TEST/EWSN12_COUNTS_LEAST_3.txt'
f = open(output, 'w')

for k in range(len(list_unique)):
    f.write(str(k)+": ")
    f.write(list_unique[k].encode('utf-8'))
    f.write('\n')

f.close()