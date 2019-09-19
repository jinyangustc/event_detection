from event_detection.corpus import Document
from event_detection.corpus import tokenize


def test_create_text():
    time = 1566418429
    content = "This is the content"
    text = Document(content, time)
    assert text.content == content
    assert text.time.isoformat() == "2019-08-21T15:13:49"
    assert text.content != "Not this one"


def test_tokenize_default_regex():
    input_str = (
        "hello Hello HELLO U.S.A. $42.42 "
        "42.42USD #twittertag hello_world yeah!!! comma, period. "
        "____"
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
