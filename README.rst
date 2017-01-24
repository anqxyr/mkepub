|Build Status| |Coverage Status| |license|

mkepub
======

**mkepub** is a minimalistic library for creating .epub files.

**Pros:**

-  Easy to use, minimalistic API.
-  Automatically generated TOC.
-  Support for nested TOC of any depth.
-  Support for embedded images.
-  In-progress books are stored on disk rather than in memory, enabling
   creation of large (5000+ pages, 20+ MiBs) epub files.
-  Adherence to the EPUB3 specs.
-  Support for most of the EPUB metadata, including language, subject,
   description, and rights.

**Cons:**

-  No support for custom page filenames or directory structure.
-  No support for reading or editing epub files.
-  No support for font-embedding or most other less commonly used EPUB
   features.
-  No content validation - using broken or unsupported html code as page
   content will lead to mkepub successfully creating a .epub file that
   does not meet EPUB3 specifications.
-  Probably other issues.

Basic Usage
~~~~~~~~~~~

.. code-block:: python

    import mkepub

    book = mkepub.Book(title='An Example')
    book.add_page(title='First Page', content='Lorem Ipsum etcetera.')
    book.save('example.epub')

Advanced Usage
~~~~~~~~~~~~~~

.. code-block:: python

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

.. |Build Status| image:: https://travis-ci.org/anqxyr/mkepub.svg?branch=master
   :target: https://travis-ci.org/anqxyr/mkepub
.. |Coverage Status| image:: https://coveralls.io/repos/github/anqxyr/mkepub/badge.svg?branch=master
   :target: https://coveralls.io/github/anqxyr/mkepub?branch=master
.. |license| image:: https://img.shields.io/github/license/anqxyr/mkepub.svg?maxAge=2592000
   :target: https://github.com/anqxyr/mkepub/LICENSE
