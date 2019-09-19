import json

import click

from event_detection.corpus import get_unimportant_words


@click.command()
@click.argument("tweets_json", type=click.File("r"))
@click.argument("stopwords_file", type=click.Path())
@click.argument("tfidf_threshold", type=float)
def generate_stopwords(tweets_json, stopwords_file, tfidf_threshold):
    tweets = json.load(tweets_json)
    tweets = [x["content"] for x in tweets]
    stopwords = get_unimportant_words(tweets, tfidf_threshold)
    with open(stopwords_file, "w") as f:
        f.writelines("\n".join(sorted(stopwords)))


if __name__ == "__main__":
    # python generate_stopwords ../data/2019-07-1517.json stopwords.txt 0.05
    generate_stopwords()
