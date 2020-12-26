import os
import sys
import collections
from math import ceil

class SSTable:

    def __init__(self, capacity_threshold, location):
        # this should be a btree but for now I'm using a list and
        # will sort it before writing to file
        self.memtable = []
        self.capacity_threshold = capacity_threshold
        self.location = location
        self.sparse_index = {}
        self.merge_threshold

        assert self.location
        assert self.capacity_threshold

    def clear(self):
        self.memtable = []

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

        print(f"Creating SSTable file named {ss_table_name}")
        with open(f"{self.location}/{ss_table_name}.txt", "w") as f:
            i = 0
            for k, val in sorted_memtable:
                f.write(f"{k} {val}\n")
                if i == 0:
                    first_key = k
                    i += 1

        self.sparse_index[first_key] = ss_table_name

    def read(self, key):
        self.update_sparse_indexes()

        val = None
        for x, y in self.memtable:
            if key == x:
                val = y

        if val is not None:
            return val

        high_file = None
        lower_file = None
        for index_key, _file in self.sparse_index.items():
            if key < index_key:
                break
            last_file = _file

        with open(f"{self.location}/{last_file}", "r") as f:
            for line in f.readlines():
                k, _val = line.rsplit(" ", 1)
                if k == key:
                    val = _val
        return val

    @classmethod
    def compact(cls, sorted_memtable):
        from lsm_tree import TOMBSTONE_OPERATOR
        deleted_keys = []
        result = {}
        for k, v in sorted_memtable:
            result[k] = v
            if v == TOMBSTONE_OPERATOR:
                deleted_keys.append(k)

        for d_key in deleted_keys:
            del result[d_key]
        return result

    def merge_files(self, filter_str=None):
        if filter_str:
            list_of_files = [f for f in os.listdir(self.location) if filter_str in f]
        else:
            list_of_files = os.listdir(self.location)
        self.merge_sort_files(list_of_files)
        self.update_sparse_indexes()

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
                    key_1, val_1 = content.rsplit(" ", 1)
                    keys[key_1] = val_1
            except IndexError:
                index_files_lines["older"] = None
                key_1 = None
                val_1 = None

            try:
                line_index_2 = index_files_lines["newer"]
                if line_index_2 != None:
                    content = newer_file_content[line_index_2]
                    key_2, val_2 = content.rsplit(" ", 1)
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

    def update_sparse_indexes(self):
        print("Updating sparse index... ")
        self.sparse_index = {}
        for filename in os.listdir(self.location):
            content = self.get_file_content(filename)
            key = content[0].rsplit(" ", 1)[0]
            self.sparse_index[key] = filename

    def merge_sort_files(self, list_of_files):
        if list_of_files == []:
            return []
        if len(list_of_files) == 1:
            return list_of_files[0]

        middle = len(list_of_files) // 2
        older = list_of_files[:middle]
        newer = list_of_files[middle:]

        return self.merge(self.merge_sort_files(older), self.merge_sort_files(newer))

    def merge(self, older_file_name, newer_file_name):
        total_files = len(os.listdir(self.location))
        if total_files == len(older_file_name) or total_files == len(newer_file_name):
            return []

        if older_file_name == [] and newer_file_name != []:
            return newer_file_name

        if newer_file_name == [] and older_file_name != []:
            return older_file_name

        if type(older_file_name) == list or type(newer_file_name) == list:
            return self._merge_list_of_files(older_file_name, newer_file_name)
        else:
            return self._merge_regular_files(older_file_name, newer_file_name)

    def _merge_list_of_files(self, older_file_name, newer_file_name):
        all_files = []
        if type(older_file_name) == list:
            all_files += older_file_name
            old_file_dict = {}
            older_content = []
            for old_file in older_file_name:
                old_file_dict[old_file] = list(filter(None, self.get_file_content(old_file)))
                older_content += list(filter(None, self.get_file_content(old_file)))
        else:
            older_content = list(filter(None, self.get_file_content(older_file_name)))
            all_files.append(older_file_name)

        if type(newer_file_name) == list:
            all_files += newer_file_name
            newer_file_dict = {}
            newer_content = []
            for new_file in newer_file_name:
                newer_file_dict[new_file] = list(filter(None, self.get_file_content(new_file)))
                newer_content += list(filter(None, self.get_file_content(new_file)))
        else:
            newer_content = list(filter(None, self.get_file_content(newer_file_name)))
            all_files.append(newer_file_name)

        # print(f"Len older_content {len(older_content)}")
        # print(f"Len newer_content {len(newer_content)}")
        print(f"Merging {older_file_name} and {newer_file_name}")
        sorted_content = self._merge_two_files(older_content, newer_content)
        # print(f"Len sorted files {len(sorted_content)}")

        if type(older_file_name) == list:
            for filename in older_file_name:
                os.remove(f"{self.location}/{filename}")
        else:
            os.remove(f"{self.location}/{older_file_name}")

        if type(newer_file_name) == list:
            for filename in newer_file_name:
                os.remove(f"{self.location}/{filename}")
        else:
            os.remove(f"{self.location}/{newer_file_name}")

        if sys.getsizeof(sorted_content) <= self.capacity_threshold:
            with open(f"{self.location}/{older_file_name}", "w") as f:
                for k, val in sorted_content:
                    f.write(f"{k} {val}\n")

            return [older_file_name]

        # should split content between files
        num_files = len(all_files)
        data_chunks = self.chunks(sorted_content, num_files)
        for filename, data in zip(all_files[:num_files], data_chunks):
            with open(f"{self.location}/{filename}", "w") as f:
                for k, val in data:
                    f.write(f"{k} {val}\n")

        return all_files[:num_files]

    def _merge_regular_files(self, older_file_name, newer_file_name):
        older_content = list(filter(None, self.get_file_content(older_file_name)))
        newer_content = list(filter(None, self.get_file_content(newer_file_name)))

        print(f"Merging {older_file_name} and {newer_file_name}")
        sorted_content = self._merge_two_files(older_content, newer_content)

        os.remove(f"{self.location}/{older_file_name}")
        os.remove(f"{self.location}/{newer_file_name}")

        if sys.getsizeof(sorted_content) <= self.capacity_threshold:
            with open(f"{self.location}/{older_file_name}", "w") as f:
                for i, v in sorted_content:
                    f.write(f"{i} {v}\n")

            return [older_file_name]

        # should split content between files
        num_files = sys.getsizeof(sorted_content) // self.capacity_threshold
        middle = ceil(len(sorted_content) // 2)
        left_sorted_content = sorted_content[:middle]
        right_sorted_content = sorted_content[middle:]

        with open(f"{self.location}/{older_file_name}", "w") as f:
            for k, val in left_sorted_content:
                f.write(f"{k} {val}\n")

        with open(f"{self.location}/{newer_file_name}", "w") as f:
            for k, val in right_sorted_content:
                f.write(f"{k} {val}\n")

        return [older_file_name, newer_file_name]

    def chunks(self, lst, num_files):
        """Yield successive n-sized chunks from lst."""
        import more_itertools as mit
        return [list(c) for c in mit.divide(num_files, lst)]

    def get_file_content(self, filename):
        ss_table_file = f"{self.location}/{filename}"
        with open(ss_table_file, "r") as f:
            content = f.read().split("\n")
        return content
