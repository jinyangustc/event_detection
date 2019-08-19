import datetime
from event_detection.text import Text


def test_create_text():
    time = datetime.datetime(2019, 8, 19, 18, 52)
    content = "This is the content"
    text = Text(content, time)
    assert text.content == content
    assert text.time.isoformat() == time.isoformat()
    assert text.content != "Not this one"
