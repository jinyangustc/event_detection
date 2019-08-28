import datetime
import itertools
from collections import defaultdict
from typing import Tuple
from typing import List
from typing import Dict

from .corpus import Text
from .corpus import tokenize
from .corpus import two_combinations

WordPair = Tuple[str, str]


class Box(object):
    def __init__(
        self,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        word_pair: WordPair,
        texts: List[Text],
    ):
        """Create a new box."""
        self.start_time = start_time
        self.end_time = end_time
        self.word_pair = word_pair
        self.texts = texts

    def update(self, texts: List[Text], win_end: datetime.datetime):
        """Keep tracking an existing box."""
        self.texts += texts
        self.end_time = win_end

    def is_older_than(self, t: datetime.datetime) -> bool:
        return self.end_time <= t

    def __repr__(self) -> str:
        return "Box(word_pair={}, num_texts={}, start_time={}, end_time={})".format(
            str(self.word_pair), len(self.texts), self.start_time, self.end_time
        )


class Storyline(object):
    @staticmethod
    def similarity(box_a: Box, box_b: Box) -> float:
        intersect_len = len([text for text in box_a.texts if text in box_b.texts])
        union_len = len(box_a.texts) + len(box_b.texts)
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


def window(
    texts: List[Text],
    start_time: datetime.datetime,
    window_size: datetime.timedelta,
    step_size: datetime.timedelta = None,
) -> List[Tuple[datetime.datetime, datetime.datetime, List[Text]]]:
    if step_size is None:
        step_size = window_size

    if step_size > window_size:
        raise ValueError("step_size is larger than window_size")
    texts = sorted(texts, key=lambda x: x.time)
    windows = []
    curr_window = []
    i = 0
    j = -1
    while i < len(texts):
        if texts[i].time >= start_time + step_size and j < 0:
            j = i
        if start_time <= texts[i].time < start_time + window_size:
            curr_window.append(texts[i])
        elif texts[i].time >= start_time + window_size:
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
    window: Tuple[datetime.datetime, datetime.datetime, List[Text]],
    tracking_boxes: Dict[Tuple[str, str], Box],
    stop_words: List[str],
    regex_pattern: str,
    significance_threshold: int,
    box_keepalive_time: datetime.timedelta,
) -> Dict[WordPair, Box]:

    win_start, win_end, window = window

    # Collect (potential) boxes in the current window
    boxes = defaultdict(list)
    for text in window:
        tokens = tokenize(text.content, stop_words, regex_pattern)
        word_pairs = two_combinations(tokens)
        for wp in word_pairs:
            boxes[wp].append(text)

    for wp, texts in boxes.items():
        if wp in tracking_boxes:
            # Update the box is being tracked
            tracking_boxes[wp].update(texts, win_end)
        else:
            # Create a new box if it is significant
            if len(texts) >= significance_threshold:
                tracking_boxes[wp] = Box(win_start, win_end, wp, texts)

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
    window_size: int = 2,
    significance_threshold: int = 1,
    box_keepalive_time: int = 0,
    similarity_threshold: float = 0.1,
) -> List[
    Tuple[datetime.datetime, datetime.datetime, List[Tuple[List[WordPair], List[Box]]]]
]:
    posts = []
    for post in input_strs:
        posts.append(Text(post["content"], post["timestamp"]))

    first_time = posts[0].time
    tracking_boxes = {}
    timeline = []
    for win in window(posts, first_time, datetime.timedelta(hours=window_size)):
        tracking_boxes = bucketize(
            win, tracking_boxes, [], None, significance_threshold, box_keepalive_time
        )
        sl = Storyline(tracking_boxes, similarity_threshold)
        consolidated_boxes = sl.get_consolidated_boxes()
        win_start, win_end, _ = win
        timeline.append((win_start, win_end, consolidated_boxes))
    return timeline
