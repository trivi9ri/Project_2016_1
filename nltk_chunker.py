import nltk
from nltk.corpus import conll2000 
import pandas
from collections import Counter

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
    NP: {<DT|PP\$>?<JJ>*<NN>}
        {<NNP>+}
        {<NN>+}"""

NPChunker = ChunkParser(train_sents)


rawtext = open('/home/yung/Python_project/temp.txt').read()
sentences = nltk.sent_tokenize(rawtext)
sentences = [sent.lower() for sent in sentences]
sentences = [sent.decode('utf-8') for sent in sentences]
sentences = [nltk.word_tokenize(sent) for sent in sentences]
sentences = [nltk.pos_tag(sent) for sent in sentences]


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
            np_list.append(np_chunk)

        else:
            for child in t:
                traverse(child, np_list)



np_list = ["list "]

for sent in sentences:
    result = NPChunker.parse(sent)
   
    traverse(result, np_list)

df = pandas.DataFrame(np_list, columns = ['NP Chunk'])

unique_np_chunk = df['NP Chunk'].value_counts()

print unique_np_chunk[:20]
