import datetime
import itertools
from typing import Tuple
from typing import List
from typing import Dict

from corpus import Text


class Box(object):
    def __init__(
        self,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        word_pair: Tuple[str, str],
        texts: List[Text],
        memory_size: datetime.timedelta = datetime.timedelta(hours=0),
    ):
        """Create a new box."""
        self.start_time = start_time
        self.end_time = end_time
        self.word_pair = word_pair
        self.texts = texts
        self.memory_size = memory_size

    def update(self, texts: List[str], win_end: datetime.datetime):
        """Keep tracking an existing box."""
        self.texts += texts
        self.end_time = win_end

    def is_older_than(self, win_start: datetime.datetime) -> bool:
        return self.end_time + self.memory_size <= win_start

    def __repr__(self) -> str:
        return "Box< name={}, num_texts={}, start={}, end={} >".format(
            str(self.word_pair), len(self.texts), self.start_time, self.end_time
        )


def consolidate(tracking_boxes: Dict, similarity_threshold: float) -> Dict:
    union_and_find = {wp: wp for wp in tracking_boxes}

    for (wp1, wp2) in itertools.combinations(tracking_boxes.keys(), 2):
        if similarity(tracking_boxes[wp1], tracking_boxes[wp2]) >= similarity_threshold:
            parent = union_and_find[wp1]
            while parent != union_and_find[parent]:
                parent = union_and_find[parent]
            union_and_find[wp2] = parent

    return union_and_find


def similarity(box_a: Box, box_b: Box) -> float:
    intersect_len = len([text for text in box_a.texts if text in box_b.texts])
    union_len = len(box_a.texts) + len(box_b.texts)
    return intersect_len / union_len
