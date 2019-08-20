import pytest
import datetime
from event_detection.corpus import Text


@pytest.fixture
def armstrong_quote():
    return "That's one small step for a man, one giant leap for mankind.".lower()


@pytest.fixture
def armstrong_quote_2_combinations():
    return {
        ("man", "small"),
        ("small", "that's"),
        ("giant", "man"),
        ("for", "mankind"),
        ("a", "that's"),
        ("leap", "that's"),
        ("leap", "one"),
        ("for", "leap"),
        ("giant", "mankind"),
        ("for", "man"),
        ("step", "that's"),
        ("a", "step"),
        ("small", "step"),
        ("for", "one"),
        ("mankind", "that's"),
        ("a", "giant"),
        ("one", "step"),
        ("a", "for"),
        ("a", "man"),
        ("leap", "man"),
        ("man", "mankind"),
        ("for", "step"),
        ("mankind", "small"),
        ("leap", "step"),
        ("giant", "leap"),
        ("a", "one"),
        ("for", "giant"),
        ("mankind", "one"),
        ("giant", "step"),
        ("leap", "small"),
        ("a", "small"),
        ("man", "that's"),
        ("giant", "that's"),
        ("man", "step"),
        ("a", "mankind"),
        ("for", "that's"),
        ("one", "small"),
        ("a", "leap"),
        ("one", "that's"),
        ("for", "small"),
        ("mankind", "step"),
        ("man", "one"),
        ("giant", "one"),
        ("giant", "small"),
        ("leap", "mankind"),
    }


def test_create_text():
    time = datetime.datetime(2019, 8, 19, 18, 52)
    content = "This is the content"
    text = Text(content, time)
    assert text.content == content
    assert text.time.isoformat() == time.isoformat()
    assert text.content != "Not this one"


def test_tokenize(armstrong_quote):
    raise NotImplementedError


def test_tokenize_no_punctuation_in_tokens(armstrong_quote):
    raise NotImplementedError


def test_two_combinations(armstrong_quote_2_combinations):
    raise NotImplementedError


def test_two_combinations_orderd_tokens(armstrong_quote_2_combinations):
    raise NotImplementedError


def test_two_combinations_no_repetition_in_return(armstrong_quote_2_combinations):
    raise NotImplementedError
