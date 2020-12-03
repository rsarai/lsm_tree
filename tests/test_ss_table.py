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


def test_adds_only_to_sstable():
    sstable = SSTable(location="tests/files/", capacity_threshold=150)
    sstable.add("aqui", 0)
    assert sstable.memtable == [("aqui", 0)]


def test_saves_contents_to_file():
    sstable = SSTable(location="tests/files", capacity_threshold=150)
    sstable.add("aqui", 0)
    sstable.add("é", 0)
    sstable.add("náutico", 0)
    sstable.add("hoje", 28)
    sstable.add("amanhã", 29)
    sstable.add("natal", 12)
    sstable.add("dezembro", 12)
    sstable.add("dia", 8)
    sstable.add("dois", 2)

    output = [
        "amanhã 29\n",
        "aqui 0\n",
        "dezembro 12\n",
        "dia 8\n",
        "dois 2\n",
        "hoje 28\n",
        "natal 12\n",
        "náutico 0\n",
        "é 0\n",
    ]
    with open("tests/files/sstable_1.txt", "r") as f:
        lines = f.readlines()
        for x, y in zip(lines, output):
            assert x == y
    os.remove("tests/files/sstable_1.txt")


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


def test_compact_removes_duplicates_keeping_the_last():
    memtable = [
        ("oi", 0),
        ("tchau", 5),
        ("contador de corridas", 0),
        ("contador de corridas", 1),
        ("contador de caminhadas", 0),
        ("contador de corridas", 2),
        ("quantidade de passos", 7206),
        ("quantidade de passos", 7365),
    ]
    result = SSTable.compact(memtable)
    assert result == {
        "oi": 0,
        "tchau": 5,
        "contador de corridas": 2,
        "contador de caminhadas": 0,
        "quantidade de passos": 7365
    }


def test_merge_two_files():
    file1 = "tests/files/sstable_1.txt"
    file2 = "tests/files/sstable_2.txt"
    with open(file1, "w") as f:
        f.write("amanhã 29\n")
        f.write("aqui 0\n")
        f.write("dezembro 12\n")
        f.write("dia 8\n")
        f.write("dois 2\n")
        f.write("hoje 28\n")
        f.write("natal 12\n")
        f.write("náutico 0\n")
        f.write("é 0\n")

    with open(file2, "w") as f:
        f.write("amanhã 1000\n")
        f.write("aqui 0\n")
        f.write("dan 2\n")
        f.write("hoy 28\n")
        f.write("manual 9\n")
        f.write("more 89\n")
        f.write("sol 0\n")
        f.write("zorro 0\n")

    files_and_contents = {}
    with open(file1, "r") as f:
        key = "sstable_1"
        content = f.read().split("\n")
        files_and_contents[key] = content

    with open(file2, "r") as f:
        key = "sstable_2"
        content = f.read().split("\n")
        files_and_contents[key] = content

    sstable = SSTable(location="tests/files", capacity_threshold=150)
    sstable.sparse_index["amanhã"] = "sstable_1"
    sstable.sparse_index["amanhã"] = "sstable_2"

    results = sstable._merge_two_files(files_and_contents["sstable_1"], files_and_contents["sstable_2"])
    assert results == [
        ('amanhã', '1000'),
        ('aqui', '0'),
        ('dan', '2'),
        ('dezembro', '12'),
        ('dia', '8'),
        ('dois', '2'),
        ('hoje', '28'),
        ('hoy', '28'),
        ('manual', '9'),
        ('more', '89'),
        ('natal', '12'),
        ('náutico', '0'),
        ('sol', '0'),
        ('zorro', '0'),
        ('é', '0'),
    ]
    os.remove("tests/files/sstable_1.txt")
    os.remove("tests/files/sstable_2.txt")

def test_merge_files():
    file1 = "tests/files/sstable_1.txt"
    file2 = "tests/files/sstable_2.txt"
    file3 = "tests/files/sstable_3.txt"
    with open(file1, "w") as f:
        f.write("amanhã 29\n")
        f.write("aqui 0\n")
        f.write("dezembro 12\n")
        f.write("dia 8\n")
        f.write("dois 2\n")
        f.write("hoje 28\n")
        f.write("natal 12\n")
        f.write("náutico 0\n")
        f.write("é 0\n")

    with open(file2, "w") as f:
        f.write("amanhã 1000\n")
        f.write("aqui 0\n")
        f.write("dan 2\n")
        f.write("hoy 28\n")
        f.write("manual 9\n")
        f.write("more 89\n")
        f.write("sol 0\n")
        f.write("zorro 0\n")

    with open(file3, "w") as f:
        f.write("corrida 10\n")
        f.write("dados 5\n")
        f.write("elefante 2\n")
        f.write("gato 28\n")
        f.write("ko 9\n")
        f.write("limão 89\n")
        f.write("mar 5\n")
        f.write("ovo 0\n")

    expected_result = [
        "amanhã 1000\n",
        "aqui 0\n",
        "corrida 10\n",
        "dados 5\n",
        "dan 2\n",
        "dezembro 12\n",
        "dia 8\n",
        "dois 2\n",
        "elefante 2\n",
        "gato 28\n",
        "hoje 28\n",
        "hoy 28\n",
        "ko 9\n",
        "limão 89\n",
        "manual 9\n",
        "mar 5\n",
        "more 89\n",
        "natal 12\n",
        "náutico 0\n",
        "ovo 0\n",
        "sol 0\n",
        "zorro 0\n",
        "é 0\n",
    ]

    sstable = SSTable(location="tests/files", capacity_threshold=150)
    sstable.sparse_index["amanhã"] = "sstable_1"
    sstable.sparse_index["amanhã"] = "sstable_2"
    sstable.sparse_index["corrida"] = "sstable_3"

    sstable.merge_files()
    with open("tests/files/sstable_1.txt", "r") as f:
        content = f.readlines()
        for x, y in zip(content, expected_result):
            assert x == y

    assert sstable.sparse_index == {"amanhã": "sstable_1"}
    os.remove("tests/files/sstable_1.txt")
