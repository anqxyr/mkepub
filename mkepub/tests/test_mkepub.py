#!/usr/bin/env python3
"""mkepub Test Suite."""

import epubcheck
import logging
import mkepub
import pathlib
import pytest

###############################################################################

logger = logging.getLogger('mkepub_test')
logging.basicConfig(
    filename='mkepub/tests/test.log', level=logging.ERROR, format=None)
logger.setLevel(logging.WARNING)


def save_and_check(book):
    name = 'mkepub/tests/{}.epub'.format(book.title.lower().replace(' ', '_'))
    path = pathlib.Path(name)
    if path.exists():
        path.unlink()
    book.save(str(path))
    r = epubcheck.EpubCheck(name)
    for m in r.messages:
        logger.warning('{0.level} {0.location}: {0.message}'.format(m))
    assert r.valid

###############################################################################


def test_book_simple():
    book = mkepub.Book(title='Simple')
    with open('mkepub/tests/cover.jpg', 'rb') as coverfile:
        book.set_cover(coverfile.read())
    book.add_page('Page 1', 'Content of the first page.')
    book.add_page('Page 2', 'Content of the second page.')
    save_and_check(book)


def test_exception_file_exists():
    book = mkepub.Book('Simple')
    with pytest.raises(FileExistsError):
        book.save('mkepub/tests/simple.epub')


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


def test_book_with_anchors():
    text = '''
    <h1 id="anchor-1">Anchor 1</h1> 
    <p> Text for anchor 1 </p>
    <h1 id="anchor-2">Anchor 2</h1>
    <p> Text for anchor 1 </p>
    '''
    book = mkepub.Book('Anchors')
    parent = book.add_page('Parent Page', '0000-0000')
    book.add_page('First Child', text, parent,
                  anchors=[('anchor-1', 'Anchor 1'), ('anchor-2', 'Anchor 2')])
    book.add_page('Third Child', text, parent,
                  anchors={'anchor-1': 'Anchor 1', 'anchor-2': 'Anchor 2'})
    save_and_check(book)


def test_book_with_images():
    book = mkepub.Book('Images')
    book.add_page('Cover Page', '<img src="images/cover.jpg"></img>')
    with open('mkepub/tests/cover.jpg', 'rb') as file:
        book.add_image('cover.jpg', file.read())
    save_and_check(book)


def test_unsupported_image_format():
    book = mkepub.Book('Untitled')
    book.add_image('bad_image.bmp', b'')
    with pytest.raises(ValueError):
        save_and_check(book)
