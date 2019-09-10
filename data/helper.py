import time
import datetime
import json
import math
from collections import defaultdict


def calculate_weights():  # using tf-idf
    with open("2019-07-1517.json", "r") as f:
        tweets = json.load(f)
    tweets = [x["content"] for x in tweets]
    idf = get_idf(tweets)
    tfidf = {}
    for doc in tweets[1:]:
        tf = get_tf(doc)
        for word in set(doc.split()):
            tfidf[word] = tf[word] * idf[word]
        print(sorted(tfidf.items(), key=lambda x: x[1]))
        exit()


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


def translate_to_json():
    with open("input_data.txt", "r") as f:
        inputs = f.readlines()

    output = []
    contents = set()
    for x in inputs:
        obj = {}
        x = eval(x)
        obj["timestamp"] = int(
            time.mktime(
                datetime.datetime.strptime(
                    x["created_at"], "%a %b %d %H:%M:%S +0000 %Y"
                ).timetuple()
            )
        )
        obj["content"] = x["text"][1:].strip("'")
        if obj["content"] not in contents:
            contents.add(obj["content"])
        else:
            continue

        output += [obj]

    with open("input_data.json", "w+") as f:
        json.dump(output, f)


if __name__ == "__main__":
    calculate_weights()
