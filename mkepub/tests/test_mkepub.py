#!/usr/bin/env python3
"""mkepub Test Suite."""

import epubcheck
import logging
import mkepub
import pathlib
import pytest
from zipfile import ZipFile

###############################################################################

logger = logging.getLogger('mkepub_test')
logging.basicConfig(
    filename='mkepub/tests/test.log', level=logging.ERROR, format=None)
logger.setLevel(logging.WARNING)


def name_for_book(book):
    return 'mkepub/tests/{}.epub'.format(book.title.lower().replace(' ', '_'))


def save_and_check(book):
    name = name_for_book(book)
    path = pathlib.Path(name)
    if path.exists():
        path.unlink()
    book.save(str(path))
    r = epubcheck.EpubCheck(name)
    for m in r.messages:
        logger.warning('{0.level} {0.location}: {0.message}'.format(m))
    assert r.valid


def assert_has_contents(book, file, expected_strings):
    name = name_for_book(book)
    zipfile = ZipFile(name, 'r')
    contents = zipfile.read(file)
    for expected_string in expected_strings:
        assert bytes(expected_string, 'utf-8') in contents

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


def test_book_with_font():
    book = mkepub.Book('Font')
    book.add_page('Page 1', 'Content')
    with open('mkepub/tests/LinBiolinum_K.woff', 'rb') as file:
        book.add_font('LinBiolinum_K.woff', file.read())
    book.set_stylesheet("""@font-face {
        font-family: "biolinum";
        src: url(../fonts/LinBiolinum_K.woff);}""")
    save_and_check(book)


def test_add_file():
    book = mkepub.Book('File')
    assert not (book.path / 'files').exists()
    with open('mkepub/tests/cover.jpg', 'rb') as file:
        book._add_file('files/cover_1.jpg', file.read())
    assert (book.path / 'EPUB/files/cover_1.jpg').exists()


def test_book_with_dcterms():
    book = mkepub.Book('DCTerms', dcterms={'available': '5', 'audience': 'everyone'})
    book.add_page('Page 1', 'Content')
    save_and_check(book)

    expected_strings = [
        '<meta property="dcterms:available">5</meta>\n',
        '<meta property="dcterms:audience">everyone</meta>\n'
    ]
    assert_has_contents(book, 'EPUB/package.opf', expected_strings)

    
def test_mediatype():
    assert mkepub.mkepub.mediatype('file.png') == 'image/png'
    assert mkepub.mkepub.mediatype('file.jpg') == 'image/jpeg'
    assert mkepub.mkepub.mediatype('file.jpeg') == 'image/jpeg'
    assert mkepub.mkepub.mediatype('file.gif') == 'image/gif'
    assert mkepub.mkepub.mediatype('file.svg') == 'image/svg+xml'


def test_cover_from_file():
    book = mkepub.Book('Cover from file')
    cover_file = 'mkepub/tests/cover.jpg'
    book.set_cover_from_file(cover_file)
    book.add_page('A single page', 'With some text.')
    save_and_check(book)


def test_font_from_file():
    book = mkepub.Book('Font from file')
    book.add_page('Page 1', 'Content')
    font_file = 'mkepub/tests/LinBiolinum_K.woff'
    book.add_font_from_file(font_file)
    book.set_stylesheet("""@font-face {
            font-family: "biolinum";
            src: url(../fonts/LinBiolinum_K.woff);}""")
    save_and_check(book)


def test_stylesheet_from_file():
    book = mkepub.Book('Stylesheet from file')
    book.add_page('Page 1', 'Content')
    style_file = 'mkepub/tests/stylesheet.css'
    book.set_stylesheet_from_file(style_file)
    save_and_check(book)