import asyncio
import time
import inspect
from typing import Callable, Any, Dict


class Task:
    def __init__(self, coro: Callable, *args: Any, priority: int = 2, task_id: str = None, route_path: str = None):
        self.coro = coro
        self.args = args
        self.priority = priority
        self.task_id = task_id or str(time.time())  # unique ID for tracking
        self.creation_time = time.time()
        self.route_path = route_path

    def __lt__(self, other):
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
            return None # so that we can check if the task exited with failure



class SimpleScheduler:
    def __init__(self):
        self.queue = asyncio.PriorityQueue() # stores Tasks
        self.workers = []

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
            print(f"✅ Task {task.task_id} completed.")

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



class CustomScheduler:
    def __init__(self):
        self.workers = []
        self.queue = asyncio.PriorityQueue()
        self.rover_queues: Dict[str, int] = {}  # track tasks per rover: {rover_id: task_count}
        self.response_times: Dict[str, float] = {}  # track avg response times: {route_path: avg_time}
        self.custom_priority_paths: Dict[str, int] = {} # for high priority paths
        # self.last_admin_activity: float = time.time()

        # dynamic adjustment parameters (tuning parameters)
        self.rover_queue_threshold = 5
        self.response_time_threshold = 2.0  # seconds
        self.admin_inactivity_threshold = 600  # 10 minutes
        # self.admin_priority_reduction = 2

    async def add_task(self, coro: Callable, *args: Any, priority: int = 2, task_id: str = None, route_path: str = None):
        # Check for custom-priority paths
        if route_path in self.custom_priority_paths:
            priority = self.custom_priority_paths[route_path]

        task = Task(coro, *args, priority=priority, task_id=task_id, route_path=route_path)
        await self.queue.put(task)

        # Update rover queue counts if applicable
        if "rover_id" in inspect.signature(coro).parameters: # if it is a rover function
           rover_id_index = list(inspect.signature(coro).parameters.keys()).index("rover_id")
           if len(args) > rover_id_index: # Make sure rover_id exists in arguments
                rover_id = args[rover_id_index]
                if rover_id:
                    self.rover_queues[str(rover_id)] = self.rover_queues.get(str(rover_id), 0) + 1

        print(f"Task {task.task_id} added to queue with priority {priority} (path: {route_path}).")


    async def worker(self):
        while True:
            task = await self.queue.get()
            start_time = time.time()

            print(f"Running task {task.task_id}...")
            await task.run()
            end_time = time.time()
            self.queue.task_done()

            # update response times (exponential moving average)
            if task.route_path:
                if task.route_path in self.response_times:
                    self.response_times[task.route_path] = (
                        0.9 * self.response_times[task.route_path]
                        + 0.1 * (end_time - start_time)
                    )
                else:
                    self.response_times[task.route_path] = end_time - start_time

            # update rover queue counts
            if "rover_id" in inspect.signature(task.coro).parameters:
                rover_id_index = list(inspect.signature(task.coro).parameters.keys()).index("rover_id")
                if len(task.args) > rover_id_index:
                    rover_id = task.args[rover_id_index]
                    if rover_id:
                        self.rover_queues[str(rover_id)] = max(0, self.rover_queues.get(str(rover_id), 0) - 1)

            print(f"✅ Task {task.task_id} completed in {end_time - start_time:.4f} seconds.")
            await self.dynamic_adjust() # call dynamic adjustment after each task


    async def dynamic_adjust(self):
        """Dynamically adjusts task priorities based on conditions."""
        # 1. Rover Load: if a particular rover has too many tasks in queue, increase priority
        for rover_id, count in self.rover_queues.items():
            if count > self.rover_queue_threshold:
                # Increase priority of rover tasks
                for task in self.queue.queue:  # iterate through the "queue"
                    if "rover_id" in inspect.signature(task.coro).parameters:
                        rover_id_index = list(inspect.signature(task.coro).parameters.keys()).index("rover_id")
                        if len(task.args) > rover_id_index:
                            if task.args[rover_id_index] == rover_id:
                                task.priority = max(0, task.priority - 1) # increase priority

        # 2. Mobile App Response Times: if the average response time is too much, increase priority
        for route_path, avg_time in self.response_times.items():
            if avg_time > self.response_time_threshold:
                for task in self.queue.queue:
                    if task.route_path == route_path:
                        task.priority = max(0, task.priority - 1)

    async def start(self, num_workers: int = 3):
        self.workers = [asyncio.create_task(self.worker()) for _ in range(num_workers)]


    async def stop(self):
        """Stops the scheduler and waits for all workers to finish."""
        print("\n🛑 Stopping scheduler...")
        for worker in self.workers:
            worker.cancel()
        print("Waiting for all running workers to finish...")
        await asyncio.gather(*self.workers, return_exceptions=True)
        print("Scheduler stopped.\n")

    def set_custom_priority_paths(self, path_priorities: Dict[str, int]):
        """Sets high priority for specific API paths.

        Args:
            path_priorities: A dictionary where keys are route paths (strings)
                             and values are the desired priority (integers).
        """
        self.custom_priority_paths = path_priorities

