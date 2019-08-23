import datetime
import itertools
from collections import defaultdict
from typing import Tuple
from typing import List
from typing import Dict

from corpus import Text

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
