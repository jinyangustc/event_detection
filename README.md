# Apollo Event Detection Module

## Install

```bash
pip install event_detect
```

## Usage
```text
>>> import event_detect
>>> import toml
>>> import json
>>> config = toml.load("../data/config.toml")
>>> stop_words = load_stop_words()
>>> input_strs = load_input_strs()
>>> event_detect.run(config, stop_words, input_strs)
...
```
