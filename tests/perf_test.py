import argparse
import threading
import typing as t
from uuid import uuid4

from tsid import TSID


DEFAULT_LOOPS = 100000
DEFAULT_THREADS = 4


def tsid_create() -> None:
    _ = TSID.create().number


def tsid_create_str() -> None:
    _ = str(TSID.create())


def uuid_create() -> None:
    _ = uuid4()


def uuid_create_str() -> None:
    _ = str(uuid4())


class CreationThread(threading.Thread):
    def __init__(self, loops: int, perf_fn: t.Callable[[], None]):
        self.loops: int = loops
        self.perf_fn: t.Callable[[], None] = perf_fn
        super().__init__()

    def run(self):
        for _ in range(self.loops):
            self.perf_fn()


def main(mode: str, loops: int, thread_count: int) -> None:
    fn: t.Callable[[], None]

    match mode:
        case 'tsid':
            fn = tsid_create
        case 'tsid_str':
            fn = tsid_create_str
        case 'uuid':
            fn = uuid_create
        case 'uuid_str':
            fn = uuid_create_str
        case _:
            raise ValueError('Invalid mode')

    threads: list[CreationThread] = [CreationThread(loops, fn)
                                     for _ in range(thread_count)]

    for thread in threads:
        thread.start()

    print('Waiting for threads to finish...')
    for thread in threads:
        thread.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""
This program tests the performance of the TSID class and its string
serialization methods. It also allows to compare it with the performance of
uuid4() and str(uuid4()).
""")
    parser.add_argument('mode', type=str, help='Which mode to run in',
                        choices=['tsid', 'tsid_str', 'uuid', 'uuid_str'])
    parser.add_argument('--loops', type=int, default=DEFAULT_LOOPS,
                        required=False, help='Number of loops per thread')
    parser.add_argument('--threads', type=int, default=DEFAULT_THREADS,
                        required=False, help='Number of threads to use')

    args = parser.parse_args()

    main(args.mode, args.loops, args.threads)
