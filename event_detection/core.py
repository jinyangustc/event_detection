import datetime
import itertools
import json
import textwrap
import time
from collections import defaultdict
from typing import Dict
from typing import List
from typing import Tuple

import click
import toml

from .corpus import Snippet
from .corpus import find_unimportant_words
from .corpus import tokenize
from .corpus import two_combinations

WordPair = Tuple[str, str]


class Box(object):
    def __init__(
        self,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        word_pair: WordPair,
        snippets: List[Snippet],
    ):
        """Create a new box."""
        self.start_time = start_time
        self.end_time = end_time
        self.word_pair = word_pair
        self.snippets = snippets

    def update(self, snippets: List[Snippet], win_end: datetime.datetime):
        """Keep tracking an existing box."""
        self.snippets += snippets
        self.end_time = win_end

    def is_older_than(self, t: datetime.datetime) -> bool:
        return self.end_time <= t

    def __repr__(self) -> str:
        return "Box(word_pair={}, num_snippets={}, start_time={}, end_time={})".format(
            str(self.word_pair), len(self.snippets), self.start_time, self.end_time
        )


class Storyline(object):
    def __init__(self, boxes: Dict[WordPair, Box], similarity_threshold):
        self.boxes = boxes
        self.hierarchy = Storyline.consolidate(boxes, similarity_threshold)

    def __repr__(self) -> str:
        return str(self.hierarchy)

    def get_consolidated_boxes(self) -> List[Tuple[List[WordPair], List[Box]]]:
        forest = Storyline.flatten_forest(self.hierarchy)
        consolidated_boxes = []
        for tree in forest:
            boxes = []
            for word_pair in forest[tree]:
                boxes.append(self.boxes[word_pair])
            consolidated_boxes.append((forest[tree], boxes))
        return consolidated_boxes

    @staticmethod
    def similarity(box_a: Box, box_b: Box) -> float:
        intersect_len = len(
            [snippet for snippet in box_a.snippets if snippet in box_b.snippets]
        )
        union_len = len(box_a.snippets) + len(box_b.snippets)
        return intersect_len / union_len

    @staticmethod
    def consolidate(
        tracking_boxes: Dict[WordPair, Box], similarity_threshold: float
    ) -> Dict[WordPair, WordPair]:
        """Connect similar boxes by Union and Find algorithm. Return a
        dictionary where the key is the word pair of the child box and the
        value is the word pair of the parent box."""
        child_parent_dict = {wp: wp for wp in tracking_boxes}

        for (wp1, wp2) in itertools.combinations(tracking_boxes.keys(), 2):
            if (
                Storyline.similarity(tracking_boxes[wp1], tracking_boxes[wp2])
                >= similarity_threshold
            ):
                parent = child_parent_dict[wp1]
                while parent != child_parent_dict[parent]:
                    parent = child_parent_dict[parent]
                child_parent_dict[wp2] = parent

        return child_parent_dict

    @staticmethod
    def flatten_forest(
        hierarchy: Dict[WordPair, WordPair]
    ) -> Dict[WordPair, List[WordPair]]:
        """Flatten the hierarchy and return a dictionary where the key is the
        word pair of the root box and the value is a list of the word pairs of
        the children boxes."""
        forest = defaultdict(list)
        for child, root in hierarchy.items():
            while root != hierarchy[root]:
                root = hierarchy[root]
            forest[root].append(child)
        return forest


def window(
    snippets: List[Snippet],
    start_time: datetime.datetime,
    window_size: datetime.timedelta,
    step_size: datetime.timedelta = None,
) -> List[Tuple[datetime.datetime, datetime.datetime, List[Snippet]]]:
    if step_size is None:
        step_size = window_size

    if step_size > window_size:
        raise ValueError("step_size is larger than window_size")
    snippets = sorted(snippets, key=lambda x: x.time)
    windows = []
    curr_window = []
    i = 0
    j = -1
    while i < len(snippets):
        if snippets[i].time >= start_time + step_size and j < 0:
            j = i
        if start_time <= snippets[i].time < start_time + window_size:
            curr_window.append(snippets[i])
        elif snippets[i].time >= start_time + window_size:
            windows.append((start_time, start_time + window_size, curr_window))
            curr_window = []
            start_time += step_size
            i = j - 1
            j = -1
        else:
            pass
        i += 1

    if len(curr_window) > 0:
        windows.append((start_time, start_time + window_size, curr_window))
    return windows


def bucketize(
    win: Tuple[datetime.datetime, datetime.datetime, List[Snippet]],
    tracking_boxes: Dict[Tuple[str, str], Box],
    stop_words: List[str],
    significance_threshold: int,
    box_keepalive_time: datetime.timedelta,
    regex_pattern: str,
    min_word_len: int,
) -> Dict[WordPair, Box]:

    win_start, win_end, win = win

    # Collect (potential) boxes in the current window
    boxes = defaultdict(list)
    for snippet in win:
        tokens = tokenize(snippet.content, stop_words, regex_pattern, min_word_len)
        word_pairs = two_combinations(tokens)
        for wp in word_pairs:
            boxes[wp].append(snippet)

    for wp, snippets in boxes.items():
        if wp in tracking_boxes:
            # Update the box is being tracked
            tracking_boxes[wp].update(snippets, win_end)
        else:
            # Create a new box if it is significant
            if len(snippets) >= significance_threshold:
                tracking_boxes[wp] = Box(win_start, win_end, wp, snippets)

    # Stop tracking boxes that have gone unpopular
    cold_pairs = [
        wp
        for wp in tracking_boxes
        if tracking_boxes[wp].is_older_than(win_start + box_keepalive_time)
    ]
    for wp in cold_pairs:
        tracking_boxes.pop(wp)

    return tracking_boxes


