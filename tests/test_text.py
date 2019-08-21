import pytest
import datetime
from event_detection.corpus import Text
from event_detection.corpus import tokenize


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


def test_tokenize_default_regex():
    input_str = (
        "hello Hello HELLO U.S.A. $42.42 "
        "42.42USD #twittertag hello_world yeah!!! comma, period."
    )
    tokens = tokenize(input_str, [])
    assert set(tokens) == {
        "hello",
        "u.s.a",
        "$42.42",
        "42.42usd",
        "#twittertag",
        "hello_world",
        "yeah",
        "comma",
        "period",
    }
