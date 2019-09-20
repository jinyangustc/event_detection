import json

import click
import toml

from event_detection.corpus import get_unimportant_words


@click.command()
@click.argument("tweets_json", type=click.File("r"))
@click.argument("stopwords_file", type=click.Path())
@click.argument("config_file", type=click.Path())
def generate_stopwords(tweets_json, stopwords_file, config_file: str):
    tweets = json.load(tweets_json)
    tweets = [x["content"] for x in tweets]
    config = toml.load(config_file)
    tfidf_threshold = config["stopword_tfidf_thresh"]
    stopwords = get_unimportant_words(tweets, tfidf_threshold)
    with open(stopwords_file, "w") as f:
        f.writelines("\n".join(sorted(stopwords)))


if __name__ == "__main__":
    generate_stopwords()
