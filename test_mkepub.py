#!/usr/bin/env python3
"""mkepub Test Suite."""

import mkepub
import subprocess

###############################################################################


def test_book_simple():
    book = mkepub.Book(title='Simple Test')
    with open('cover.jpg', 'rb') as coverfile:
        book.set_cover(coverfile.read())
    book.add_page('Page 1', 'Content of the first page.')
    book.add_page('Page 2', 'Content of the second page.')
    book.save('simple.epub')

    subprocess.check_output(['epubcheck', 'simple.epub'])
