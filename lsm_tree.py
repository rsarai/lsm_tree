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
import json
import collections
from datetime import datetime
from pprint import pprint

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
        return sys.getsizeof(self.buffer_L0) > self.buffer_capacity

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

    def __init__(self, size_ratio, location):
        self.name = f"level_L_{size_ratio}"
        self.location = location
        self.capacity_threshold = 512
        self.size_ratio = size_ratio
        self.level_capacity = self.capacity_threshold * (2**size_ratio)
        self.runs = None
        self.sparse_index = {}

        self._set_current_runs()

    def get_current_size(self):
        return sum(
            [os.path.getsize(self.location + "/" + r + ".txt")
            for r in self.runs]
        )

    def is_over_capacity(self):
        return self.get_current_size() > self.level_capacity

    def _set_current_runs(self):
        if len(os.listdir(self.location)) == 0:
            self.runs = set()
            return

        self.runs = set(
            [
                f.replace(".txt", "") for f in os.listdir(self.location) if self.name in f
            ]
        )

    def write_to_disk(self, data):
        now = datetime.now()
        time = now.strftime("%m-%d-%Y%H-%M-%S.%f")
        ss_table_name = f"sstable_{self.name}_clock_{time}"

        # print(f"Creating SSTable file named {ss_table_name}")
        with open(f"{self.location}/{ss_table_name}.txt", "w") as f:
            for k, val in data:
                f.write(f"{k} {val}\n")

        self._set_current_runs()
        if len(self.runs) >= 2:
            self.merge_files(filter_str=self.name)
            self._set_current_runs()

        return ss_table_name

    def update_sparse_indexes(self):
        _new_sparse_index = []
        for filename in os.listdir(self.location):
            if not self.name in filename:
                continue

            content = self.get_file_content(filename)
            key = content[0].rsplit(" ", 1)[0]
            _new_sparse_index += [{"key": key, "file": filename}]

        self.sparse_index = sorted(_new_sparse_index, key=lambda k: k["key"])

    def get(self, key):
        val = None
        last_file = None
        for item_dict in self.sparse_index:
            index_key = item_dict["key"]
            _file = item_dict["file"]
            if key < index_key:
                break
            last_file = _file

        if last_file:
            with open(f"{self.location}/{last_file}", "r") as f:
                for line in f.readlines():
                    k, _val = line.rsplit(" ", 1)
                    if k == key:
                        val = _val
        return val



class LSM_tree:
    def __init__(self, name, buffer_capacity, max_levels=5,
                 default_path="/home/sarai/github-projects/lsm-trees/files/"):
        self.name = name
        self.default_path = default_path
        self.buffer_L0 = BufferL0(buffer_capacity)
        self.disk_levels = [
            DiskLevel(size_ratio + 1, default_path)
            for size_ratio in range(max_levels)
        ]
        self.max_levels = max_levels

    def get_file_content(self, filename):
        table_file = f"{self.default_path}/{filename}.txt"
        with open(table_file, "r") as f:
            content = f.read().split("\n")

        result = []
        for line in content:
            if line:
                k, _val = line.rsplit(" ", 1)
                result.append((k, _val))
        return result

    def show(self):
        print("\n\n")
        print(self.name)
        print(self.buffer_L0.buffer_L0)
        for disk in self.disk_levels:
            print(f"===== {disk.name} =====")
            print("Runs: ", disk.runs)
            print("Current Size: ", disk.get_current_size())
            print("Capacity: ", disk.level_capacity)
        print("===== ===== ===== =====\n")

    def merge_levels(self, smaller_level, bigger_level):
        content = []
        for filename in smaller_level.runs:
            content += self.get_file_content(filename)

        compact_content = SSTable.compact(content)
        sorted_content = [(k, compact_content[k]) for k in sorted(compact_content)]
        bigger_level.write_to_disk(sorted_content)

        for filename in smaller_level.runs:
            os.remove(f"{self.default_path}/{filename}.txt")
        smaller_level.runs = set()
        smaller_level.update_sparse_indexes()
        bigger_level.update_sparse_indexes()

    def insert(self, key, value):
        if not self.buffer_L0.is_over_capacity():
            self.buffer_L0.insert(key, value)
            return

        compact_memtable = self.buffer_L0.compact()
        sorted_content = [(k, compact_memtable[k]) for k in sorted(compact_memtable)]
        i = 0
        merge_list = []
        while True:
            disk_level = self.disk_levels[i]
            if not disk_level.is_over_capacity():
                break

            merge_list.append(i)
            i += 1

        disk_level.write_to_disk(sorted_content)
        if merge_list:
            for i in merge_list[::-1]:
                if i == self.max_levels - 1:
                    # Max level is not merged
                    continue

                self.merge_levels(self.disk_levels[i], self.disk_levels[i + 1])

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

    def search(self, key):
        res = None

        res = self.get(key)
        if res != TOMBSTONE_OPERATOR and res is not None:
            return res

        for d_level in self.disk_levels:
            res = d_level.get(key)
            if res:
                return res

        return res
