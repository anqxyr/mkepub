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


def test_book_no_cover():
    book = mkepub.Book(title='No Cover Test')
    book.add_page('Page Only', 'This is all the text.')
    book.save('nocover.epub')

    subprocess.check_output(['epubcheck', 'nocover.epub'])


def test_book_one_author():
    book = mkepub.Book(title='Whatever', author='This Guy')
    book.add_page('Page 1', 'text text. text.')
    book.save('one_author.epub')

    subprocess.check_output(['epubcheck', 'one_author.epub'])


def test_book_multiple_authors():
    book = mkepub.Book(
        title='Still Whatever', authors=['This Guy', 'Some Other Guy'])
    book.add_page('Page 1', 'text text. text.')
    book.save('multiple_authors.epub')

    subprocess.check_output(['epubcheck', 'multiple_authors.epub'])


def test_book_nested():
    book = mkepub.Book('Nested')
    parent = book.add_page('Parent Page', '0000-0000')
    book.add_page('First Child', 'ヽ(。_°)ノ', parent)
    second_child = book.add_page('Second Child', 'blop', parent)
    book.add_page('Grandkid', 'ooOOoo', second_child)
    book.save('nested.epub')

    subprocess.check_output(['epubcheck', 'nested.epub'])



