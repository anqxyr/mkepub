#!/usr/bin/env python3
"""mkepub Test Suite."""

import mkepub
import pathlib
import subprocess

###############################################################################

if not pathlib.Path('test_output/').exists():
    pathlib.Path('test_output/').mkdir()


def save_and_check(book):
    name = 'test_output/{}.epub'.format(book.title.lower().replace(' ', '_'))
    book.save(name)
    subprocess.check_output(['epubcheck', name])


def test_book_simple():
    book = mkepub.Book(title='Simple')
    with open('cover.jpg', 'rb') as coverfile:
        book.set_cover(coverfile.read())
    book.add_page('Page 1', 'Content of the first page.')
    book.add_page('Page 2', 'Content of the second page.')
    save_and_check(book)


def test_book_no_cover():
    book = mkepub.Book(title='No Cover')
    book.add_page('Page Only', 'This is all the text.')
    save_and_check(book)


def test_book_one_author():
    book = mkepub.Book(title='One Author', author='This Guy')
    book.add_page('Page 1', 'text text. text.')
    save_and_check(book)


def test_book_multiple_authors():
    book = mkepub.Book(
        title='Multiple Authors', authors=['This Guy', 'Some Other Guy'])
    book.add_page('Page 1', 'text text. text.')
    save_and_check(book)


def test_book_nested():
    book = mkepub.Book('Nested')
    parent = book.add_page('Parent Page', '0000-0000')
    book.add_page('First Child', 'ヽ(。_°)ノ', parent)
    second_child = book.add_page('Second Child', 'blop', parent)
    book.add_page('Grandkid', 'ooOOoo', second_child)
    save_and_check(book)
