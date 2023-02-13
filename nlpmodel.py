from sentence_transformers import SentenceTransformer, util

from fpl_api import playercomparison
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

from nltk import pos_tag
from nltk import RegexpParser
text ="aa".split()


tokens_tag = pos_tag(text)
print(tokens_tag)

count = 0
names = []
for i in tokens_tag:
    if i[1] == 'NNP':
        names.append(i[0])
        count = count + 1

if count == 2:
    playercomparison(names[0], names[1])
elif count == 1:
    print('Get data')
else:
    sentences1 = ['Highest goal scorer']

    sentences2 = ['Who scored most goals?',
                  'Which forward player to buy in next gameweek?',
                  'Which defender player to buy in next gameweek?',
                  ]

    embeddings1 = model.encode(sentences1, convert_to_tensor=True)
    embeddings2 = model.encode(sentences2, convert_to_tensor=True)

    cosine_scores = util.cos_sim(embeddings1, embeddings2)

    if cosine_scores[0][0] > 0:
        print('Hi')
    #print(cosine_scores[0][1])
    print(cosine_scores[0])
    #print('Highest element: ' + str(np.argmax(cosine_scores[0])))
    x = np.argmax(cosine_scores[0])
    if x == 0:
        print('0')


