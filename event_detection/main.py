import datetime
from typing import Iterator

from corpus import Text
from typing import List


def window(
    texts: List[Text], start_time: datetime.datetime, window_size: datetime.timedelta
) -> Iterator[List[Text]]:
    if len(texts) == 0:
        return []

    # Sort input texts by time
    texts = sorted(texts, key=lambda x: x.time)

    end_time = texts[-1].time
    win_end_time = start_time + window_size
    win_start_idx = 0
    while texts[win_start_idx].time < end_time:

        # Find the last element within the window
        win_end_idx = win_start_idx
        while texts[win_end_idx].time < win_end_time:
            win_end_idx += 1

        # Yield the window
        yield texts[win_start_idx:win_end_idx]

        # Advance window start
        win_start_idx = win_end_idx


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
        print(win)
