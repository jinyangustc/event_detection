import datetime
from typing import Tuple
from typing import Set
from typing import List
import re
import itertools


class Text(object):
    def __init__(self, post_content: str, post_time: int):
        self.content = post_content
        self.time = datetime.datetime.fromtimestamp(post_time)

    def __repr__(self) -> str:
        return "Text(post_content={}, post_time={})".format(
            self.content, self.time.isoformat()
        )


def tokenize(
    input_str: str, stop_words: List[str], regex_pattern: str = None
) -> Set[str]:
    """Split the input string into tokens by space and newline, lower case all
    tokens, remove punctuations in each token, and return a set of tokens."""
    if regex_pattern is None:
        regex_pattern = r"\S*\w\s*"
    token_pattern = re.compile(regex_pattern)
    tokens = token_pattern.findall(input_str)
    tokens = [x.lower().strip() for x in tokens if x not in stop_words]
    return set(tokens)


def two_combinations(tokens: Set[str]) -> Set[Tuple[str, str]]:
    """Return a set of ordered 2-combinations of the input tokens.

    'ordered' means for any tuple 't', t[0] < t[1]. The return value is a set,
    so there will not be repetitions.

    >>> two_combinations({'a', 'b', 'c'})
    {('a', 'b'), ('a', 'c'), ('b', 'c')}
    """
    return set(itertools.combinations(sorted(tokens), 2))
