#!/usr/bin/env python3
"""mkepub Test Suite."""

import pathlib

import mkepub


def test_empty_book():
    """
    Test creation of an empty book.

    This test is only to make sure that no exceptions are raised during
    the creation of the book, and that a file exists afterward. It does not
    check the contents of the file.
    """
    file = pathlib.Path('test.epub')
    if file.exists():
        file.unlink()
    book = mkepub.Book()
    book.add_page('-', '-')
    book.save(str(file))
    assert file.exists()


def test_page_add():
    """Test addition of a page to the book."""
    book = mkepub.Book()
    page = book.add_page('-', '-')
    path = book.path / 'pages' / (page.uid + '.xhtml')
    assert path.exists()


def test_page_add_child():
    """Test child pages."""
    book = mkepub.Book()
    parent = book.add_page('-', '-')
    child = book.add_page('-', '-', parent)
    assert child in parent.children
