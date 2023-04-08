import argparse
import threading
import typing as t
from uuid import uuid4

from tsid import TSID

cache: set[int] = set()


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

    threads: list[CreationThread] = []
    for _ in range(thread_count):
        thread: CreationThread = CreationThread(loops, fn)
        thread.start()
        threads.append(thread)

    print('Waiting for threads to finish...')
    for thread in threads:
        thread.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', type=str, help='Which mode to run in',
                        choices=['tsid', 'tsid_str', 'uuid', 'uuid_str'])
    parser.add_argument('loops', type=int, default=1000000,
                        help='Number of loops per thread')
    parser.add_argument('threads', type=int, default=4,
                        help='Number of threads to use')

    args = parser.parse_args()

    main(args.mode, args.loops, args.threads)
