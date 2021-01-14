# LSM-Trees

## TODO
#### SSTable
- [x] Don't merge files into single file. Do merge sort to merge its content and leave the files ordered.
- [x] Test merging files with updates on key, check if the most recent is kept.
#### LSM Tree
- [x] Build memory component
- [x] Build disk component
- [x] Build search
    - simulating fence pointers
- [x] Build merge
    - Ideas for recursive merge. All inputs are always saved on the level 1 not matter what, if the level 1 is over capacity trigger the recursive merge
    - [here](images/lsm_tree.png)
- [x] Sorted merging is not working for multiple files in the same level. eg: level 3 has two files, the files are sorted inside themselfs but not related to each other
- [ ] Finish reading the [The Log-Structured Merge-Tree (LSM-Tree)](https://www.cs.umb.edu/~poneil/lsmtree.pdf) paper.
- [ ] In some places I'm filtering for level files and in others I'm not, fix this.
- [ ] Understand better merge policies (leveling, tiering, lazy leveling)
- [ ] Implement both ways of merging strategies and add as a parameter on LSM class
- [ ] Implement bloom filter to optimize search
- [ ] Refactor to assure consistency across background merges
---------

- LSM stands for Log-Structured Merge-Tree
- It's a data structure suited for storages engines with the main focus on inserting and updating records. It's based on the principle of merging and compacting files
- The basic idea of LSM-tree is to keep a cascade of SSTables that are merged in the background.

## Implementation trade-offs
- Each implementation balances the cost of I/O updates and the cost of I/O reads. Due to the level structure of the LSM one needs to perform merging operations in order to remove duplicates and ease reads, when to do the merge is the critical point. In one approach, you can have frequent merges that allow you ease search but delay updates and writes, on the other side you may delay merges until they are stricly necessary having fast writes and updates, but slow recover and higher space cost.

## Components
- memtable -> AVL tree and stores key-values pairs sorted by key (called buffer or L0)
- segments -> very large file stored in disk comprises of many immutable log segments accompanied by indexes like hash indexes for quick key look ups. Implemented using SSTables
    - Has a comparable directory structure to a B-tree, but is optimized for sequential disk access, with nodes 100% full, and sequences of single-page nodes on each level below the root packed together in contiguous multi-page disk blocks for efficient arm use

## Implementation
#### Parameters
- Number of levels
- Size ratio between levels
- Merging strategy

#### Requirements
- High update rate (100k - 1M updates per second for flash storage and 1k- 10k of updates per second for HDD storage)
- Efficient reads (1K - 5K reads per second for flash storage and 20-100 reads per second for HDD storage
- Every level can follow either of the following merge policies - leveling, tiering, or lazy leveling.
- Each level includes bloom filter(s) with optimized bits per entry to determine if a key is not contained in the level.
- Each level includes fence pointers to allow page or block access within a run
    - Fence pointers contain the first key of every block on the run, this is key avoid scanning all blocks when searching for a key.


## Base Logic
#### Writes
- Updates and inserts are treated in the same way
- Deletes are also performed in the same way as updates (first added to buffer), but with a special marker, which denotes this record as "deleted".
- When the memtable fills the sorted data is flushed to a new file on disk. This process repeats as more and more writes come in.

#### Merging
- The merge process takes as input a set of sorted files and creates as output a new set of sorted files non-overlapping in key range, called a run
- The current level has reached its threshold size, therefore its contents needs to be pushed to larger levels as part of the merge process to clear more space at the current level.
- A new run is being moved into the current level which has already reached its allowed threshold of runs, and therefore any run being merged into the current level cannot simply be added, rather it must be merged with a run that is already at the current level in order to abide under the threshold. In this fashion, it is possible for a merge to cause a cascade of further merges through the larger levels that follow.
- When data are sort-merged, deletes and updates are performed, keeping only the newest values when there are entries that modify the same key.
- The merging first tries to merge the content from memory into the most recent segment, when the filling block is packed it then moves to a new free area on disk
    - "When the growing C0 tree first reaches its threshold size, a leftmost sequence of entries is deleted from the C0 tree (this should be done in an efficient batch manner rather than one entry at a time) and reorganized into a C1 tree leaf node packed 100% full."
    - Successive multi-page blocks of the C1 tree leaf level in ever increasing key-sequence order are written out to disk to keep the C0 tree threshold size from exceeding its threshold.

##### Tiering
- Write-optimized
- With tiering, we merge runs within a level only when the level reaches capacity. So runs will acumulate unmerged until they reach the level capacity.
- Search in tiering would search first on the buffer, than in each one of runs inside level 1, if nothing is found repeat the same procedure with the following levels

##### Leveling
- Read-optimized
- Runs are merged as soon as they get, this results in only a single file per level.
- Search in leveling would search first on the buffer, than in single file inside the level 1, if nothing is found repeat the same procedure with the following levels

#### Lazy Leveling
- Lies on a sweet spot providing faster updates and lookups. It works by optmizing writes, the idea is that the cost of writing and them merging is equal to all levels (usually the amount of writes you need to make before merge is the same for all merges). This means even though the heaviest load in on the higher level you are still spending the same effort in all levels by merging all the them the same amount of times. Since the smaller levels are exponentially smaller that the highest (:]) they become superfulous since they demand less work.
- Lazy Leveling performs a double merging strategy, the smallers levels use the tiering approach, while the highest level uses the leveling merge approach.

![](/images/leveling_and_tiering.png)

These two approaches are controlled by the size ratio between the levels. When the size ratio is 1 the tiering methodology works it's exactly the leveling approach.

#### Reads
- Reads happen first at L0 and are propagate to the levels
- To avoid doing a binary search on every single run during query answering, various optimizations can be performed by maintaining auxiliary structures. Common ones are: fence pointers and Bloom filters.

#### Consistency and Level Management.
- While files have correspondence with the underlying file system, levels are conceptual and must be managed by the LSM-tree implementation. To maintain a consistent view of the immutable files, it is typical to maintain globally a catalog and manifest structure (in-memory and persisted) which describes the file to level relationships and indicate which set of files form a current snapshot.
- That way, background merges that create new files can continue progress while ongoing readers are guaranteed to see a consistent view of the set of files corresponding to a single snapshot of the LSM-tree without disruption to query correctness.

#### Happy Path
- Inserts are added to an in-memory buffer (memtable)
- When the memtable fills the sorted data is flushed to a new file on disk. This process repeats as more and more writes come in.
- Periodically the system performs a compaction. Compaction selects multiple files and merges them together, removing any duplicated updates or deletions
- [Image](images/lsm_tree.png)

## Optimizations

#### Monkey
- This is mostly a read optimization it relies on using Bloom filter to speed up searches. The key thing is that the rate of false-positives produced my the bloom filters may be decrease for smaller levels (since the bigger cost will be on searching in higher levels), by realocating the filters to lower levels it is possible to keep the same memory usage with fewer false-positives (faster reads).

#### Dostoevsky
- Automatic way to tweak the size ratio and the amount of the types of merging strategies.

-------

# SSTables
- String Sorted Tables
- Saved on disk
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
- https://www.cs.umb.edu/~poneil/lsmtree.pdf
- https://stratos.seas.harvard.edu/files/stratos/files/dostoevskykv.pdf
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
- https://yetanotherdevblog.com/lsm/
- http://www.benstopford.com/2015/02/14/log-structured-merge-trees/
- https://scholar.harvard.edu/files/stratos/files/dostoevskykv.pdf
