import time
from datetime import datetime

from tsid import TSID, TSIDGenerator


dt: datetime | None = None


def print_tsid(t: TSID) -> None:
    global dt

    extra: str = ''

    if dt is not None and t.datetime != dt:
        extra = ' <-- millisecond change'

    dt = t.datetime
    print(f"{t} | {t.datetime.isoformat()} | {t.random} {extra}")


if __name__ == '__main__':
    g: TSIDGenerator()
    for _ in range(10):
        print_tsid(g.create())
    time.sleep(0.1)
    print_tsid(g.create())
