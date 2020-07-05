"""
Work by buffering writes (inserts, deletes, and updates) in main memory and deferring their persistence to a later
time. While such designs slightly penalize reads, which then need to search various different levels of data
structures, they allow writes to be performed efficiently, and dramatically increase data ingestion rates.

An LSM-tree consists of a hierarchy of storage levels that increase in size.
- Buffer: smallest and stored in main memory, and its purpose is to buffer updates for efficiency
- L1 ... Lk : The rest of the levels are stored on disk.

As new writes accumulate and the buffer fills, the buffer contents must be persisted to disk as a
file with contents sorted on key order.

Simple proof of concept implementation, real implementation will be done in C
"""
import os
import collections


TOMBSTONE_OPERATOR = "/!/"


class Level:
    """
        Levels have exponentially increasing capacities
        Contain runs
    """
    def __init__(self, filepath, max_runs):
        self.filepath = filepath
        self.max_runs = max_runs


class BufferL0:
    """
        Sorting can happen at insertion time or when the buffer gets full
    """
    def __init__(self, buffer_capacity):
        self.buffer_capacity = buffer_capacity
        self.buffer_L0 = []         # TODO make this a AVL tree

    def insert(self, key, value):
        if len(self.buffer_L0) == self.buffer_capacity:
            return

        self.buffer_L0.append({key: value})
        self.buffer_L0 = sorted(self.buffer_L0, key=lambda k: list(k.keys())[0])
        return value

    def get(self, key):
        for item in reversed(self.buffer_L0):
            if list(item.keys())[0] == key:
                return item[key]
        return TOMBSTONE_OPERATOR

    def clear(self):
        self.buffer_L0 = []


class LSM_tree:
    def __init__(self, name, buffer_capacity, merge_threshold, default_path="/home/sarai/github-projects/lsm-trees/files/"):
        self.name = name
        self.default_path = default_path
        self.buffer_L0 = BufferL0(buffer_capacity)
        self.disk_levels = []

    def insert(self, key, value):
        result = self.buffer_L0.insert(key, value)
        if result:
            return
        self.write_buffer_to_disk()
        self.clear_buffer()
        self.insert(key, value)

    def update(self, key, value):
        self.insert(key, value)

    def delete(self, key):
        self.insert(key, TOMBSTONE_OPERATOR)

    def get(self, key):
        return self.buffer_L0.get(key)

    def write_buffer_to_disk(self):
        with open('disk',"w+") as f:
            # read data on disk into memory
            # content = f.read()
            # merge the sorted buffer and the sorted disk contents
            # self.merging()
            pass

    def merging(self):
        """
            Takes as input a set of sorted files and creates as output a
            new set of sorted files non-overlapping in key range
        """

    def clear_buffer(self):
        self.buffer_L0.clear()
