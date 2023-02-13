from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize

st = StanfordNERTagger('/Users/sumit/Downloads/stanford-ner-2020-11-17/classifiers/english.all.3class.distsim.crf.ser.gz',
					   '/Users/sumit/Downloads/stanford-ner-2020-11-17/stanford-ner.jar',
					   encoding='utf-8')

text = 'MUN vs MCI'

tokenized_text = word_tokenize(text)
classified_text = st.tag(tokenized_text)

print(classified_text)