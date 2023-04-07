import threading
from datetime import datetime
from tsid.tsid import TSID

cache: set[int] = set()

class CreationThread(threading.Thread):
    def __init__(self):
        self.count: int = 0
        super().__init__()

    def run(self):
        while True:
            t: TSID = TSID.fast()
            if t.number in cache:
                print(f"Collision ({self.count}): {t.number} {t.random} {t.datetime} {datetime.now()}")
            else:
                cache.add(t.number)

            self.count += 1

            if self.count % 1000000 == 0:
                print(f"Thread {self.name}, count: {self.count}")

print("Testing collision. Press Ctrl+C to stop.")

threads: list[CreationThread] = []

for i in range(8):
    t: CreationThread = CreationThread()
    t.start()
    threads.append(t)

for t in threads:
    t.join()
