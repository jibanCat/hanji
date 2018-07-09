from collections import defaultdict
### WHY "defaultdict", INSTEAD OF THE REGULAR "dict" FUNCTION?
from datetime import datetime
from bs4 import BeautifulSoup
import bs4
from urllib import request
import urllib
import time
import random
import re
import os
import glob
import pandas as pd


class Book:
    """Han-Ji '<http://hanchi.ihp.sinica.edu.tw/ihp/hanji.htm>'_ Dataset.
    
    Attributes:
        flat_bodies (list): a list containing all htmls 
        flat_passages (list): a list containing the text of all passages (i.e., every individual piece in a book). Users should define their own methods to organize the passages.
        flat_heads (list): a list containing all the text of the heads (i.e., the metadata at the top of each individual piece, like title and author). Users should define their own methods to organize the heads.
        flat_meta (list): a list containing all metadata (dictionary) extracted from bookmarks. User should define their own methods to extract metadata.
        paths (list): a list of paths extracted from the "bookmark" provided in the database. e.g., 集／總集／文選／卷第二十七　詩戊之一／樂府上／古樂府三首／飲馬長城窟行(P.1277)
    
    Args: 
        bookname (string): the name of the book, default = ''
        date (string): the date you collected the book, default = None
        creator (string): the name of the creator who created the instance
        description (string): optional description for the instance
        
    Methods:
        fetch_data(URL): fetch book bs4 obj from a start page URL of a Book in Han-Ji
        extract_paths(): extract paths from bookmark in self.flat_bodies list and append paths to self.paths
        write_htmls(path): write data into htmls on the disk in path
        load_htmls(path): load data from htmls on the disk in path
    """
    
    def __init__(self, bookname='', date=None, creator=None, description=''):
        self.flat_bodies   = []
        self.flat_passages = []
        self.flat_heads    = []
        self.flat_meta     = []
        self.paths = []
        self.author_bag = defaultdict(list)
        self.bookname    = bookname
        self.date        = datetime.strptime(date, '%Y-%m-%d')
        self.creator     = creator
        self.description = description
        ### ?
        
    def __getitem__(self, index):
        '''
        Args:
            index (int): Index
            
        Returns:
            bs4 html object in the flat_bodies
        '''
        return self.flat_bodies[index]
    
    def __len__(self):
        return len(self.flat_bodies)
    
    def __repr__(self):
        fmt_str = "Dataset {} ".format(self.bookname)
        fmt_str += "created by {} at {}.\n".format(self.creator, self.date)
        fmt_str += "{} data points. ".format(self.__len__()) 
        if len(self.author_bag) > 2:
            fmt_str += "\n{} authors and commentars.\n".format(len(self.author_bag))
        fmt_str += self.description
        return fmt_str

    def pretty_print(self, index):
        """pretty print the html source page in a Jupyter notebook cell output"""
        from IPython.display import HTML
        return HTML(self._pretty_html( self.flat_bodies[index] ))

    def _pretty_html(self, soup):
        """cut off irrelevant content, such as side columns in the webpage, from the Han-Ji HTML source page. 
        This procedure aims to save memory for the computer."""
        head = soup.find("head")
        span_id_fontstyle = str(soup.find("span", {"id": "fontstyle"}))
        path  = str(soup.find('a', attrs={'class', 'gobookmark'}))
        HTML_string = """<html>
                {}
            <body>
                {}
            </body>
        </html>
        """.format(str(head), "{}\n\t{}".format(path, span_id_fontstyle))
        return HTML_string
    
    def fetch_data(self, URL, pages_limit=10000, print_bookmark=False, html_cutoff=False,
                   BASE_URL='http://hanchi.ihp.sinica.edu.tw/ihpc/', sleep_range=(1, 3)):
        '''fetch book bs4 obj from a start page URL of a Book in Han-Ji
        
        Args:
            URL (string): the start page url from han-ji website
            page_limit (int): the limit of next pages you can scrape. default = 10000
            print_bookmark (bool): print the bookmark while fetching the data. default = False
            html_cutoff (bool): cut off the irrelavant side column and tags in Han-Ji raw html files, 
                                to save memory usage.
        '''
        for i in range(pages_limit):            
            # use urllib.request to get the html content of the website
            req  = request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
            page = request.urlopen(req)
            soup = BeautifulSoup(page, 'lxml')

            # show information on the screen
            if print_bookmark == True:
                print("[Info] Start fetching {}. {}/{} epoch.".format(
                    soup.find('a', attrs={'class', 'gobookmark'}).text, i + 1, pages_limit))            
            else:
                print("[Info] Start fetching {}. {}/{} epoch.".format(URL, i + 1, pages_limit))            
            
            # check if the content is the same as previous page
            ### ? -> Response: this line is an ad-hoc solution for dealing with the first page while scraping. There must be a better way to do it.
            if i > 0:
                buffer = self.flat_bodies[-1].find_all('div', attrs={'style': True})
            else:
                # use a dummy list for the buffer for the first page
                buffer = ['dummy']
            
            # if the first and last elements in the buffer are the same as current page
            # delete page and save the current page.
            ### GOOD SOLUTION, BUT ARE WE SURE THERE ARE NO HIDDEN TRAPS IN USING THIS RULE?  COULD TWO CONSECUTIVE BUT DIFFERENT POEMS HAVE THE SAME START AND END WORD?
            ### Response: the comparison here is for end and start sentences of a poem. 
            ### It's quite unlikely two poems have the same start and end senetences, right?
            if (buffer[-1] == 
                soup.find_all('div', attrs={'style': True})[-1]) and (
                buffer[0] == 
                soup.find_all('div', attrs={'style': True})[0]):
                print("[Warning] This page is the same as the previous one, discard previous one and store the new one.")
                if html_cutoff == True:
                    self.flat_bodies[-1] = BeautifulSoup( self._pretty_html(soup), 'lxml' )
                else:    
                    self.flat_bodies[-1] = soup
            else:
                # append to flat bodies
                if html_cutoff==True:
                    self.flat_bodies.append( BeautifulSoup( self._pretty_html(soup), 'lxml'))
                else:
                    self.flat_bodies.append(soup)
               
            
            # find the next page
            next_page = soup.find('img', {'src' : '/ihp/snext.gif'})
            if next_page != None:
                url = next_page.find_parent()['href']
            else:
                print('[Info] No further next page. Stop fetching.')
                break
                
            URL = urllib.parse.urljoin(BASE_URL, url)
            time.sleep(random.randint(sleep_range[0], sleep_range[1]))
            
    def extract_paths(self):
        '''extract paths from bookmark in self.flat_bodies list and append paths to self.paths'''
        self.paths = []
        
        for soup in self.flat_bodies:
            # extract "gobookmark" class
            path  = soup.find('a', attrs={'class', 'gobookmark'}).text
            self.paths.append(path)
    
    def _sum_indent_and_padding(self, texts):
        '''returns the sum of indents and paddings in the texts.'''
        return [
            sum([int(num[0]), int(num[1])])
             for text in texts 
             for num in re.findall(r'text-indent:(.*?)em;padding-left:(.*?)em;', text['style'])
        ]        

    def _indent_and_padding(self, texts):
        '''Return the indent and padding tuples of indents and paddings in the texts.'''
        return [
            (int(num[0]), int(num[1]))
             for text in texts 
             for num in re.findall(r'text-indent:(.*?)em;padding-left:(.*?)em;', text['style'])
        ]                    
                                        
    def write_htmls(self, path='data/', html_cutoff=False):
        '''writing all htmls in flat_bodies to the folder data/

        Args:
            path (str) : the path to the folder you want to write htmls files
            html_cutoff (bool) : whether or not you want to cut off irrelevant contents in Han-Ji webpage 
        '''
        try:
            os.makedirs(path)
        except OSError:
            pass
            
        for i,soup in enumerate(self.flat_bodies):
            filename = os.path.join(path, '{}_{}.html'.format(
                self.bookname, str(i).zfill(4)))
            with open(filename, 'w', encoding='utf-8') as file:
                if html_cutoff==True:
                    file.write( self._pretty_html(soup) )
                else:
                    file.write(str(soup))
                
        # update the description
        self.description += 'Writing data to {}.\n'.format(os.path.join(path, self.bookname + '*'))
        
    def load_htmls(self, path='data/'):
        '''loading all files with filename = "bookname_*.html" in path data/
        '''
        self.flat_bodies = []
        i = 0
        while 1:
            filename = os.path.join(path, '{}_{}.html'.format(
                self.bookname, str(i).zfill(4)))
            if os.path.isfile(filename):
                with open(filename, 'r', encoding='utf-8') as file:
                    self.flat_bodies.append(BeautifulSoup(file.read(), 'lxml'))
            else:
                print("[Info] Stop at loading {}.".format(filename))
                break
            i += 1
        print("[Info] Total length of the data is {}.".format(len(self.flat_bodies)))
        
        # update the description
        self.description += 'Loading data from {}.\n'.format(path.format(os.path.join(path, self.bookname + '*')))

