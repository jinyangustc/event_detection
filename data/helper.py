import time
import datetime

import json


def translate_to_json():
    with open("input_data.txt", "r") as f:
        inputs = f.readlines()

    output = []
    contents = set()
    for x in inputs:
        obj = {}
        x = eval(x)
        obj["timestamp"] = int(
            time.mktime(
                datetime.datetime.strptime(
                    x["created_at"], "%a %b %d %H:%M:%S +0000 %Y"
                ).timetuple()
            )
        )
        obj["content"] = x["text"][1:].strip("'")
        if obj["content"] not in contents:
            contents.add(obj["content"])
        else:
            continue

        output += [obj]

    with open("input_data.json", "w+") as f:
        json.dump(output, f)
