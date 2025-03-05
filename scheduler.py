import asyncio
import time
import inspect
from typing import Callable, Any

class Task:
    def __init__(self, coro: Callable, *args: Any, priority: int = 2, task_id: str = None):
        self.coro = coro
        self.args = args
        self.priority = priority
        self.task_id = task_id or str(time.time())  # unique ID for tracking
        self.creation_time = time.time()

    def __lt__(self, other): # comparison for the priority
        return self.priority < other.priority

    async def run(self):
        """Executes the coroutine with its arguments."""
        try:
            # check if the coroutine function expects a task_id
            if "task_id" in inspect.signature(self.coro).parameters:
                return await self.coro(*self.args, task_id=self.task_id)
            else:
                return await self.coro(*self.args)
        except Exception as e:
            print(f"\n⚠️ Task {self.task_id} failed: {e}\n") # logging
            return None # so that we know that task exited with failure


class SimpleScheduler:
    def __init__(self):
        self.queue = asyncio.PriorityQueue() # stores Tasks

    async def add_task(self, coro: Callable, *args: Any, priority: int = 2, task_id: str = None):
        """Adds a task to the queue.

        Args:
            coro: The coroutine function to execute.
            *args: Arguments to pass to the coroutine.
            priority: The priority of the task (lower number = higher priority).
            task_id: The task ID.
        """
        task = Task(coro, *args, priority=priority, task_id=task_id)
        await self.queue.put(task)
        print(f"Task {task.task_id} added to queue with priority {priority}.") # logging

    async def worker(self):
        """Processes tasks from the queue."""
        while True:
            task = await self.queue.get() # retrieves and removes the highest priority task
            print(f"Running task {task.task_id}...")
            await task.run()
            self.queue.task_done() # indicates the completion
            print(f"Task {task.task_id} completed.")

    async def start(self, num_workers: int = 3): # NOTE: `num_workers` should be increased if deploying to a high performance cloud
        """Starts the scheduler's worker tasks. using asyncio.create_task"""
        self.workers = [asyncio.create_task(self.worker()) for _ in range(num_workers)]

    async def stop(self):
        """Stops the scheduler and waits for all workers to finish."""
        # cancel all worker tasks
        print("\n🛑 Stopping scheduler...")
        for worker in self.workers:
            worker.cancel()
        # wait for all worker tasks to finish
        print("Waiting for all running workers to finish...")
        await asyncio.gather(*self.workers, return_exceptions=True)
        print("Scheduler stopped.\n")

