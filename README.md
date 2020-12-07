# LSM-Trees

- Stands for Log-Structured Merge-Tree
- It's a data structure suited for storages engines with the main focus on inserting and updating records. It's based on the principle of merging and compacting files
- The basic idea of LSM-tree is to keep a cascade of SSTables that are merged in the background.

## Components
- memtable -> AVL tree and stores key-values pairs sorted by key
- segments -> very large file stored in disk comprises of many immutable log segments accompanied by indexes like hash indexes for quick key look ups. Implemented using SSTables

When the size of the in-memory of memtable exceeds a certain threshold, (typically a few megabytes), it’s flushed to disk as a new segment as SSTable sorted by key.

-------

# SSTables
- String Sorted Tables
- Sequence of key-value pairs is sorted by key
- New pairs are appended to the end of the file
- Each key only appears once in the file (since the merge process excludes duplicates, keeping the recent one).

## Merging segments
- Similar to merge sort. Read the input files side by side, look at the first key in each file, copy the lowest key (according to the sort order) to the output file, and repeat.

## Searching
- The multiple pairs are stored ordered. In a search you will need to iterate through the pairs until you find the one that englobes your key. Recover that segment and search for the value inside. If the key is not inside, is because it was not created.
- Requires a in memory index to sign the byte offset of the segments
- The pairs inside the offset can be grouped into a block and compress it before writing it to disk

## Resume
### Insertion
- When a write comes in, add it to an in-memory balanced tree data structure. This in-memory tree is sometimes called a memtable.
- When the memtable gets bigger than some threshold write it out to disk as an SSTable file. This can be done efficiently because the tree already maintains the key-value pairs sorted by key. The new SSTable file becomes the most recent segment of the database. While the SSTable is being written out to disk, writes can continue to a new memtable instance.
- In order to serve a read request, first try to find the key in the memtable, then in the most recent on-disk segment, then in the next-older segment, etc.
- From time to time, run a merging and compaction process in the background to combine segment files and to discard overwritten or deleted values.

### Read
- A given key is first looked up in the memtable.
- Then using a hash index it’s searched in one or more segments depending upon the status of the compaction.

# TODO
- [ ] Don't merge files into single file. Do merge sort to merge its content and leave the files ordered.

# Notes
- Remember: Memory devices are byte-addressable and Storage devices are block addressable
- LSM-trees sort merges similarly sized runs (run is a sorted array of data) organizing them into levels of exponentially increasing capacities
- To get a value from a storage device one can:
    - Map pointers to indexes in main memory to make it easy to search (contains mim-max key in each block for every run). Binary search is only performed in memory and then one I/O operation to the storage device
    - Modern systems have bloom filters that point to memory indexes (one for each run)
- Merging
    - The frequency of merging always presents a trade-off between writing and reading. Which is if I merge files to frequently my writing may suffer while my readings will be easier.
    - Tiering (write optimized): Each level gather runs from the previous level and when it reach capacity these runs are merged and flushed to the next level.
    - Leveling (read optimized): Merge happens when a new run arrives and if the size exceeds the expected is flushed to the next level.

# References
- https://priyankvex.wordpress.com/2019/04/28/introduction-to-lsm-trees-may-the-logs-be-with-you/
- Designing Data-Intensive Applications
- https://www.cs.umb.edu/~poneil/lsmtree.pdf
- http://ranger.uta.edu/~sjiang/pubs/papers/wang14-LSM-SDF.pdf
- https://queue.acm.org/detail.cfm?id=3220266
- https://medium.com/databasss/on-disk-io-part-3-lsm-trees-8b2da218496f
- https://lrita.github.io/images/posts/database/lsmtree-170129180333.pdf
- https://github.com/nicodri/Log-Structured-Merge-Tree/blob/83461f0a08e27387f479988ccdd34f4da12d7b3e/src/component.c
- https://github.com/nicodri/Log-Structured-Merge-Tree/blob/master/src/LSMtree.h
- https://github.com/nicodri/Log-Structured-Merge-Tree/blob/master/src/LSMtree.c
- https://github.com/dhanus/lsm-tree/blob/master/lsm.c
- https://github.com/dhanus/lsm-tree/blob/master/lsm.h
- http://source.wiredtiger.com/2.3.1/lsm.html
- https://www.youtube.com/watch?v=b6SI8VbcT4w