class WenShuan(Book):
    """WenShuan Dataset
    
    Attributes:
        head_bag (dict): A dictionary store all heads in the WenShuan as keys and comments as values.
        author_bag (dict): a dictionary stores all authors name and their comments. The structure is like this: 
            '丘希範': [(88,
               <font size="-2">梁史曰：丘遲，字希範，吳興人。八歲能屬文，及長，辟徐州從事。高祖踐祚，拜中書郎，遷司徒</font>),
              (88, <font size="-2">從事中郎。卒。集題曰：兼中書侍郎丘遲上。</font>),
              (239, ''),
              (490, '')], ...
              numbers stands for the index in flat arrays.
              author_bag is a template that allow you to use for further applications such as extrac metadata, but it is not working well for every books. 

    Args: same as Book class
    
    Methods:
        get_author_bag(): Extract author names from align=right tags and compare with author names in the bookmarks
        extract_meta(): Extract meta data from self.paths. Index 3 in path for scroll, 4 for category, 5 for author name, after 5 for the title. The method would check the author name using author_bag automatically.
        passages2tuples(): Call _passages2TextCommentPairs to transform self.flat_bodies, to text comment pairs and store in self.flat_passages
        heads2tuples(): Convert heads in <h3> tags to (header, [comment, commnent, ...]) pairs.
        extract_commentators(): Insert commentators into metadata from author_bag
    
    """
    
    def __init__(self, date, creator, description=''):
        Book.__init__(self, 'wenshuan', date, creator, description)
        self.sound_glosses_bag = []
        
    def _path_author_name_yield(self, fifth_path_item):
        '''yield the author name in the path via checking if it is in the author_bag'''
        # get the min and max length of author_bag
        author_bag_len = [len(key) for key in self.author_bag.keys()]
        for i in range(min(author_bag_len), max(author_bag_len) + 1):
            if fifth_path_item[:i] in self.author_bag:
                yield (i, fifth_path_item[:i])

    def extract_meta(self):
        '''Extract meta data from self.paths.
        Note: index 3 in path for scroll, 4 for category, 5 for author name, after 5 for the title.
        '''
        for path in self.paths:            
            # initialize the meta data
            meta = defaultdict(str)
            path_split = path.split('／')

            # check if the length of the path is longer than 5
            if len(path_split) >= 5:
                scroll = path_split[3].split()[0]
                poem   = path_split[3].split()[1]
                category = path_split[4]
                try:
                    idx, author = next(iter(self._path_author_name_yield(path_split[5])))
                except StopIteration:
                    print('[Warning] No author name in the path, {}.'.format(path))
                    author = ''
                    idx = 0

                # grab the title, which is the text behind the author name    
                title = '/'.join([x if i > 0 else x[idx:] for i,x in enumerate(path_split[5:])])

            else:
                author   = ''
                category = ''
                poem     = ''
                scroll   = ''
                title    = path_split[3]
                print('[Warning] Path is too short, {}. Only use title for metadata.'.format(path))
                

            # add values for keys
            meta['scroll'] = scroll
            meta['category']   = poem
            meta['genre'] = category
            meta['author'] = author
            meta['title']  = title
            self.flat_meta.append(meta)       
        
        # update description
        self.description += "Grabbed meta data with {} unique author names from paths.\n".format(len(set(meta['author'] for meta in self.flat_meta)))


    def passages2tuples(self, indent=4):
        '''Call _passages2TextCommentPairs to transform self.flat_bodies, 
        to text comment pairs and store in self.flat_passages'''
        for body in self.flat_bodies:
            texts  = body.find_all('div', attrs={'style': True})

            # get the indent of the text
            sum_indent_padding = self._sum_indent_and_padding(texts)

            # setting threshold: sum_indent_padding > indent for authors
            texts = [texts[i] for i,s in enumerate(sum_indent_padding) if s <= indent]
            
            tcpairs = self._passages2TextCommentPairs(texts)
            self.flat_passages.append(tcpairs)
            
        # update description
        mean_num_pairs = sum(
            [len(tcpairs) for tcpairs in self.flat_passages]
        ) / len(self.flat_passages)
        self.description += "Got text comment pairs for WenShuan with mean of the pairs for each passage is {}.\n".format(mean_num_pairs)

    def _passages2TextCommentPairs(self, texts, comment_attr='size'):
        '''
        Input texts object (bs4.element.ResultSet) and return 
        a DataFrame which seperate 
        the passages and comments (with <font size="-2"></font> tag)
        into different columns. 
        '''
        # get all elements (includes passages and comments) into a long list,
        # which means make a whole page html into a list, 
        # such that text = [passage, ..., comment, ..., passage, ...]
        text = [item for sublist in texts for item in list(sublist)]

        # filter out irrevelant elements, leave only passages and 
        # comments with font size = '-2'
        textIter = filter(lambda x : 
            isinstance(x, bs4.element.NavigableString) 
            # modification here to make sure all sizes fit in, not only size = -2
            or (comment_attr in x.attrs
            if isinstance(x, bs4.element.Tag) else False), 
            text)

        # the list to append (passage, comment) tuples
        tcpairs = []

        # buffer lists to store passages and tags independently
        buffer_text = []
        buffer_tag  = []

        for t in textIter:
            # This is the tricky part, takes me lots of time to figure it out. 
            # since the ordering of text and tag is like
            # ['text', ..., 'tag, ..., 'text'(next text element after a series of tags), ... ]
            # we should :
            if ( len(buffer_text) > 0 and # count at least one text element
                 len(buffer_tag) > 0 and  # count at least one tag element
                # and make sure # we have already looped to
                # **the next text element after tags**
                 isinstance(t, bs4.element.NavigableString) ): 

                # append tuple (text, tag), which means (passage, comment)
                tcpairs.append((''.join(buffer_text), ''.join(buffer_tag)))

                # clear buffer lists to be empty
                buffer_text.clear()
                buffer_tag.clear()

            # if t is passage (bs4.element.NavigableString):
            # force bs4.element.NavigableString to be str and append to the list    
            if isinstance(t, bs4.element.NavigableString):
                buffer_text.append(str(t)) 

            # else if t i a tag (bs4.element.Tag):
            # find all texts in tag and strip the childern tags. 
            # append all into the list        
            elif isinstance(t, bs4.element.Tag):
                buffer_tag.append(
                    ''.join(t.find_all(text=True, recursive=False))
                )

        # append anything else leave in th buffer lists into List
        # and remember to exclude the spaces.
        if (not ''.join(buffer_text).isspace() and 
            not ''.join(buffer_tag).isspace()):
            tcpairs.append((''.join(buffer_text), ''.join(buffer_tag)))

        return tcpairs

    def heads2tuples(self):
        '''Convert heads in <h3> tags to (header, [comment, commnent, ...]) pairs.'''
        self.flat_heads = []
        self.head_bag   = defaultdict(list)

        for body in self.flat_bodies:
            # extract heads <h3>
            heads = body.find_all('h3')
            
            flat_head = []
            for head in heads:
                # exclude the blank string in the head
                pair = [h for h in head if h != ' ']

                # assume the first element of <h3> is the header
                header_name, comments = pair[0], pair[1:]

                # preserve the comments into a shared dict in the class.
                # Plan to match the comments here with self.flat_meta 
                self.head_bag[header_name.replace('\u3000', '').replace('文選', '')] = comments
                
                # append a pair of text and comment 
                flat_head.append((header_name, comments))
                
            # append header with the following content
            self.flat_heads.append(flat_head)

        # update desciption
        mean_len_comment = sum([len(c) for head in self.flat_heads for _,c in head]) / len(self.flat_heads)
        self.description += "Grabbed tuple pairs from heads, the mean number of elements follow by the header is {}.".format(mean_len_comment)  
        
    def extract_commentators(self):
        '''Insert commentators into metadata from author_bag'''
        for author,comment_list in self.author_bag.items():
            if '注' in author:
                for comment in comment_list:
                    index, _ = comment
                    self.flat_meta[index]["commentator"] = author

    def _punctuation_count(self, phrase, pun_bag = {"、","。", "，", "？", "：", "；", "「", "」"}):
        '''Count num punctuactions in phrase based on a given pun_bag'''
        return sum(phrase.count(p) for p in pun_bag)

    def _backward_char_search(self, phrase, exclude = {" ", "、","。", "，", "？", "：", "；", "「", "」"}):
        '''Return the frist char which is not in exclude.'''
        for char in phrase[::-1]:
            if char not in exclude:
                return char
            else: continue       
                
    def _sound_glosses_check(self, text, comment):
        '''Check the comment is a sound glosses or not.
        If it is a sound glosses, return (character reffered to, sound) as a tuple.'''
        if  (self._punctuation_count(comment) < 2 and 
            len(re.sub(r"[、。，？：；「」]", "", comment.replace(" ", ""))) < 4 and 
            comment != ""):
            return self._backward_char_search(text), re.sub(r"[、。，？：；「」]", "", comment)
            
        elif (self._punctuation_count(comment.split("。")[0]) == 0 and 
            0 < len(comment.split("。")[0]) < 4):
            return self._backward_char_search(text), comment.split("。")[0]
        
        else: return None
        
    def extract_sound_glosses(self, remove_sound_glosses=True):
        self.sound_glosses_bag = []
        new_flat_passages  = []

        for i,passage in enumerate(self.flat_passages):
            # A place to save sound glosses    
            new_passage = []
            p_preivous_buffer = ''

            for j,(p,c) in enumerate(passage):
                # check if c is a single phrase comment
                sound_gloss = self._sound_glosses_check(p, c)

                if sound_gloss != None:
                    self.sound_glosses_bag.append((i,) + sound_gloss)
                    p_preivous_buffer += p

                    # CASE 2: Inline Sound Glosses
                    if len(c) >= 5:
                        if p_preivous_buffer[-1] != "。":
                            p_preivous_buffer += "。"

                    # CASE 1: Single Phrase
                    elif re.search(r"(.+)([、。，？：；「」])", c) != None:
                        match = re.search(r"(.+)([、。，？：；「」])", c)
                        p_preivous_buffer += match.group(2)

                else:
                    new_passage.append((p_preivous_buffer + p, c))
                    p_preivous_buffer = ''

            new_flat_passages.append(new_passage)

        if remove_sound_glosses:
            self.flat_passages = new_flat_passages

    def get_author_bag(self, indent=4, name_length_limit=5):
        '''uses indents in the original webpage to gather a bag of authors (with any comments that may be attached to the authors).
        If indents + paddings are smaller than indent(default=4) and the length of the name is smaller than name_length_limit(default=5), then consider it as an author name.
        '''
        ### I DON'T GET THE LAST PART ("length of the name is smaller than name_length_limit(default=5)")
        buffer_author = None
        
        for i,soup in enumerate(self.flat_bodies):
            # gets the text body
            body  = soup.find_all('span', {'id' : 'fontstyle'})[0]
            author_list = self._plausible_authorlist(body, indent)
            
            for author_text in author_list:
                # one possible danger here is that next may not 
                # be enough if there are multiple authors in one line
                try:
                    author = next(iter(self._author_yield(author_text)))
                except StopIteration:
                    author = None
                try:
                    tag = next(iter(self._tag_yield(author_text)))
                    if author is None:
                        print("[Warning] No author name in {} item, but got a tag. Attach this tag to previous author name {}.".format(i, buffer_author))
                        author = buffer_author 
                except StopIteration:
                    if author:
                        tag = ''
                        
                if author:
                    # check the length of the author name
                    # split the name with space and check the mean of length
                    author_split = author.split()
                    if sum([len(x) for x in author_split]) / len(author_split) < name_length_limit:
                        # add new key in the author_bag
                        self.author_bag[author].append((i, tag))    
                    else:
                        print("[Warning] Author name, {} in {}, is too long. Discard this one.".format(author, i))
                        continue
                    
                buffer_author = author
                
    def _sum_indent_and_padding(self, texts):
        '''returns the sum of indents and paddings in the texts.'''
        return [
            sum([int(num[0]), int(num[1])])
             for text in texts 
             for num in re.findall(r'text-indent:(.*?)em;padding-left:(.*?)em;', text['style'])
        ]        
                            
    def _plausible_authorlist(self, body, indent=4):
        '''gets a plausible author list using indent number and 
        align="right" '''
        texts  = body.find_all('div', attrs={'style': True})
        # get the indent of the text
        sum_indent_padding = self._sum_indent_and_padding(texts)

        # setting threshold: sum_indent_padding > indent for authors
        author_list = [texts[i] for i,s in enumerate(sum_indent_padding) if s > indent]

        if body.find('div', attrs={"align": True}):
            author_list.append(body.find('div', attrs={"align": True}))
        return author_list
    
    def _author_yield(self, author_text):
        '''yields the first occurrence of the NavigableString'''
        for tag in author_text:
            if isinstance(tag, bs4.element.NavigableString):
                if not tag.isspace():
                    yield tag

    def _tag_yield(self, author_text, tag="font", attrs="size"):
        '''yields  tag with a given attrs'''
        for tag in author_text:
            if isinstance(tag, bs4.element.Tag):
                if "size" in tag.attrs:
                    yield tag    
             

    def _writeECSV(self, filename, meta, df):
        '''write a pandas.DataFrame into csv file with comments contain'''
        with open(filename, 'w', encoding='utf-8') as file:
            for key, value in meta.items():
                file.write('# {} = {}\n'.format(key, value))
            df.to_csv(file)

    def write_passages_ECSV(self, path="文選/"):
        '''writing passages into extend CSV format on the disk'''
        try:
            os.makedirs(path)
        except OSError:
            pass
        
        for i, (passage, meta) in enumerate( zip( self.flat_passages, self.flat_meta ) ):
            # define the filename based on scroll and title
            filename = os.path.join( path, '{}_Passage_{}_{}.csv'.format(i, meta['scroll'], meta['title'].replace('/', '-') ) )
            
            # write the csv files
            self._writeECSV(filename, meta, pd.DataFrame( passage, columns=["passage_text", "passage_comment"]))        

