import datetime
import json
import toml
import textwrap
import time
import sys
import os
import getopt

from event_detection.core import event_detect


def print_usage() -> str:
    usage = "\nRequire arguments: \n \
            -c config file \n \
            -s stop words file \n \
            -i input corpus \n "
    print(usage)
    exit()


def main():

    optlist, _ = getopt.getopt(sys.argv[1:], "c:s:i:")
    if len(optlist) < 3:
        print_usage()
    for argv in optlist:
        if argv[1] == "":
            print_usage()
        elif not os.path.isfile(argv[1]):
            raise ImportError("Error: file {} doesn't exist".format(argv[1]))

    config = toml.load(optlist[0][1])
    significance_threshold = config["significance_threshold"]
    window_size = config["window_size"]
    similarity_threshold = config["similarity_threshold"]
    box_keepalive_time = datetime.timedelta(hours=config["box_keepalive_time"])

    with open(optlist[1][1]) as f:
        stop_words = [x.strip() for x in f.readlines()]

    # Load input corpus
    with open(optlist[2][1]) as f:
        input_strs = json.load(f)

    def print_fix_width(long_str):
        wrapper = textwrap.TextWrapper(width=79)
        for x in wrapper.wrap(text=long_str):
            print(x)

    t1 = time.time()
    results = event_detect(
        stop_words,
        input_strs,
        window_size=window_size,
        significance_threshold=significance_threshold,
        box_keepalive_time=box_keepalive_time,
        similarity_threshold=similarity_threshold,
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

            ts = {t for b in boxes for t in b.texts}
            for t in ts:
                print_fix_width(t.content)
                print()

            print("-" * 79)
    print("Processed in {} s".format(time.time() - t1))


if __name__ == "__main__":
    main()
