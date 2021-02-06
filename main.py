import glob
import html
import re
import string
import numpy as np
import pandas as pd

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer

from datetime import datetime
startTime = datetime.now()

files = glob.glob("English/*.txt")


def parse_HTML(text):
    clean = re.compile('<.*?>')
    return html.unescape(" ".join(re.sub(clean, '', text).split())) \
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
    global ps
    stemmed = [ps.stem(w) for w in lowerCaseList]

    # Removing punctuation and contractions
    noPunctuation = [''.join(c for c in s if c not in string.punctuation + "‘" + "’" + "“" + "”") for s in stemmed]
    noPunctuation = [s for s in noPunctuation if s]
    return [i for i in noPunctuation if i not in ('ve', 're', 't', 'nt', 'd', 'll')]


files = glob.glob("English/*.txt")
pList, allSentences, allDocuments, dCounter, angerWords = {}, {}, {}, 0, {}
trustTerms = ["loyalty", "reliance", "fraud", "forgery", "trust", "confidence", "covenant", "pledge",
              "promise", "warn", "alert", "flatter", "compliment", "periphrasis", "lie"]
# Getting the anger words from the wne file
with open('anger.wne') as f:
    ps = PorterStemmer()
    angerWords = set(word_tokenize(f.read()))
    trustTerms_stemmed = [ps.stem(word) for word in trustTerms]
    reversed_stemming_trust = dict(zip(trustTerms_stemmed, trustTerms))
angerWords = np.unique([ps.stem(w) for w in angerWords])

# Creating the postings list

startTime = datetime.now()
# for file in [files[0], files[1], files[2], files[3], files[4]]:
for file in files:
    dCounter += 1
    f = open(file)
    allDocuments["D{}".format(dCounter)] = f.name
    text = f.read()
    f.close()
    text = parse_HTML(text)
    sentences = sent_tokenize(text)

    sCounter = 0
    for sentence in sentences:  # Storing sentences in relation to documents
        sCounter += 1
        allSentences["D{}S{}".format(dCounter, sCounter)] = sentence
        for term in all_terms(sentence):  # Creating postings list
            if term not in pList:
                pList[term] = ["D{}S{}".format(dCounter, sCounter)]
            else:
                pList.get(term).append("D{}S{}".format(dCounter, sCounter))


document_count = dict((i, 0) for i in allDocuments)
trust_terms_intersection = list(pList.keys() & trustTerms_stemmed)
trust_terms_locations = [pList.get(word) for word in trust_terms_intersection]
trust_terms = dict(zip(trust_terms_intersection, trust_terms_locations))
anger_word_intersection = pList.keys() & angerWords
anger_word_locations = [pList.get(word) for word in anger_word_intersection]
anger_words = dict(zip(anger_word_intersection, anger_word_locations))

cooccurrence_result = dict((i, 0) for i in trust_terms)
for trust_term in trust_terms:
    t_counter = 0
    for t_loc in trust_terms[trust_term]:
        for anger_word in anger_words:
            for a_loc in anger_words[anger_word]:
                if t_loc == a_loc:
                    t_counter += 1
                    document_count[a_loc.partition("S")[0]] += 1
    cooccurrence_result[trust_term] = t_counter

print("Total runtime:\t\t\t\t"+str(datetime.now() - startTime))

df = pd.DataFrame(document_count.items(), columns=["Document", "Trust-Anger co-ocurrence count"])
for _, doc in df.iterrows():
    df = df.replace(doc["Document"], allDocuments[doc["Document"]].replace('English\\ ', ''))
df = df.sort_values(by=['Trust-Anger co-ocurrence count'], ascending=False)

# df_anger_word = dict((i, []) for i in anger_word_intersection)
# file_anger_counts = dict((i, dict((j, 0) for j in anger_word_intersection)) for i in allDocuments)
# for anger_word in anger_word_intersection:
#     docAppearances = []
#     for location in pList[anger_word]:
#         key = location.partition("S")[0]
#         docAppearances.append(key)
#         file_anger_counts[key][anger_word] += 1
#     df_anger_word[anger_word] = len(np.unique(docAppearances))
#
# idf = dict((i, 0) for i in df_anger_word)
# for term in idf:
#     # idf[term] = 5/df_anger_word[term]
#     idf[term] = len(files) / df_anger_word[term]
#
# tf_idf_scores = dict((doc, dict((term, 0) for term in file_anger_counts[doc])) for doc in file_anger_counts)
# for document in file_anger_counts:
#     for word in file_anger_counts[document]:
#         if file_anger_counts[document][word] != 0:
#             tf_idf_scores[document][word] = idf[word] * (1 + np.log10(file_anger_counts[document][word]))
#
# doc_with_max_score, most_important_anger_term, maxScore = 0, "", 0
# for document in tf_idf_scores:
#     for word in tf_idf_scores[document]:
#         if maxScore < tf_idf_scores[document][word]:
#             maxScore = tf_idf_scores[document][word]
#             doc_with_max_score = document
#             most_important_anger_term = word
#
# print("'Angriest' document:\t\t{}\nMost important anger term:\t{}\ntf-idf score of term:\t\t{}"
#       .format(allDocuments[doc_with_max_score], most_important_anger_term, maxScore))
