# Apollo Event Detection Package

This is a rewrite of the event detection module in Apollo Social Sensing toolkit. The code is migrated to Python 3 and
appropriate abstractions are introduced to improve code reuse.

## Install

### Use the package

```bash
git clone https://github.com/jinyangustc/event_detection.git
cd event_detection

# creat a virtual environment.
python3 -m venv venv

# activate the virtual environment
source venv/bin/activate

# install the package in the virtual environment
pip install .
```

### Develop the package

If you want to modify the code, a development environment can be set up as follows:
```text
git clone https://github.com/jinyangustc/event_detection.git
cd event_detection
python3 -m venv venv
source venv/bin/activate

# install the package in the virtual environment in editable mode
# For more information about installing local packages with `pip`, see `pip help install`
pip install -e .

# install development dependencies, such as pre-commit, pytest and black, etc.
pip install -r requirements.txt

# initialize pre-commit hooks
pre-commit install
```

## Algorithm

The key idea of the detection algorithm is to find spikes of keywords that do not commonly co-occur. An information gain
metric is used to detect such spikes in an unsupervised fashion.

For example, in description of a car accidents, a particular car accident involving a drunk driver who ran over a dog on
a bridge, might be described by tweets containing such keywords as "drunk" and "dog". These words do not commonly
co-occur in the same post. Hence if such an uncommon combination of words spikes today (or in the given time window) in
the context of tweets about car accidents, it is an indication that a new event instance occurred.

For the documents in each time window, the algorithm first tokenize each document to
keywords. Uninteresting keywords, such as "the", "this" and etc., are filtered out by a stopword list provided by the
user. Then each document is represented by a list of 2-combinations of the keywords. For example, a document with
keywords:
```text
["car", "drunk", "dog"]
```
will be represented as:
```text
[("car", "drunk"), ("car", "dog"), ("drunk", "dog")]
```
Then we count the number of occurrences of each keyword pair in the current time window. Only those keyword pairs that
appear more than a threshold called `significance_threshold` are considered popular and will be kept.

A popular keyword pair and all the documents in the window that contain those two words are put into a "box". For
example:
```python
Box(())
```

- `significance_threshold`
- `window_size`
- `similarity_threshold`
- `box_keepalive_time`

## Usage

The core functionality is provided as a library.
```
>>> import toml
>>> import json
>>> import event_detect
>>>
>>> config = toml.load("../data/config.toml")
>>> stop_words = load_stop_words()
>>> input_strs = load_input_strs()
>>>
>>> event_detect.run(config, stop_words, input_strs)
...
```

## FAQ

### Why 2-combinations?
The reason of using 2-combinations is that 2-combinations of words provides a large enough space to de-multiplex
different instances of same type of events. In English, there are about 3000 commonly used words, which is able to cover
95% of common texts. If we use single keywords, the number of events in a time window might exceed the number of words
that we have, which means many events cannot be distinguished from each other. If we use 2-combinations of the words,
then we have 10^6 combinations which should be sufficient to cover most use cases. On the other hand, the computation
time increases as the increase of number of combinations. Therefore, k-combinations where k > 2 might be too slow in
practice. time increases as the increase of number of combinations. Therefore, k-combinations where k > 2 might be too
slow in practice.
