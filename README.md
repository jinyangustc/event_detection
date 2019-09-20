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
```bash
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

For the documents in each time window (the size of the window is controlled by `window_size`), the algorithm first tokenize each document to
keywords. Uninteresting keywords, such as "the", "this" and etc., are filtered out by a stopword list provided by the
user. Then each document is represented by a list of 2-combinations of the keywords. For example, a document with
keywords:
```python
["car", "drunk", "dog"]
```
will be represented as:
```python
[("car", "drunk"), ("car", "dog"), ("drunk", "dog")]
```
Then we count the number of occurrences of each keyword pair in the current time window. Only those keyword pairs that
appear more than a threshold called `significance_threshold` are considered popular and will be kept.

A popular keyword pair and all the documents in the window that contain those two words are put into a "box". For
example, the "dog-drunk" box with 2 documents in it:
```text
>>> from event_detection.core import Box
>>> from event_detection.corpus import Document
>>> import datetime
>>> st = datetime.datetime(2019, 9, 1)
>>> et = datetime.datetime(2019, 9, 2)
>>> doc1 = Document("A drunk driver run over a dog in a car accident", 1568938357)
>>> doc2 = Document("A dog was killed by a drunk driver in a car accident", 1568938380)
>>> b = Box(st, et, ('dog', 'drunk'), [doc1, doc2])
>>> b
Box(word_pair=('dog', 'drunk'), num_docs=2, start_time=2019-09-01 00:00:00, end_time=2019-09-02 00:00:00)
```

If a popular keyword pair has appeared in one of the boxes we have been tracking, i.e., we have been tracking the event
represented by this keyword pair, we update the existing box by adding the documents containing the two words in the
current window.

If a keyword pair is popular in the current window and hasn't been tracking, we create a new box with all the documents
containing the two words in the current window.

If a box has gone "cold", i.e., hasn't been updated for a while (the length is controlled by `box_keepalive_time`, we
stop tracking it.

Once the boxes have been created or updated, the Jaccard similarity between boxes are calculated. Two boxes are
connected if their similarity is higher than the parameter `similarity_threshold`. Then we use Union and Find algorithm
to merge similar boxes. This process is called consolidation. Consolidation is necessary because different keyword pairs
may refer to the same event instance.

## Usage

The core functionality is provided as a library.
```text
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
