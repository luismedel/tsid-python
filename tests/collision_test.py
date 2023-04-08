import argparse
import threading

from tsid import TSID


DEFAULT_LOOPS = 100000
DEFAULT_THREADS = 4


ncache: set[int] = set()
scache: set[str] = set()


class CreationThread(threading.Thread):
    def __init__(self, loops: int):
        self.loops: int = loops
        super().__init__()

    def run(self):
        for _ in range(self.loops):
            t = TSID.create()
            if t.number in ncache:
                print(f'Collision: {t.number}')
                return

            ncache.add(t.number)

            if TSID(t.number) != t:
                print(f'Err: {t.number}')
                return

            for format in ['s', 'S', 'x', 'X', 'd', 'z']:
                s = t.to_string(format)
                if s in scache:
                    print(f'Collision str({format}) {s}')
                    return

                scache.add(s)
                t2 = TSID.from_string(t.to_string(format), format)
                if t2 != t:
                    print(f'Err str({format}): {t.to_string(format)}')


def main(loops: int, thread_count: int) -> None:
    threads: list[CreationThread] = [CreationThread(loops)
                                     for _ in range(thread_count)]

    for thread in threads:
        thread.start()

    print('Waiting for threads to finish...')
    for thread in threads:
        thread.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""
This program tests for collisions in the TSID class and its string
serialization methods. It does this by creating a large number of TSIDs
and serializing them to strings. It also tests that the deserialization
is correct.
""")

    parser.add_argument('--loops', type=int, default=DEFAULT_LOOPS,
                        required=False, help='Number of loops per thread')
    parser.add_argument('--threads', type=int, default=DEFAULT_THREADS,
                        required=False, help='Number of threads to use')

    args = parser.parse_args()

    main(args.loops, args.threads)
