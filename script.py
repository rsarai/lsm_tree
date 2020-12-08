list_of_books = ["A Christmas Carol in Prose; Being a Ghost Story of Christmas by Charles Dickens (2135)",
    "Pride and Prejudice by Jane Austen (1471)",
    "Frankenstein; Or, The Modern Prometheus by Mary Wollstonecraft Shelley (1353)",
    "Alice's Adventures in Wonderland by Lewis Carroll (844)",
    "Moby Dick; Or, The Whale by Herman Melville (704)",
    "The Yellow Wallpaper by Charlotte Perkins Gilman (657)",
    "The Adventures of Sherlock Holmes by Arthur Conan Doyle (634)",
    "Lao-tzu, A Study in Chinese Philosophy by Thomas Watters (605)",
    "The Scarlet Letter by Nathaniel Hawthorne (568)",
    "A Tale of Two Cities by Charles Dickens (562)",
    "A Modest Proposal by Jonathan Swift (545)",
    "Metamorphosis by Franz Kafka (517)",
    "The Brothers Karamazov by Fyodor Dostoyevsky (507)",
    "Et dukkehjem. English by Henrik Ibsen (468)",
    "The Importance of Being Earnest: A Trivial Comedy for Serious People by Oscar Wilde (459)",
    "Adventures of Huckleberry Finn by Mark Twain (458)",
    "Il Principe. English by Niccolò Machiavelli (444)",
    "War and Peace by graf Leo Tolstoy (422)",
    "Dracula by Bram Stoker (420)",
    "Queen of the Martian Catacombs by Leigh Brackett (407)",
    "The Picture of Dorian Gray by Oscar Wilde (401)",
    "Beowulf: An Anglo-Saxon Epic Poem (398)",
    "Walden, and On The Duty Of Civil Disobedience by Henry David Thoreau (396)",
    "Jane Eyre: An Autobiography by Charlotte Brontë (394)",
    "The Salem Belle: A Tale of 1692 by Ebenezer Wheelwright (388)",
    "The Adventures of Tom Sawyer by Mark Twain (385)",
    "The Strange Case of Dr. Jekyll and Mr. Hyde by Robert Louis Stevenson (369)",
    "The Awakening, and Selected Short Stories by Kate Chopin (358)",
    "The Rebel of Valkyr by Alfred Coppel (350)",
    "Peter Pan by J. M. Barrie (343)",
    "The Souls of Black Folk by W. E. B. Du Bois (341)",
    "The Iliad by Homer (339)",
    "Grimms' Fairy Tales by Jacob Grimm and Wilhelm Grimm (336)",
    "Great Expectations by Charles Dickens (329)",
    "Little Women by Louisa May Alcott (329)",
    "The Republic by Plato (316)",
    "Emma by Jane Austen (310)",
    "Narrative of the Life of Frederick Douglass, an American Slave by Frederick Douglass (308)",
    "Anthem by Ayn Rand (305)",
    "The Prophet by Kahlil Gibran (297)",
    "The Hound of the Baskervilles by Arthur Conan Doyle (276)",
    "The Count of Monte Cristo, Illustrated by Alexandre Dumas (275)",
    "Wuthering Heights by Emily Brontë (271)",
    "Heart of Darkness by Joseph Conrad (271)",
    "Ulysses by James Joyce (266)",
    "The Harim and the Purdah: Studies of Oriental Women by Elizabeth Cooper (258)",
    "Tractatus Logico-Philosophicus by Ludwig Wittgenstein (258)",
    "Dubliners by James Joyce (253)",
    "A Christmas Carol by Charles Dickens (251)",
    "Treasure Island by Robert Louis Stevenson (251)",
    "Uncle Tom's Cabin by Harriet Beecher Stowe (249)",
    "Siddhartha by Hermann Hesse (248)",
    "The Slang Dictionary: Etymological, Historical and Andecdotal by John Camden Hotten (245)",
    "Anne of Green Gables by L. M. Montgomery (240)",
    "Star Ship by Poul Anderson (240)",
    "Leviathan by Thomas Hobbes (238)",
    "Prestuplenie i nakazanie. English by Fyodor Dostoyevsky (237)",
    "Beyond Good and Evil by Friedrich Wilhelm Nietzsche (229)",
    "The War of the Worlds by H. G. Wells (226)",
    "The Wonderful Wizard of Oz by L. Frank Baum (223)",
    "Les Misérables by Victor Hugo (212)",
    "As It Was by Paul L. Payne (211)",
    "The Kama Sutra of Vatsyayana by Vatsyayana (211)",
    "Anna Karenina by graf Leo Tolstoy (207)",
    "The Turn of the Screw by Henry James (204)",
    "Don Quixote by Miguel de Cervantes Saavedra (203)",
    "The Odyssey by Homer (201)",
    "Pygmalion by Bernard Shaw (201)",
    "Mostly About Nibble the Bunny by John Breck (200)",
    "The Convict Ship, Volume 1 (of 3) by William Clark Russell (200)",
    "Also sprach Zarathustra. English by Friedrich Wilhelm Nietzsche (197)",
    "Alexander the Great by Jacob Abbott (197)",
    "The Call of the Wild by Jack London (195)",
    "The Happy Prince, and Other Tales by Oscar Wilde (194)",
    "Divine Comedy, Longfellow's Translation, Hell by Dante Alighieri (192)",
    "A Study in Scarlet by Arthur Conan Doyle (192)",
    "Plain Tales from the Hills by Rudyard Kipling (189)",
    "Essays of Michel de Montaigne — Complete by Michel de Montaigne (187)",
    "David Copperfield by Charles Dickens (186)",
    "The Philippines a Century Hence by José Rizal (186)",
    "Sense and Sensibility by Jane Austen (183)",
    "A Journal of the Plague Year by Daniel Defoe (178)",
    "Waldmüller: Bilder und Erlebnisse (173)",
    "Le jardin des supplices by Octave Mirbeau (172)",
    "An Index of The Divine Comedy by Dante by Dante Alighieri (170)",
    "A Dictionary of Cebuano Visayan by John U. Wolff (170)",
    "Mercy Flight by Mack Reynolds (169)",
    "The Masque of the Red Death by Edgar Allan Poe (167)",
    "The Time Machine by H. G. Wells (165)",
    "Twas the Night before Christmas: A Visit from St. Nicholas by Clement Clarke Moore (164)",
    "A Pickle for the Knowing Ones by Timothy Dexter (163)",
    "The Elements of Style by William Strunk (163)",
    "Complete Original Short Stories of Guy De Maupassant by Guy de Maupassant (161)",
    "The Nursery Rhymes of England (159)",
    "Manifest der Kommunistischen Partei. English by Friedrich Engels and Karl Marx (159)",
    "Three Men in a Boat (To Say Nothing of the Dog) by Jerome K. Jerome (158)",
    "The Legend of Sleepy Hollow by Washington Irving (158)",
    "Through the Looking-Glass by Lewis Carroll (158)",
    "Incidents in the Life of a Slave Girl, Written by Herself by Harriet A. Jacobs (157)",
    "Major Barbara by Bernard Shaw (156)"]

def count_vowels(mystr):
    return sum(list(map(mystr.lower().count, "aeiou")))

def count_as(mystr):
    return sum(list(map(mystr.lower().count, "a")))


from ss_table import SSTable

location = '/home/sarai/github-projects/lsm-trees/files/big_test'
sstable = SSTable(location=location, capacity_threshold=150)
sstable.add(list_of_books[52], 666)

for book in list_of_books:
    sstable.add(book, count_vowels(book))

sstable.merge_files()

assert sstable.read("The War of the Worlds by H. G. Wells (226)"), 6
assert sstable.read("Jane Eyre: An Autobiography by Charlotte Brontë (394)"), 15
assert sstable.read("Major Barbara by Bernard Shaw (156)"), 8

# should create 11 files
# all files should have 9 items
# last inserted book "Major Barbara by Bernard Shaw (156)" should be in the memtable
