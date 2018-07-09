# Han-Ji (漢籍) Scraper

- The scraper function is defined as a method in the `Book` class. You can scrape the html files using

```python
from hanji import Book
# get a instance of Book class
book = Book.Book(bookname="name", date="2018-05-29", creator="MF)

# get the htmls from the Han-Ji website, The UR
book.fetch_data('http://hanchi.ihp.sinica.edu.tw/ihpc/hanji?@30^1389784921^802^^^60311004001000010006@@460127924',
                pages_limit=1000, print_bookmark=False,)
```

- Now, `bs4` objects are stored in the `book.flat_bodies` list. You can write the html files into `data` folder via

```python
# writing htmls into a folder
book.write_htmls(path="data")

# loading files to book
book.load_htmls(path="data")
```

- Exctract the bookmark (the dependencies of the poems) out of the page, just typed

```python 
book.extract_paths()
```

- To preview the first page of Han-Ji page in a pretty HTML format, type

```python
book.pretty_print(0) # 0 for the first page in scraped Han-Ji data
```

## WenShuan (文選) Organizer

- The `WenShuan.py` was designed as a wrapper of the `Book.py` and have specific methods to organize the texts files in WenShuan

```python 
from hanji import Book
# get a instance out of WenShuan class
wenshuan = Book.WenShuan('2018-05-29', 'MF')
wenshuan.fetch_data(URL="(URL for Han-Ji WenShuan)",
                pages_limit=1000, print_bookmark=True,)

# organize the text files 
wenshuan.extract_paths()         # extract the bookmarks
wenshuan.get_author_bag()        # get the bag of author names and comments
wenshuan.extract_meta()          # extract the meta data
wenshuan.passages2tuples()       # get the passsage into (text, comment) tuples
wenshuan.heads2tuples()          # get headers into (head, comment, ...) tuples
wenshuan.extract_commentators()  # append commentators to metadata
wenshuan.extract_sound_glosses() # append all sound glosses in comments into a list and remove them from the self.flat_passages
```
- Writing to CSV: `Wenshuan.py` provides a method to write `wenshuan.flat_passages` and `wenshuan.flat_meta` to a series of CSV files in folder (default folder is `"/文選"`). Metadata is listed in the comments (`#`) in the headers. 

```python
wenshuan.write_passages_ECSV()
```


## (Ongoing) SongShu (宋書) Organizer 

- The `SongShu.py` was also designed as a wrapper of `Book.py` class. SongShu organizer separated every pieces of works into passages. 

```python
from hanji import Book
songshu = Book.SongShu("2018-06-28", "MF")
songshu.fetch_data(URL="(The first page URL of SongShu in Han-Ji)", pages_limit=2000, print_bookmark=True)
songshu.write_htmls()
```

- To recover the fetched data we downloaded last time, run
```python
songshu = SongShu("2018-06-28", "MF")
songshu.load_htmls()
# [Info] Stop at loading data/ShongShu_0851.html.
# [Info] Total length of the data is 851.
```

- To extract metadata, bookmarks, and organize the passages:
```python
# preprocessing the songshu data to get metadata and bookmarks
# and separate the passages in every pages
songshu.extract_paths()
songshu.extract_meta()
songshu.extract_passages()
```  
The <font color="#A60628">Warning</font> in the above output cell show that some pages in SonShu do not have a clear definition of **separating the passages**.


## Rare Character Identifier

Some characters in Han-Ji are rare chars. In this case, if we use `urllib` to parse the source page, we only get the fragments of the rare chars (構字形). 

To resolve this situation, we can use JavaScript API in http://char.iis.sinica.edu.tw/ to acquire the fragments of chars, and then we can use the fragments to search the correct rare char unicodes. 

The following lines show how to scrape the a bag of rare char unicodes from a text string:
```python
from rare_char_converter import rare_char_converter

selenium_driver = "(PATH TO YOUR SELENIUM DRIVER)"
text = "(YOUR HAN-JI TEXT)"
rare_char_converter(text, selenium_driver)
# Return: dict, {"(fragments of char)" : (UNICODE, string of the rare char)}
```

## Tutorial List:

1. [`Book -- Basic Usage.ipynb`](http://nbviewer.jupyter.org/github/jibanCat/DigitalHumanities/blob/master/Han-Ji/tutorials/Book%20--%20Basic%20Usage.ipynb): The basic usage of `Book.py`. The way to scrape a book in Han-Ji and class methods to do further exploration.
2. [`WenShuan -- How to Use and Sound Glosses Search.ipynb`](http://nbviewer.jupyter.org/github/jibanCat/DigitalHumanities/blob/master/Han-Ji/tutorials/WenShuan%20--%20How%20to%20Use%20and%20Sound%20Glosses%20Search.ipynb): How to use WenShuan class and an exploration for sound glosses in WenShuan.
3. [`WenShuan -- What happens to the number of separate pieces (76X comparing to 528).ipynb`](http://nbviewer.jupyter.org/github/jibanCat/DigitalHumanities/blob/master/Han-Ji/tutorials/WenShuan%20--%20What%20happens%20to%20the%20number%20of%20separate%20pieces%20%2876X%20comparing%20to%20528%29.ipynb): A tutorial for counting the number of piece works in WenShuan.
4. [`WenShuan -- Rare Char Identify Using Selenium.ipynb`](http://nbviewer.jupyter.org/github/jibanCat/DigitalHumanities/blob/master/Han-Ji/tutorials/WenXuan%20--%20Rare%20Char%20Identify%20Using%20Selenium.ipynb): Identify the rare characters in WenShuan using rare chars search in sinica.
5. [`SongShu -- Place Names Export (Part 1).ipynb`](http://nbviewer.jupyter.org/github/jibanCat/DigitalHumanities/blob/master/Han-Ji/tutorials/SongShu%20--%20Place%20Names%20Export%20%28Part%201%29.ipynb): How to use Songshu class and simplest regex to match all place names in the SongShu class.
6. [`SongShu -- Place Names Export (Part 2).ipynb`](http://nbviewer.jupyter.org/github/jibanCat/DigitalHumanities/blob/master/Han-Ji/tutorials/SongShu%20--%20Place%20Names%20Export%20%28Part%202%29.ipynb): Export place names to `csv`s and data viz the frequency of characters associated with place names.