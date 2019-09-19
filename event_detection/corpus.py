import datetime
import itertools
import math
import re
from collections import Counter
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple


class Document(object):
    """An abstraction of text with a timestamp."""

    def __init__(self, post_content: str, post_unix_epoch: int):
        self.content = post_content
        self.time = datetime.datetime.fromtimestamp(post_unix_epoch)

    def __repr__(self) -> str:
        return "Document(post_content={}, post_time={})".format(
            self.content, self.time.isoformat()
        )


def tokenize(
    input_str: str, stop_words: List[str], regex_pattern: Optional[str] = None
) -> Set[str]:
    """Split the input string into tokens by space and newline, lower case all
    tokens, remove punctuations in each token, and return a set of tokens."""
    if regex_pattern is None:
        regex_pattern = r"\S*[^\W_]\s*"
    token_pattern = re.compile(regex_pattern)
    tokens = token_pattern.findall(input_str)
    tokens = [x.lower().strip() for x in tokens if x not in stop_words]
    return set(tokens)


def two_combinations(tokens: Set[str]) -> Set[Tuple[str, ...]]:
    """Return a set of ordered 2-combinations of the input tokens.

    'ordered' means for any tuple 't', t[0] < t[1]. The return value is a set,
    so there will not be repetitions.

    >>> two_combinations({'a', 'b', 'c'})
    {('a', 'b'), ('a', 'c'), ('b', 'c')}
    """
    return set(itertools.combinations(sorted(tokens), 2))


def inverse_document_frequency(docs: List[str]) -> Dict[str, float]:
    """A simple Inverse Document Frequency (IDF) implementation."""
    n = len(docs)
    df = Counter()
    for doc in docs:
        df.update(tokenize(doc, []))
    idf = {}
    for word in df.keys():
        idf[word] = math.log10(n / (df[word] + 1))
    return idf


def term_frequency(doc: str) -> Dict[str, float]:
    """A simple Term Frequency (TF) implementation."""
    words = tokenize(doc, [])
    tf = Counter(words)
    tf = {k: v / len(words) for k, v in tf.items()}
    return tf


def get_unimportant_words(docs: List[str], tfidf_thresh: float) -> Set[str]:
    """Get unimportant words from documents by selecting low TF-IDF words."""
    idf = inverse_document_frequency(docs)
    output = set()
    for doc in docs:
        tf = term_frequency(doc)
        for word in tf.keys():
            if tf[word] * idf[word] < tfidf_thresh:
                output.add(word)
    return output