def event_detect(
    stop_words: List[str],
    input_strs: List[Dict[str, str]],
    window_size: int,
    significance_threshold: int,
    box_keepalive_time: datetime.timedelta,
    similarity_threshold: float,
    token_regex: str,
    min_word_len: int,
) -> List[
    Tuple[datetime.datetime, datetime.datetime, List[Tuple[List[WordPair], List[Box]]]]
]:
    posts = []
    for post in input_strs:
        posts.append(Snippet(post["content"], int(post["timestamp"])))

    first_time = posts[0].time
    tracking_boxes = {}
    timeline = []
    for win in window(posts, first_time, datetime.timedelta(hours=window_size)):
        tracking_boxes = bucketize(
            win,
            tracking_boxes,
            stop_words,
            significance_threshold,
            box_keepalive_time,
            token_regex,
            min_word_len,
        )
        sl = Storyline(tracking_boxes, similarity_threshold)
        consolidated_boxes = sl.get_consolidated_boxes()
        win_start, win_end, _ = win
        timeline.append((win_start, win_end, consolidated_boxes))
    return timeline


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "-i",
    "--input-file",
    required=True,
    type=click.File(),
    help="Input snippets JSON file.",
)
@click.option(
    "-t",
    "--tfidf-threshold",
    type=float,
    default=0.1,
    show_default=True,
    help=(
        "TF-IDF score threshold. Words with TF-IDF "
        "score lower than this are considered as stop words."
    ),
)
@click.option(
    "-o", "--output-file", type=click.File("w"), help="Save stop words to output file."
)
@click.option("-v", "--verbose", is_flag=True, help="Print TF-IDF scores.")
def stopwords(input_file, tfidf_threshold, output_file, verbose):
    """Generate stopwords based on TF-IDF scores."""
    snippets = json.load(input_file)
    snippets = [x["content"] for x in snippets]
    stop_words = find_unimportant_words(snippets, tfidf_threshold)

    if verbose:
        for k, v in stop_words.items():
            print("{}: {}".format(k, v))
    else:
        for k in stop_words.keys():
            print(k)

    # save output to a file if -o option is provided
    if output_file:
        output_file.writelines("\n".join(sorted(stop_words)) + "\n")


@cli.command()
@click.option(
    "-c",
    "--config",
    required=True,
    type=click.File(),
    help="Configuration file (.toml)",
)
@click.option(
    "-s",
    "--stopwords-file",
    required=True,
    type=click.File(),
    help="Stopwords file (.txt)",
)
@click.option(
    "-i",
    "--input-file",
    required=True,
    type=click.File(),
    help="Input corpus file (.json)",
)
def detect(config, stopwords_file, input_file):
    """Detect events in corpus."""
    config = toml.load(config)
    # tokenization config
    token_regex_pattern = config["tokenization"]["regex_pattern"]
    min_word_length = config["tokenization"]["min_word_length"]

    # detection config
    significance_threshold = config["detection"]["significance_threshold"]
    window_size = config["detection"]["window_size"]
    similarity_threshold = config["detection"]["similarity_threshold"]
    box_keepalive_time = datetime.timedelta(
        hours=config["detection"]["box_keepalive_time"]
    )

    # Load stop word list
    stop_words = [x.strip() for x in stopwords_file.readlines()]

    # Load input corpus
    input_strs = json.load(input_file)

    def print_fix_width(long_str):
        wrapper = textwrap.TextWrapper(width=79)
        for x in wrapper.wrap(text=long_str):
            print(x)

    t1 = time.time()
    print("Initialization completes. Start event detection...")
    results = event_detect(
        stop_words,
        input_strs,
        window_size,
        significance_threshold,
        box_keepalive_time,
        similarity_threshold,
        token_regex_pattern,
        min_word_length,
    )
    for win_start, win_end, box_forest in results:
        print("#" * 79)
        win_header = "window from {} to {}".format(win_start, win_end)
        print(
            "{}{}{}".format(
                " " * int((79 - len(win_header)) / 2),
                win_header,
                " " * int((79 - len(win_header)) / 2),
            )
        )
        print("#" * 79)
        for wps, boxes in box_forest:

            # print word pairs
            print_fix_width(str(wps))
            print()

            ts = {t for b in boxes for t in b.snippets}
            for t in ts:
                print_fix_width(t.content)
                print()

            print("-" * 79)
    print("Processed in {} s".format(time.time() - t1))
    for k, v in config.items():
        print("{}: {}".format(k, v))
