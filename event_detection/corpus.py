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
from typing import TypeVar


T = TypeVar("T", int, str)


class Snippet(object):
    """An abstraction of text with a timestamp."""

    def __init__(
        self,
        snippet: Dict[str, T],
        content_key: str = "content",
        timestamp_key: str = "timestamp",
    ):
        self._snippet = snippet
        self._content_key = content_key
        self._timestamp_key = timestamp_key

    @property
    def content(self) -> str:
        return self._snippet[self._content_key]

    @property
    def time(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self._snippet[self._timestamp_key])

    @property
    def raw_dict(self) -> Dict[str, T]:
        return self._snippet

    def __repr__(self) -> str:
        return f"Snippet(content={self.content}, timestamp={self.time.isoformat()})"


def tokenize(
    input_str: str,
    stop_words: List[str],
    regex_pattern: Optional[str] = None,
    min_word_len: int = 0,
) -> Set[str]:
    """Split the input string into tokens by space and newline, lower case all
    tokens, remove punctuations in each token, and return a set of tokens."""
    if regex_pattern is None:
        regex_pattern = r"\S*[^\W_]\s*"
    token_pattern = re.compile(regex_pattern)
    tokens = token_pattern.findall(input_str)
    tokens = [x.lower().strip() for x in tokens]
    tokens = [x for x in tokens if x not in stop_words]
    if min_word_len > 0:
        tokens = [x for x in tokens if len(x) > min_word_len]
    return set(tokens)


def two_combinations(tokens: Set[str]) -> Set[Tuple[str, ...]]:
    """Return a set of ordered 2-combinations of the input tokens.

    'ordered' means for any tuple 't', t[0] < t[1]. The return value is a set,
    so there will not be repetitions.

    >>> two_combinations({'a', 'b', 'c'})
    {('a', 'b'), ('a', 'c'), ('b', 'c')}
    """
    return set(itertools.combinations(sorted(tokens), 2))


def inverse_document_frequency(snippets: List[str]) -> Dict[str, float]:
    """A simple Inverse Document Frequency (IDF) implementation."""
    n = len(snippets)
    df = Counter()
    for snippet in snippets:
        df.update(tokenize(snippet, [], None))
    idf = {}
    for word in df.keys():
        idf[word] = math.log10(n / (df[word] + 1))
    return idf


def term_frequency(snippet: str) -> Dict[str, float]:
    """A simple Term Frequency (TF) implementation."""
    words = tokenize(snippet, [], None)
    tf = Counter(words)
    tf = {k: v / len(words) for k, v in tf.items()}
    return tf


def find_unimportant_words(
    snippets: List[str], tfidf_thresh: float
) -> Dict[str, float]:
    """Get unimportant words from documents by selecting low TF-IDF words."""
    idf = inverse_document_frequency(snippets)
    stopwords = {}
    for snippet in snippets:
        tf = term_frequency(snippet)
        for word in tf.keys():
            if tf[word] * idf[word] < tfidf_thresh:
                stopwords[word] = tf[word] * idf[word]
    return stopwords
