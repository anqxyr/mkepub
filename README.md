[![Build Status](https://travis-ci.org/anqxyr/mkepub.svg?branch=master)](https://travis-ci.org/anqxyr/mkepub)
[![Coverage Status](https://coveralls.io/repos/github/anqxyr/mkepub/badge.svg?branch=master)](https://coveralls.io/github/anqxyr/mkepub?branch=master)
[![license](https://img.shields.io/github/license/anqxyr/mkepub.svg?maxAge=2592000)]()

# mkepub

Ever wanted to turn some text into a EPUB, but it seemed like too much of a hassle? This is the library for you.

### Basic Usage

```python
import mkepub

book = mkepub.Book(title='An Example')
book.add_page(title='First Page', content='Lorem Ipsum etcetera.')
book.save('example.epub')
```

### Advanced Usage

```python
import mkepub

book = mkepub.Book(title='Advanced Example', author='The Author')
# multiple authors can be specified as a list:
# mkepub.Book(title='Advanced Example', authors=['The First Author', 'The Second Author'])
with open('cover.jpg', 'rb') as file:
    book.set_cover(file.read())
with open('style.css') as file:
    book.set_stylesheet(file.read())

first = book.add_page('Chapter 1', 'And so the book begins.')

child = book.add_page('Chapter 1.1', 'Nested TOC is supported.', parent=first)
book.add_page('Chapter 1.1.1', 'Infinite nesting levels', parent=child)
book.add_page('Chapter 1.2', 'In any order you wish.', parent=first)

book.add_page('Chapter 2', 'Use <b>html</b> to make your text <span class="pink">prettier</span>')

book.add_page('Chapter 3: Images', '<img src="images/chapter3.png" alt="You can use images as well">')
# as long as you add them to the book:
with open('chapter3.png', 'rb') as file:
    book.add_image('chapter3.png', file.read())

book.save('advanced.epub')
```