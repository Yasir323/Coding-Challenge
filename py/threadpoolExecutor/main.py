from enum import Enum
import os
from collections import deque
import queue
import time
import threading
from typing import Union, List, Tuple
import random


class Status(Enum):
    PENDING = 0
    RUNNING = 1
    DONE = 2
    EXCEPTION = 3
    CANCELLED = 4


class Future:

    def __init__(self, id_):
        self.id_ = id_
        self.status = Status.PENDING
        self.result = None

    def cancel(self):
        if self.status == Status.PENDING:
            self.status = Status.CANCELLED
            return True
        return False

    def is_cancelled(self):
        return self.status == Status.CANCELLED

    def is_pending(self):
        return self.status == Status.PENDING

    def is_done(self):
        return self.status == Status.DONE


class ThreadPoolExecutor:

    def __init__(self, num_workers: Union[int, None] = None) -> None:
        self.num_workers = min(32, os.cpu_count() + 4) if not num_workers else num_workers
        self.pending_tasks = queue.Queue()
        self.shutdown_flag = False
        self.pool = deque([], maxlen=self.num_workers)
        self.sequence_number = 0
        self.futures = []
        self.initialize_pool()

    def initialize_pool(self):
        for _ in  range(self.num_workers):
            thread = threading.Thread(target=self._worker)
            thread.start()
            self.pool.append(thread)

    def _worker(self):

        while not self.shutdown_flag:
            future, task, args = self.pending_tasks.get()
            if task is None:
                break
            if future.status == Status.PENDING:
                status = Status.RUNNING
                future.status = status
                try:
                    result = task(*args)
                except:
                    status = Status.EXCEPTION
                else:
                    status = Status.DONE

                # with threading.Lock():
                #     self.futures[future.id_].status = status
                #     self.futures[future.id_].result = result
                future.status = status
                future.result = result

    def submit(self, task: Tuple[callable, List]) -> Future:
        future = Future(self.sequence_number)
        self.futures.append(future)
        self.pending_tasks.put_nowait((future, *task))
        self.sequence_number += 1
        return future

    def shutdown(self):
        self.shutdown_flag = True
        for thread in self.pool:
            thread.join()

    def terminate(self):
        with threading.Lock():
            while True:
                try:
                    task = self.pending_tasks.get_nowait()
                except queue.Empty:
                    break
                future, _, _ = task
                future.status = Status.CANCELLED

def task(sec):
    print(time.ctime(), "Sleeping for: {} seconds".format(sec))
    time.sleep(sec)
    print(time.ctime(), "Task done!")
    return "{}: Rows returned".format(random.randint(10, 20))


def main():
    executor = ThreadPoolExecutor(4)
    futures = []
    for i in range(8):
        futures.append(executor.submit((task, [random.randint(1, 5)])))
    time.sleep(2.3)
    executor.terminate()
    for future in futures:
        status = future.status
        if status == Status.DONE:
            print(future.id_, status, future.result)
        else:
            print(future.id_, future.status)
    executor.shutdown()

if __name__ == "__main__":
    main()

