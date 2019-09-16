# Apollo Event Detection Package

## Install

```
pip install event_detect
```

## Usage
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

## Algorithm
TODO: Explain the insight of the algorithm.
