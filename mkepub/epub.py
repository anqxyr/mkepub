#!/usr/bin/env python3

"""
Create Epub files.

This code was designed to provide a very simple and straight-forward API for
creating epub files, by sacrificing most of the versatility of the format.

Example usage:

>>> book = Book(title='Example Book', author='John Doe')
>>> with open('cover.png', 'br') as file:
>>>     book.add_cover(file.read())
>>> with open('style.css') as file:
>>>     book.add_stylesheet(file.read())
>>> book.add_page(title='First Page', content='some text')
>>> chapter = book.add_page(title='First Chapter', content='more text')
>>> book.add_page(
>>>     title='Sub-Page 1',
>>>     content='first subpage of the chapter',
>>>     parent=chapter)
>>> with open('image.jpg', 'br') as file:
>>>     book.add_image('image.jpg', file.read())
>>> book.save('example.epub')

"""

###############################################################################
# Module Imports
###############################################################################

import arrow
import collections
import itertools
import logging
import lxml.etree
import lxml.html
import pathlib
import pkgutil
import tempfile
import uuid
import zipfile

###############################################################################

log = logging.getLogger(__name__)

###############################################################################

Page = collections.namedtuple('Page', 'uid title children')
Image = collections.namedtuple('Image', 'name type')


class Book:
    """EPUB book."""

    def __init__(self, **kwargs):
        """"Create new book."""
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = []
        self.images = []
        self.uid_generator = map('{:04}'.format, itertools.count(1))

        self.path = pathlib.Path(self.tempdir.name).resolve()
        (self.path / 'pages').mkdir()
        (self.path / 'images').mkdir()

        self.title = kwargs.get('title', 'Untitled')
        self.language = kwargs.get('language', 'en')
        self.author = kwargs.get('author', 'Unknown Author')

    ###########################################################################
    # Public Methods
    ###########################################################################

    def add_page(self, title, content, parent=None):
        """
        Add a new page.

        The page will be added as a subpage of the parent. If no parent is
        provided, the page will be added to the root of the book.
        """
        log.info('New page: {}'.format(title))
        page = Page(next(self.uid_generator), title, [])
        self.root.append(page) if not parent else parent.children.append(page)
        self._write_page(page.uid, title, content)
        return page

    def add_image(self, name, data):
        """Add image file."""
        log.info('New image: {}'.format(name))
        if name.endswith('.jpg'):
            media_type = 'image/jpeg'
        if name.endswith('.png'):
            media_type = 'image/png'
        self.images.append(Image(name, media_type))
        with open(str(self.path / 'images' / name), 'wb') as file:
            file.write(data)

    def set_cover(self, data):
        """Set the cover image to the given png data."""
        with open(str(self.path / 'cover.png'), 'wb') as file:
            file.write(data)

    def set_stylesheet(self, data):
        """Set the stylesheet to the given css data."""
        with open(str(self.path / 'stylesheet.css'), 'w') as file:
            file.write(data)

    def save(self, filename):
        """Save book to a file."""
        self._write_spine()
        self._write_container()
        self._write_toc()
        with open(str(self.path / 'mimetype'), 'w') as file:
            file.write('application/epub+zip')
        with zipfile.ZipFile(filename, 'w') as archive:
            archive.write(
                str(self.path / 'mimetype'), 'mimetype',
                compress_type=zipfile.ZIP_STORED)
            for file in self.path.rglob('*.*'):
                archive.write(
                    str(file), str(file.relative_to(self.path)),
                    compress_type=zipfile.ZIP_DEFLATED)
        log.info('Book saved: {}'.format(self.title))

    ###########################################################################
    # Private Methods
    ###########################################################################

    def _write_page(self, uid, title, content):
        """Write the contents of the page into an xhtml file."""
        xmltree = _template('page.xhtml')
        xmltree('xhtml:title').text = title
        xmltree('xhtml:body').append(lxml.html.fromstring(content))
        xmltree.write(self.path / 'pages' / (uid + '.xhtml'))

    def _write_spine(self):
        spine = _template('content.opf')
        now = arrow.utcnow().format('YYYY-MM-DDTHH:mm:ss')
        spine(property='dcterms:modified').text = now
        spine('dc:date').text = now
        spine('dc:title').text = self.title
        spine('dc:creator').text = self.author
        spine('dc:language').text = self.language
        spine(id='uuid_id').text = str(uuid.uuid4())

        for page in _flatten(self.root):
            _add_node(
                spine('opf:manifest'),
                'item',
                href='pages/{}.xhtml'.format(page.uid),
                id=page.uid,
                mediatype='application/xhtml+xml')
            _add_node(spine('opf:spine'), 'itemref', idref=page.uid)

        for uid, image in enumerate(self.images):
            _add_node(
                spine('opf:manifest'),
                'item',
                href='images/' + image.name,
                id='img{:03}'.format(uid + 1),
                mediatype=image.type)

        spine.write(self.path / 'content.opf')

    def _write_container(self):
        container = _template('container.xml')
        meta_inf = self.path / 'META-INF'
        meta_inf.mkdir()
        container.write(meta_inf / 'container.xml')

    def _write_toc(self):
        toc = _template('toc.ncx')
        toc('ncx:text').text = self.title
        for page in self.root:
            self._page_to_toc(page, toc('ncx:navMap'))
        toc.write(self.path / 'toc.ncx')

    def _page_to_toc(self, page, node):
        navpoint = _add_node(
            node, 'navPoint', id=page.uid, playOrder=page.uid.lstrip('0'))
        navlabel = _add_node(navpoint, 'navLabel')
        _add_node(navlabel, 'text').text = page.title
        _add_node(navpoint, 'content', src='pages/{}.xhtml'.format(page.uid))
        for child in page.children:
            self._page_to_toc(child, navpoint)


###############################################################################
# Helper Classes and Methods
###############################################################################


class _ETreeWrapper:
    """Convinience wrapper around xml trees."""

    def __init__(self, *args, namespaces, **kwargs):
        self.tree = lxml.etree.ElementTree(*args, **kwargs)
        self.namespaces = namespaces

    def __call__(self, tag='*', **kwargs):
        path = './/{}'.format(tag)
        for key, value in kwargs.items():
            path += '[@{}="{}"]'.format(key, value)
        return self.tree.find(path, namespaces=self.namespaces)

    def __getattr__(self, name):
        return getattr(self.tree, name)

    def write(self, path):
        self.tree.write(str(path), xml_declaration=True,
                        encoding='UTF-8', pretty_print=True)


def _add_node(*args, **kwargs):
    """
    Add new xml node.

    Wrapper around lxml.etree.SubElement, for better readability.
    """
    if 'mediatype' in kwargs:
        kwargs['media-type'] = kwargs.pop('mediatype')
    return lxml.etree.SubElement(*args, **kwargs)


def _template(name):
    """Get file template."""
    return _ETreeWrapper(
        lxml.etree.fromstring(
            pkgutil.get_data('mkepub', 'resources/' + name),
            lxml.etree.XMLParser(remove_blank_text=True)),
        namespaces=dict(
            opf='http://www.idpf.org/2007/opf',
            dc='http://purl.org/dc/elements/1.1/',
            xhtml='http://www.w3.org/1999/xhtml',
            ncx='http://www.daisy.org/z3986/2005/ncx/'))


def _flatten(tree):
    for item in tree:
        yield item
        yield from _flatten(item.children)
