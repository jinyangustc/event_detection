import datetime
from typing import List
from typing import Tuple
from typing import Dict
from collections import defaultdict

from box import Box
from box import Storyline
from corpus import Text
from corpus import tokenize
from corpus import two_combinations


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


def event_detect(
    window: Tuple[datetime.datetime, datetime.datetime, List[Text]],
    tracking_boxes: Dict[Tuple[str, str], Box],
    stop_words: List[str],
    regex_pattern: str,
    significance_threshold: int,
    box_keepalive_time: datetime.timedelta,
) -> Dict:

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


def run(
    config: Dict[str, str], stop_words: List[str], input_strs: List[Dict[str, str]]
):
    posts = []
    for post in input_strs:
        posts.append(Text(post["content"], post["timestamp"]))

    first_time = posts[0].time
    tracking_boxes = {}
    timeline = []
    for win in window(posts, first_time, datetime.timedelta(hours=window_size)):
        tracking_boxes = event_detect(
            win, tracking_boxes, [], None, significance_threshold, box_keepalive_time
        )
        sl = Storyline(tracking_boxes, similarity_threshold)
        consolidated_boxes = sl.get_consolidated_boxes()
        win_start, win_end, _ = win
        timeline.append((win_start, win_end, consolidated_boxes))
    return timeline


if __name__ == "__main__":
    import json
    import toml
    import textwrap

    config = toml.load("../data/config.toml")
    significance_threshold = config["significance_threshold"]
    window_size = config["window_size"]
    similarity_threshold = config["similarity_threshold"]
    box_keepalive_time = datetime.timedelta(hours=config["box_keepalive_time"])

    with open("../data/stopwords.txt") as f:
        stop_words = [x.strip() for x in f.readlines()]

    # Load input corpus
    with open("../data/example.json") as f:
        input_strs = json.load(f)

    def print_fix_width(long_str):
        wrapper = textwrap.TextWrapper(width=79)
        for x in wrapper.wrap(text=long_str):
            print(x)

    results = run(config, stop_words, input_strs)
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

            ts = {t for b in boxes for t in b.texts}
            for t in ts:
                print_fix_width(t.content)
                print()

            print("-" * 79)
