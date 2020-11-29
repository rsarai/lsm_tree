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

    def merge_files(self):
        total_files = len(os.listdir(location))
        files_and_contents = {}
        for i in range(total_files + 1):
            ss_table_file = f"{self.location}/sstable_{i}.txt"
            with open(ss_table_file, "r") as f:
                key = f"sstable_{i}"
                content = f.read().split("\n")
                files_and_contents[key] = content

        # need to start from the beginning to the ending
        # 1, 2, 3, 4, 5
        # [1, 2] - 1, [1, 3] - 1, [1, 4] - 1, [1, 5] - 1
        while len(os.listdir(location)) > 1:
            newer_file_name = "sstable_" + str(len(os.listdir(location)))
            older_file_name = "sstable_" + str(newer_file - 1)
            print(f"Merging {older_file_name} with {newer_file_name}")

            new_file_content = _merge_two_files(
                files_and_contents[older_file_name],
                files_and_contents[newer_file_name]
            )

            os.remove(f"{self.location}/{older_file_name}.txt")
            os.remove(f"{self.location}/{newer_file_name}.txt")
            del self.sparse_index[newer_file_name]
            del self.sparse_index[older_file_name]

            new_file_name = older_file_name
            print(f"Creating merged SSTable file named {new_file_name}")
            with open(f"{self.location}/{new_file_name}.txt", "w") as f:
                i = 0
                for k, val in new_file_content:
                    f.write(f"{k} {val}\n")
                    if i == 0:
                        first_key = k
                        i += 1

            self.sparse_index[first_key] = new_file_name

    def _merge_two_files(self, older_file_content, newer_file_content):
        older_file_content = list(filter(None, older_file_content))
        newer_file_content = list(filter(None, newer_file_content))
        index_files_lines = {"older": 0, "newer": 0}
        new_file_content = []

        while set(index_files_lines.values()) != None:
            keys = {}
            try:
                line_index_1 = index_files_lines["older"]
                if line_index_1 != None:
                    content = older_file_content[line_index_1]
                    key_1, val_1 = content.split(" ", 1)
                    keys[key_1] = val_1
            except IndexError:
                index_files_lines["older"] = None
                key_1 = None
                val_1 = None

            try:
                line_index_2 = index_files_lines["newer"]
                if line_index_2 != None:
                    content = newer_file_content[line_index_2]
                    key_2, val_2 = content.split(" ", 1)
                    keys[key_2] = val_2
            except IndexError:
                index_files_lines["newer"] = None
                key_2 = None
                val_2 = None

            if key_1 is None and key_2 is None:
                break

            if key_1 is None or key_2 is None:
                if key_1:
                    new_file_content.append((key_1, val_1.strip("\n")))
                    index_files_lines["older"] += 1

                if key_2:
                    new_file_content.append((key_2, val_2.strip("\n")))
                    index_files_lines["newer"] += 1

            elif key_1 == key_2:
                new_file_content.append((key_2, val_2.strip("\n")))
                index_files_lines["newer"] += 1
                index_files_lines["older"] += 1
            else:
                smaller_key = min([key_2, key_1])
                smaller_key_value = keys[smaller_key].strip("\n")
                new_file_content.append((smaller_key, smaller_key_value))
                key_index = "newer" if smaller_key == key_2 else "older"
                index_files_lines[key_index] += 1

        return new_file_content


if __name__ == "__main__":
    files_and_contents = {}
    location="tests/files"
    total_files = len(os.listdir(location))

    for i in range(1, total_files + 1):
        ss_table_file = f"{location}/sstable_{i}.txt"
        with open(ss_table_file, "r") as f:
            key = f"sstable_{i}"
            content = f.read().split("\n")
            files_and_contents[key] = content

    older_file_content = files_and_contents["sstable_1"]
    newer_file_content = files_and_contents["sstable_2"]
    result = _merge_two_files(older_file_content, newer_file_content)
    print(result)
