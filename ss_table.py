import os
import sys
import collections

class SSTable:

    def __init__(self, capacity_threshold, location):
        # this should be a btree but for now I'm using a list and
        # will sort it before writing to file
        self.memtable = []
        self.capacity_threshold = capacity_threshold
        self.location = location
        self.sparse_index = {}

        assert self.location
        assert self.capacity_threshold

    def add(self, key, value):
        self.memtable.append((key, value))

        if sys.getsizeof(self.memtable) <= self.capacity_threshold:
            return

        print("Over capacity. Writing to disk")
        self.create_disk_ss_table()

    def create_disk_ss_table(self):
        local_memtable = [t for t in self.memtable]
        print("Reseting Memtable")
        self.memtable = []

        compact_memtable = self.compact(local_memtable)
        sorted_memtable = [(k, compact_memtable[k]) for k in sorted(compact_memtable)]

        total_files = len(os.listdir(self.location))
        ss_table_name = f"sstable_{total_files + 1}"
        first_key = None

        print("Creating SSTable file named {}")
        with open(f"{self.location}/{ss_table_name}.txt", "w") as f:
            i = 0
            for k, val in sorted_memtable:
                f.write(f"{k} {val}\n")
                if i == 0:
                    first_key = k
                    i += 1

        self.sparse_index[first_key] = ss_table_name

    def read(self, key):
        val = self.memtable.get(key, None)

        if val:
            return val

        total_files = len(os.listdir(location))
        while total_files > 0:
            ss_table_file = f"sstable_{total_files}"
            with open(f"{self.location}/{ss_table_name}.txt", "w") as f:
                for line in f.readlines():
                    k, _val = line.split(" ", 1)
                    if k == key:
                        val = _val

            total_files -= 1
            if val:
                break

        return val

    def compact(self, sorted_memtable):
        result = {}
        for k, v in sorted_memtable:
            result[k] = v
        return result

    def merge():
        pass
