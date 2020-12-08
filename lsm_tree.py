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
import sys
import collections
from datetime import datetime

from ss_table import SSTable


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
        self.buffer_L0.append((key, value))

    def get(self, key):
        for bf_key, val in reversed(self.buffer_L0):
            if bf_key == key:
                return val
        return TOMBSTONE_OPERATOR

    def clear(self):
        self.buffer_L0 = []

    def is_over_capacity(self):
        return sys.getsizeof(self.memtable) > self.buffer_capacity

    def compact(self):
        deleted_keys = []
        result = {}
        for k, v in self.buffer_L0:
            result[k] = v
            if v == TOMBSTONE_OPERATOR:
                deleted_keys.append(k)

        for d_key in deleted_keys:
            del result[d_key]

        return result

class DiskLevel(SSTable):

    def __init__(self, data, capacity, location):
        self.location = location
        self.level_capacity = 256 * 2^capacity
        self.capacity_threshold = 256

        self.write_to_disk(data)

    def write_to_disk(self, data):
        now = datetime.now()
        time = now.strftime("%m-%d-%Y%H-%M-%S")
        ss_table_name = f"sstable_{time}"

        print(f"Creating SSTable file named {ss_table_name}")
        with open(f"{self.location}/{ss_table_name}.txt", "w") as f:
            for k, val in data:
                f.write(f"{k} {val}\n")


class LSM_tree:
    def __init__(self, name, buffer_capacity, merge_threshold, default_path="/home/sarai/github-projects/lsm-trees/files/"):
        self.name = name
        self.default_path = default_path
        self.buffer_L0 = BufferL0(buffer_capacity)
        self.disk_levels = []

    def insert(self, key, value):
        if self.buffer_L0.is_over_capacity():
            result = self.buffer_L0.compact()

            capacity = len(self.disk_levels) + 1 if len(self.disk_levels) > 0 else 1
            new_level = DiskLevel(result, capacity, default_path)
            self.disk_levels.append(new_level)

            self.buffer_L0.clear()

        self.buffer_L0.insert(key, value)

    def update(self, key, value):
        self.insert(key, value)

    def delete(self, key):
        self.insert(key, TOMBSTONE_OPERATOR)

    def get(self, key):
        return self.buffer_L0.get(key)

    def clear_buffer(self):
        self.buffer_L0.clear()
