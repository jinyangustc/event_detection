# Apollo Event Detection Package

This is a rewrite of the event detection module in the Apollo Social Sensing toolkit. The code is migrated to Python 3 and
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
## Input format

The input is a list (or stream) of short text snippets, each with its own timestamp. Those snippets can represent text from tweets, tags of instagram images, comments on reddit, headlines from news websites, sentences/subject lines from emails, or some combination of the above. Whatever, the source is, it needs to reformatted as a JSON list of objects (dictionary) with two required keys: "content" and "timestamp", representing the respective snippests and their times. The timestamp is in standard UNIX time format. For example: 

```json
[
  {"content": "hello, world", "timestamp": 1563309777},
  {"content": "this is an example", "timestamp": 1563309777},
  {"content": "ok, you get the idea!", "timestamp": 1563309789},
  ...
]
```

The algorithm chops up the input stream (or file) into windows (by time). In each window, the algorithm finds salient events in the text and outputs all snippets about each separate event into a separate box. We call it event detection. The following key parameters customize the algorithm:

- `min_word_length`: Allow the algorithm to ignore any words less than or equal to this length (default: 3 characters). This allows the detection to ignore words like "is", "are", "he", "she", etc.

- `window_size`: How many hours of input text should the algorithm consider at a time. You need the window to be large enough to contain a significant number of text snippets. However, you do not want it to be too large because event detection works on one window at a time. If the window is, say, one day, you cannot detect events sooner than one day boundaries.

- `significance_threshold`: How many times an event should be mentioned in a window in order to be considered significant. Lower thresholds will create meaningless output (false positives), whereas very high thresholds will cause some important events to be missed (false negatives). This parameter needs to be tuned to your dataset. One suggestion is to set it to something on the lower end, then increment until you are happy with the output.

Additional advanced paramters/settings are mentioned in the algorithm description below if you want to fine-tune performance and you understand the internals of the algorithm. These internals are described next.

## Algorithm

The key insight behind the event detection algorithm is that, when new events occur, new combinations of words end up occurring together (i.e., co-occurring) in the same sentence, headline or tweet (i.e., in the snippets of input text). Those words would typically not co-occur earlier. For example, after a tsunami in Japan, many headlines would have the words "Japan" and "tsunami" together. Similarly, after a protest erupts that is carried out by farmers in some state, the words "farmers" and "protest" would frequently co-occur together in descriptions of that event. The idea of the event detection algorithm is therefore to find frequently occurring new combinations of words that did not co-occur earlier. The algorithm does not interpret the words. It simply counts them to find new frequent co-occurrence patterns. A tunable parameter, called `significance_threshold` decides how many snippets of input need to contain the new word pattern in order for the pattern to be considered significant enough. Since we are dealing with possibly infinite input streams, the above counting is done in one window of input at a time (say every 6 hours). The size of the window is controlled using the parameter, `window_size` (expressed in hours). Hence, for example, if an event is significant if it is mentioned at least 10 times an hour, then  a possible parameterization is to set `window_size` to one hour and `significance_threshold` to 10. Once a frequent pattern is detected (according to set parameters), all text snippets in the input file that contain the pattern are put in a separate box that corresponds to the detected event. 

More specifically, for the input snippets in each time window (the size of the window, in hours, is controlled by `window_size`), the algorithm first tokenizes each snippet into separate words, called 
keywords. Uninteresting keywords, such as "the", "this" etc., are filtered out by a stopword list provided by the
user. Each snippet is then represented by a list of (remaining) keywords pairs. For example, a document with
keywords:
```python
["car", "hits", "dog"]
```
will be represented as:
```python
[("car", "hits"), ("car", "dog"), ("hits", "dog")]
```
Then we count the number of occurrences of each keyword pair in the current time window. Only those keyword pairs that
appear more than the `significance_threshold` are considered popular and are kept.

A popular keyword pair and all the documents in the window that contain those two words are put into a separate "box". For
example, in the text below, such a popular combination is the "dog-drunk" box (with 2 documents in it):
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

If the box already exists from a previous window, we simply update the existing box by adding the new snippets from the
current window. Otherwise we create a new box. If a box has gone "cold" (i.e., hasn't been updated for several time windows controlled by the parameter `box_keepalive_time`) we close it and consider this event finished.

There is one more twist. Sometimes several created boxes end up with very similar content. In this case, they are logically merged. More specifically, the Jaccard similarity between boxes is calculated. Two boxes are logically merged if their similarity is higher than the parameter `similarity_threshold`. We use Union and Find algorithm
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
