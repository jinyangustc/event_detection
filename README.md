# Apollo Event Detection Package


```text
.
├── data
│   ├── 2019-07-1517.json
│   ├── config.toml
│   ├── example.json
│   ├── generate_stopwords.py
│   ├── helper.py
│   └── stopwords.txt
├── event_detection
│   ├── core.py
│   ├── corpus.py
│   └── __init__.py
├── examples
│   └── simple_console_timeline.py
├── LICENSE
├── README.md
├── requirements.txt
├── setup.py
└── tests
    ├── __init__.py
    └── test_text.py
```

## Install

### Use the package

```bash
git clone https://github.com/jinyangustc/event_detection.git
cd event_detection

# it is recommended to creat a virtual environment.
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
pip install -e .

# install development dependencies, such as pre-commit, pytest and black, etc.
pip install -r requirements.txt

# initialize pre-commit hooks
pre-commit install
```

Now install the package in the virtual environment in editable mode. For more information about installing local
packages with `pip` please refer `pip help install`.


## Algorithm
TODO: Explain the insight of the algorithm.

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