class SongShu(Book):
    """SongShu Dataset
    
    Attributes:
        flat_meta : a list of bookmarks in SonShu extracted from Han-Ji
        flat_passages : a list of ``passages`` in SongShu. 
            Each ``passages`` contain a list of passage in a piece of work.
            i.e., flat_passages = [passages1(list, passages2(list), ...]
                  passages1 = [passage1(str), passage2(str), ...]    
                  
    Args: same as Book class
    
    Methods:
        extract_meta(): Extract meta data from self.paths. Index 3 in path for scroll, 4 for category, 5 for author name, after 5 for the title. The method would check the author name using author_bag automatically.    
        extract_passages(): Extract passages based on indent==2 & padding==0. 
                            If there's no passage in this page, merge all texts into one string.
    """
    
    def __init__(self, date, creator, description=''):
        Book.__init__(self, 'ShongShu', date, creator, description)

    def extract_meta(self):
        self.flat_meta = []
        for path in self.paths:
            meta = {}
            bookmark_split = path.split('／')

            # Navie implementation
            category = bookmark_split[3].split('\u3000')[0] # 本紀、志、列傳
            scroll   = bookmark_split[4].split('\u3000')[0] # 卷 N 
            categrory_number   = bookmark_split[4].split('\u3000')[1] # 本紀第 N 
            title = '/'.join(bookmark_split[5:]).replace('..[底本：宋元明三朝遞修本]', '')
            meta['category'] = category
            meta['category_number'] = categrory_number
            meta['scroll'] = scroll
            meta['title']  = title
            self.flat_meta.append(meta)

    def extract_passages(self):
        '''Extract passages from SongShu, which divided by the ( indent == 2 & padding == 0 )'''
        self.flat_passages = []

        for body,path in zip(self.flat_bodies, self.paths):
            texts  = body.find_all('div', attrs={'style': True})
            try:
                self.flat_passages.append(
                    self._passage2paragraphs(texts)
                )
            except IndexError as e:
                print("[Warning] Not the right indent.", path)
                self.flat_passages.append(
                    ''.join([text.text for text in texts])
                )


    def _passage2paragraphs(self, texts):
        '''Organize a passage with its paragraph, which is defined using ( indent == 2& padding == 0 )
        '''
        # concatenent the paragraphs with indents not equal to 2 to the previous paragraph
        new_texts = []
        
        # get the pairs of indents and paddings 
        indent_padding_list = self._indent_and_padding(texts)
        
        for text, (indent, padding) in zip(texts, indent_padding_list):
            if indent == 2 and padding == 0:
                # only save the text, without tags
                new_texts.append(
                    ''.join([s for s in text if isinstance(s, bs4.NavigableString)])
                )
            else:
                new_texts[-1] += ''.join([s for s in text if isinstance(s, bs4.NavigableString)])
            
        return new_texts                            