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
            if k in deleted_keys:
                # if key was deleted but a new insertion happened
                # keep recent value
                deleted_keys.remove(k)
            result[k] = v
            if v == TOMBSTONE_OPERATOR:
                deleted_keys.append(k)

        for d_key in deleted_keys:
            del result[d_key]

        return result

class DiskLevel(SSTable):

    def __init__(self, size_ratio, location, merge_threshold):
        self.name = f"level_L_{size_ratio}"
        self.location = location
        self.capacity_threshold = 256
        self.size_ratio = size_ratio
        self.level_capacity = self.capacity_threshold * 2^size_ratio
        self.runs = []
        self.merge_threshold = merge_threshold
        self.sparse_index = {}

    def is_over_capacity(self):
        return sum([os.path.getsize(r) for r in self.runs]) > self.level_capacity

    def write_to_disk(self, data):
        now = datetime.now()
        time = now.strftime("%m-%d-%Y%H-%M-%S")
        ss_table_name = f"sstable_{self.name}_clock_{time}"

        print(f"Creating SSTable file named {ss_table_name}")
        with open(f"{self.location}/{ss_table_name}.txt", "w") as f:
            for k, val in data:
                f.write(f"{k} {val}\n")

        self.runs.append(ss_table_name)

        if len(self.runs) >= 2:
            self.merge_files(filter_str=self.name)

        return ss_table_name


class LSM_tree:
    def __init__(self, name, buffer_capacity, merge_threshold, max_levels=5,
                 default_path="/home/sarai/github-projects/lsm-trees/files/"):
        self.name = name
        self.default_path = default_path
        self.buffer_L0 = BufferL0(buffer_capacity)
        self.disk_levels = [
            DiskLevel(size_ratio + 1, default_path) for size_ratio in range(max_levels)
        ]
        self.max_levels = max_levels

    def merge_levels(smaller_level, bigger_level):
        content = []
        for filename in smaller_level.runs:
            content += self.get_file_content(filename)

        compact_content = self.compact(content)
        sorted_content = [(k, compact_content[k]) for k in sorted(compact_content)]
        bigger_level.write_to_disk(sorted_content)

        for filename in smaller_level.runs:
            os.remove(f"{self.default_path}/{filename}")
        smaller_level.runs = []

    def insert(self, key, value):
        if not self.buffer_L0.is_over_capacity():
            self.buffer_L0.insert(key, value)
            return

        result = self.buffer_L0.compact()
        i = 0
        merge_list = []
        while True:
            disk_level = self.disk_levels[i]
            if not disk_level.is_over_capacity():
                break

            merge_list.append(i)
            i += 1

        disk_level.write_to_disk(result)
        if merge_list:
            for i in merge_list[::-1]:
                if i == self.max_levels - 1:
                    # Max level is not merged
                    continue

                merge_levels(self.disk_levels[i], self.disk_levels[i + 1])

        # TODO get indexes for search
        self.buffer_L0.clear()

    def update(self, key, value):
        self.insert(key, value)

    def delete(self, key):
        self.insert(key, TOMBSTONE_OPERATOR)

    def get(self, key):
        return self.buffer_L0.get(key)

    def clear_buffer(self):
        self.buffer_L0.clear()
