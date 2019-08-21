import datetime

from corpus import Text
from typing import List


def window(
    texts: List[Text],
    start_time: datetime.datetime,
    window_size: datetime.timedelta,
    step_size: datetime.timedelta = None,
) -> List[List[Text]]:
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
            windows.append(curr_window)
            curr_window = []
            start_time += step_size
            i = j - 1
            j = -1
        i += 1

    if len(curr_window) > 0:
        windows.append(curr_window)
    return windows


if __name__ == "__main__":
    import json

    # Load input corpus
    with open("../data/example.json") as f:
        input_strs = json.load(f)

    posts = []
    for post in input_strs:
        posts.append(Text(post["content"], post["timestamp"]))

    first_time = posts[0].time
    for win in window(posts, first_time, datetime.timedelta(hours=2)):
        print(len(win))
