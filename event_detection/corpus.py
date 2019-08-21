import datetime
from typing import Tuple
from typing import Set
import itertools


class Text(object):
    def __init__(self, post_content: str, post_time: int):
        self.content = post_content
        self.time = datetime.datetime.fromtimestamp(post_time)

    def __repr__(self) -> str:
        return "Text(content={}, time={})".format(self.content, self.time.isoformat())


def tokenize(input_str: str) -> Set[str]:
    """Split the input string into tokens by space and newline, lower case all
    tokens, remove punctuations in each token, and return a set of tokens."""
    raise NotImplementedError


def two_combinations(tokens: Set[str]) -> Set[Tuple[str, str]]:
    """Return a set of ordered 2-combinations of the input tokens.

    'ordered' means for any tuple 't', t[0] < t[1]. The return value is a set,
    so there will not be repetitions.

    >>> two_combinations({'a', 'b', 'c'})
    {('a', 'b'), ('a', 'c'), ('b', 'c')}
    """
    return set(itertools.combinations(tokens, 2))
