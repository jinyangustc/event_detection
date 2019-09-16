import json
import math
from collections import defaultdict


def generate_stopwords(filename_input, filename_stopwords, threshold):
    stopwords = calculate_stopwords(filename_input, threshold)
    s = ""
    for word in stopwords:
        s += word + "\n"
    with open(filename_stopwords, "w+") as f:
        f.write(s)


def calculate_stopwords(filename_input, threshold):  # use tf-idf
    with open(filename_input, "r") as f:
        tweets = json.load(f)
    tweets = [x["content"] for x in tweets]
    idf = get_idf(tweets)
    output = set()
    for doc in tweets[1:]:
        tf = get_tf(doc)
        for word in set(doc.split()):
            tfidf = tf[word] * idf[word]
            if tfidf < threshold:
                output.add(word)
    return output


def get_idf(tweets):
    n = len(tweets)
    df = defaultdict(int)
    for doc in tweets:
        for word in set(doc.split()):
            df[word] += 1
    idf = {}
    for word in df.keys():
        idf[word] = math.log10(n / (df[word] + 1))
    return idf


def get_tf(doc):
    tf = {}
    n = len(doc)
    count = defaultdict(int)
    for word in doc.split():
        count[word] += 1
    for word in count.keys():
        tf[word] = count[word] / n
    return tf


if __name__ == "__main__":
    generate_stopwords("2019-07-1517.json", "stopwords.txt", 0.01)
