import datetime
from typing import NamedTuple


class Text(NamedTuple):
    content: str
    time: datetime.datetime
