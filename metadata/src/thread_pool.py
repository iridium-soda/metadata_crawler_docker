"""
A custom class to rewrite concurrent.futures.ThreadPoolExecutor
Add a method to help threads to define theirselves
"""
import threading
from concurrent.futures import ThreadPoolExecutor

class CustomThreadPoolExecutor(ThreadPoolExecutor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._threads_mapping = []


    def register_position(self):
        """
        NOTE: MUST execute after stepping into the thread INSTANTLY!!!
        Add the thread_id to the map
        """
        thread_id=threading.get_ident()
        if thread_id not in self._threads_mapping:
            self._threads_mapping.append(thread_id)
        
    def get_thread_position(self):
        thread_id=threading.get_ident()
        return self._threads_mapping.index(thread_id)+1 # workerID should start from 1