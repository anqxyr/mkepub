#!/usr/bin/env python3
"""mkepub Test Suite."""

import pathlib

import mkepub


def test_book_simple():
    file = pathlib.Path('simple.epub')
    if file.exists():
        file.unlink()
    book = mkepub.Book(title='Simple Test')
    with open('cover.jpg', 'rb') as coverfile:
        book.set_cover(coverfile.read())
    book.add_page('First page', 'Content of the first page.')
    book.add_page('Second page', 'Content of the second page.')
    book.add_page('Third page', 'Content of the third page.')
    book.save(str(file))
    assert file.exists()

