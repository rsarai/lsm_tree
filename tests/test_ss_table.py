import os
import pytest
from ss_table import SSTable


def test_creates_sstable():
    with pytest.raises(TypeError):
        sstable = SSTable()

def test_adds_to_sstable():
    sstable = SSTable(location="./files/", capacity_threshold=500)
    sstable.add("aqui", 0)
    sstable.add("é", 0)
    sstable.add("náutico", 0)

    assert sstable.memtable == [("aqui", 0), ("é", 0), ("náutico", 0)]


def test_adds_to_sstable():
    sstable = SSTable(location="tests/files/", capacity_threshold=150)
    sstable.add("aqui", 0)
    sstable.add("é", 0)
    sstable.add("náutico", 0)
    sstable.add("hoje", 28)
    sstable.add("amanhã", 29)
    sstable.add("natal", 12)
    sstable.add("dezembro", 12)
    sstable.add("dia", 8)
    sstable.add("dois", 2)

    assert sstable.memtable == []
    assert sstable.sparse_index == {"amanhã": "sstable_1"}
    os.remove("tests/files/sstable_1.txt")
