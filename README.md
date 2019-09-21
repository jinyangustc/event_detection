# Apollo Event Detection Package

This is a rewrite of the event detection module in the Apollo Social Sensing toolkit. The code is migrated to Python 3 and appropriate abstractions are introduced to improve code reuse.

## Install

Get a copy of the code through git-clone.
```text
git clone https://github.com/jinyangustc/event_detection.git
```
Or you can simply download a zip file and unzip it.

Then go to directory.
```text
cd /the/path/to/event_detection/
```

### Use the package

In the directory of this project:
```bash
# creat a virtual environment.
python3 -m venv venv

# activate the virtual environment
source venv/bin/activate

# install the package in the virtual environment
pip install .
```

### Set up a develop environment

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
  {"content": "ok, you get the idea!", "timestamp": 1563309789}
]
```

The algorithm chops up the input stream (or file) into windows (by time). In each window, the algorithm finds salient events in the text and outputs all snippets about each separate event into a separate box. We call it event detection. The following key parameters customize the algorithm:

- `min_word_length`: Allow the algorithm to ignore any words less than or equal to this length (default: 3 characters). This allows the detection to ignore words like "is", "are", "he", "she", etc.

- `window_size`: How many hours of input text should the algorithm consider at a time. You need the window to be large enough to contain a significant number of text snippets. However, you do not want it to be too large because event detection works on one window at a time. If the window is, say, one day, you cannot detect events sooner than one day boundaries.

- `significance_threshold`: How many times an event should be mentioned in a window in order to be considered significant. Lower thresholds will create meaningless output (false positives), whereas very high thresholds will cause some important events to be missed (false negatives). This parameter needs to be tuned to your dataset. One suggestion is to set it to something on the lower end, then increment until you are happy with the output.

Additional advanced paramters/settings are mentioned in the algorithm description below if you want to fine-tune performance and you understand the internals of the algorithm. These internals are described next.

## Usage

Once installed, this package provides a command line tool called `apollo` which has two sub-commands:
```text
(venv) ~/git/event_detection $ apollo --help
Usage: apollo [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  detect     Detect events in corpus.
  stopwords  Generate stopwords based on TF-IDF scores.
```

This package comes with a [sample JSON file](data/sample.json) in `data/` folder. The rest of this section will use this file as an example.

### Generate stop words

The `stopwords` sub-command generates stop word list with a input file (in the format described in [Input format](#Input-format) section).
```text
(venv) ~/git/event_detection $ apollo stopwords --help
Usage: apollo stopwords [OPTIONS]

  Generate stopwords based on TF-IDF scores.

Options:
  -i, --input-file FILENAME    Input snippets JSON file.  [required]
  -t, --tfidf-threshold FLOAT  TF-IDF score threshold. Words with TF-IDF score
                               lower than this are considered as stop words.
                               [default: 0.1]
  -o, --output-file FILENAME   Save stop words to output file.
  -v, --verbose                Print TF-IDF scores.
  --help                       Show this message and exit.
```

The following command will use `data/sample.json` file and TF-IDF threshold `0.11` to generate a stop word file `data/stopwords.txt`. The `-v` switch turns on the verbose mode which prints the TF-IDF scores to the STDOUT.
```text
(venv) ~/git/event_detection $ apollo stopwords -v -t 0.11 -i data/sample.json -o data/stopwords.txt
rt: 0.06357815854140902
ago: 0.07733288849736422
e: 0.10515616143379646
km: 0.07951493227053164
strikes: 0.07816974568972883
of: 0.026368349196490153
#earthquake: 0.06407877088292269
info: 0.08938875818079496
more: 0.0813800611445794
[the rest of the output is omitted]
```

The stop word file should only contain one word per line:
```text
(venv) ~/git/event_detection $ tail data/stopwords.txt
yes
yesterday
yet
yo
york
you
you're
your
y’all
zone
```

### Detect events

The `detect` sub-command runs the event detection algorithm described in [the algorithm section](#Algorithm).
```text
(venv) ~/git/event_detection $ apollo detect --help
Usage: apollo detect [OPTIONS]

  Detect events in corpus.

Options:
  -c, --config FILENAME          Configuration file (.toml)  [required]
  -s, --stopwords-file FILENAME  Stopwords file (.txt)  [required]
  -i, --input-file FILENAME      Input corpus file (.json)  [required]
  --help                         Show this message and exit.
```
The parameters to configure the algorithm is stored in a TOML file. There is [an example configuration](data/config.toml) in `data/` folder. We run the detection algorithm on the `data/sample.json` with the example configuration and the stop word file `data/stopwords.txt` generated in previous step:
```text
(venv) ~/git/event_detection $ apollo detect -c data/config.toml -i data/sample.json -s data/stopwords.txt > timeline.txt
```
The output is redirect to the file `timeline.txt`.

### Output format

Let's have a look at the output, the `timeline.txt` file. A time window looks like this:
```text
###############################################################################
            window from 2019-07-16 21:42:57 to 2019-07-17 00:42:57
###############################################################################
[('guam', 'village'), ('guam', 'inarajan'), ('inarajan', 'village'), ('109km',
'village'), ('109km', 'inarajan'), ('109km', 'guam'), ('guam', 'merizo'),
('merizo', 'village'), ('103km', 'merizo'), ('103km', 'guam'), ('103km',
'village')]

GUAM (INARAJAN VILLAGE):  USGS | M 5.7 - 109km S of Inarajan Village, Guam
https://t.co/rVKqPQnB91

A 5.6 magnitude earthquake recorded about 64 miles south of Merizo Guam at a
depth of 4.7 miles deep and struck at… https://t.co/KuMpWmPTXZ

[omitted]

5.7 earthquake, 109km S of Inarajan Village, Guam. 2019-07-17 08:03:54 at
epicenter (9m ago, depth 34km). https://t.co/4DsgPaThot

-------------------------------------------------------------------------------
[('22:03', 'guam')]

#Sismo vía #USGSBigQuakes =&gt; Prelim M5.6 Earthquake Guam region Jul-16 22:03
UTC, updates https://t.co/lScdvgkpad

[omitted]

Alerta desastre: Green earthquake alert (Magnitude 5.7M, Depth:33.9km) in Guam
16/07/2019 22:03 UTC, No people with… https://t.co/YW1tExRPm6

-------------------------------------------------------------------------------
[('fracture', 'owen')]

#earthquake  2019-07-16 23:49:10 (M4.7) Owen Fracture Zone region 14.5 56.3
(1cbfb) https://t.co/A8GRo5OhPc

[omitted]

M4.7 - Owen Fracture Zone region Mag: 4.7 Depth: 10km Date-Time: 2019-07-16
23:49:10 UTC https://t.co/oJnS19oZnm… https://t.co/vWmHbmJ7VY

-------------------------------------------------------------------------------
```

A window starts with a header describing the start and end time of the window:
```text
###############################################################################
            window from 2019-07-16 21:42:57 to 2019-07-17 00:42:57
###############################################################################
```

Boxes (events) are separated by dash lines. A box starts with a list of word pairs which are the result of consolidation (i.e., logically merged boxes), followed by the snippets that contain those word pairs:
```text
[('guam', 'village'), ('guam', 'inarajan'), ('inarajan', 'village'), ('109km',
'village'), ('109km', 'inarajan'), ('109km', 'guam'), ('guam', 'merizo'),
('merizo', 'village'), ('103km', 'merizo'), ('103km', 'guam'), ('103km',
'village')]

GUAM (INARAJAN VILLAGE):  USGS | M 5.7 - 109km S of Inarajan Village, Guam
https://t.co/rVKqPQnB91

A 5.6 magnitude earthquake recorded about 64 miles south of Merizo Guam at a
depth of 4.7 miles deep and struck at… https://t.co/KuMpWmPTXZ

[omitted]

5.7 earthquake, 109km S of Inarajan Village, Guam. 2019-07-17 08:03:54 at
epicenter (9m ago, depth 34km). https://t.co/4DsgPaThot

-------------------------------------------------------------------------------
```

To make the example short, part of the content is omitted and shown as `[omitted]` here.

### Use the package as a library

The core functions are also exposed as library to facilitate integration with existing analysis pipelines or UIs.
```text
>>> from event_detection.corpus import Snippet
>>> Snippet("hello, world", 123456789)
Snippet(content=hello, world, timestamp=1973-11-29T15:33:09)
>>>
>>> from event_detection.core import event_detect
>>> # input from your analysis pipeline
>>> results = event_detect(
...     stop_words,
...     input_strs,
...     window_size,
...     significance_threshold,
...     box_keepalive_time,
...     similarity_threshold,
...     token_regex_pattern,
...     min_word_length,
... )
```

## Algorithm

The key insight behind the event detection algorithm is that, when new events occur, new combinations of words end up occurring together (i.e., co-occurring) in the same sentence, headline or tweet (i.e., in the snippets of input text). Those words would typically not co-occur earlier. For example, after a tsunami in Japan, many headlines would have the words "Japan" and "tsunami" together. Similarly, after a protest erupts that is carried out by farmers in some state, the words "farmers" and "protest" would frequently co-occur together in descriptions of that event. The idea of the event detection algorithm is therefore to find frequently occurring new combinations of words that did not co-occur earlier. The algorithm does not interpret the words. It simply counts them to find new frequent co-occurrence patterns. A tunable parameter, called `significance_threshold` decides how many snippets of input need to contain the new word pattern in order for the pattern to be considered significant enough. Since we are dealing with possibly infinite input streams, the above counting is done in one window of input at a time (say every 6 hours). The size of the window is controlled using the parameter, `window_size` (expressed in hours). Hence, for example, if an event is significant if it is mentioned at least 10 times an hour, then  a possible parameterization is to set `window_size` to one hour and `significance_threshold` to 10. Once a frequent pattern is detected (according to set parameters), all text snippets in the input file that contain the pattern are put in a separate box that corresponds to the detected event.

More specifically, for the input snippets in each time window (the size of the window, in hours, is controlled by `window_size`), the algorithm first tokenizes each snippet into separate words, called keywords. Uninteresting keywords, such as "the", "this" etc., are filtered out by a stopword list provided by the user. Each snippet is then represented by a list of (remaining) keywords pairs. For example, a document with keywords:
```python
["car", "hits", "dog"]
```
will be represented as:
```python
[("car", "hits"), ("car", "dog"), ("hits", "dog")]
```
Then we count the number of occurrences of each keyword pair in the current time window. Only those keyword pairs that appear more than the `significance_threshold` are considered popular and are kept.

A popular keyword pair and all the documents in the window that contain those two words are put into a separate "box". For example, in the text below, such a popular combination is the "dog-drunk" box (with 2 documents in it):
```text
>>> from event_detection.core import Box
>>> from event_detection.corpus import Snippet
>>> import datetime
>>> st = datetime.datetime(2019, 9, 1)
>>> et = datetime.datetime(2019, 9, 2)
>>> doc1 = Snippet("A drunk driver run over a dog in a car accident", 1568938357)
>>> doc2 = Snippet("A dog was killed by a drunk driver in a car accident", 1568938380)
>>> b = Box(st, et, ('dog', 'drunk'), [doc1, doc2])
>>> b
Box(word_pair=('dog', 'drunk'), num_docs=2, start_time=2019-09-01 00:00:00, end_time=2019-09-02 00:00:00)
```

If the box already exists from a previous window, we simply update the existing box by adding the new snippets from the current window. Otherwise we create a new box. If a box has gone "cold" (i.e., hasn't been updated for several time windows controlled by the parameter `box_keepalive_time`) we close it and consider this event finished.

There is one more twist. Sometimes several created boxes end up with very similar content. In this case, they are logically merged. More specifically, the Jaccard similarity between boxes is calculated. Two boxes are logically merged if their similarity is higher than the parameter `similarity_threshold`. We use Union and Find algorithm to merge similar boxes. This process is called consolidation. Consolidation is necessary because different keyword pairs may refer to the same event instance.

## FAQ

### Why 2-combinations?
The reason of using 2-combinations is that 2-combinations of words provides a large enough space to de-multiplex different instances of same type of events. In English, there are about 3000 commonly used words, which is able to cover 95% of common texts. If we use single keywords, the number of events in a time window might exceed the number of words that we have, which means many events cannot be distinguished from each other. If we use 2-combinations of the words, then we have 10^6 combinations which should be sufficient to cover most use cases. On the other hand, the computation time increases as the increase of number of combinations. Therefore, k-combinations where k > 2 might be too slow in practice. time increases as the increase of number of combinations. Therefore, k-combinations where k > 2 might be too slow in practice.
