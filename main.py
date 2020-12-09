import glob
import html
import re
import string

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer

from datetime import datetime
startTime = datetime.now()

files = glob.glob("English/*.txt")


def parse_HTML(t):
    clean = re.compile('<.*?>')
    return html.unescape(" ".join(re.sub(clean, '', t).split())) \
        .replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")


# Returns terms retrieved from text 't'
def all_terms(t):
    # Stop-words removal
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(t)
    filtered_text = [w for w in word_tokens if w not in stop_words]

    # Case folding
    lowerCaseList = list(map(str.lower, filtered_text))

    # Stemming
    ps = PorterStemmer()
    stemmed = [ps.stem(w) for w in lowerCaseList]

    # Removing punctuation and contractions
    noPunctuation = [''.join(c for c in s if c not in string.punctuation + "‘" + "’" + "“" + "”") for s in stemmed]
    noPunctuation = [s for s in noPunctuation if s]
    return [i for i in noPunctuation if
            i != 's'
            and i != 've'
            and i != 're'
            and i != 't'
            and i != 'nt'
            and i != 'd'
            and i != 'll']


def sentence_alias(sentence, arr):
    index = arr.indexOf(sentence)
    return "S" + str(index)


termsDict, sentencesDict, s_lib, doc_lib = {}, {}, {}, {}
# for file in [files[0], files[1]]:
for file in files:
    f = open(file)
    text = f.read()
    f.close()
    text = parse_HTML(text)
    sentences = sent_tokenize(text)

    for sentence in sentences:  # Storing sentences in relation to documents
        if sentence not in sentencesDict:
            sentencesDict[sentence] = [f.name]
        elif f.name not in sentencesDict.get(sentence):
            sentencesDict.get(sentence).append(f.name)
        for term in all_terms(sentence):  # Storing terms in relation to sentences
            if term not in termsDict:
                termsDict[term] = [sentence]
            elif sentence not in termsDict.get(term):
                termsDict.get(term).append(sentence)

print("Total runtime:\t"+str(datetime.now() - startTime))
