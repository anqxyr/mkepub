#!/usr/bin/env python3

"""
Create Epub files.

This code was designed to provide a very simple and straight-forward API for
creating epub files, by sacrificing most of the versatility of the format.
"""

###############################################################################
# Module Imports
###############################################################################

import collections
import datetime
import imghdr
import itertools
import jinja2
import pathlib
import tempfile
import uuid
import zipfile


###############################################################################

def mediatype(name):
    ext = name.split('.')[-1].lower()
    if ext not in ('png', 'jpg', 'jpeg', 'gif', 'svg'):
        raise ValueError('Image format "{}" is not supported.'.format(ext))
    if ext == 'jpg':
        ext = 'jpeg'
    return 'image/' + ext


env = jinja2.Environment(loader=jinja2.PackageLoader('mkepub'))
env.filters['mediatype'] = mediatype

###############################################################################

Page = collections.namedtuple('Page', 'page_id title children')
Image = collections.namedtuple('Image', 'image_id name')


class Book:
    """EPUB book."""

    def __init__(self, title, **metadata):
        """"Create new book."""
        self.title = title
        self.metadata = metadata

        self.tempdir = tempfile.TemporaryDirectory()
        self.root = []
        self.images = []
        self.uuid = uuid.uuid4()
        self._page_id = map('{:04}'.format, itertools.count(1))
        self._image_id = map('{:03}'.format, itertools.count(1))

        self.path = pathlib.Path(self.tempdir.name).resolve()
        for dirname in [
                'EPUB', 'META-INF', 'EPUB/images', 'EPUB/css', 'EPUB/covers']:
            (self.path / dirname).mkdir()

        self.set_stylesheet('')
        self._cover = None

    ###########################################################################
    # Public Methods
    ###########################################################################

    def add_page(self, title, content, parent=None):
        """
        Add a new page.

        The page will be added as a subpage of the parent. If no parent is
        provided, the page will be added to the root of the book.
        """
        page = Page(next(self._page_id), title, [])
        self.root.append(page) if not parent else parent.children.append(page)
        self._write_page(page, content)
        return page

    def add_image(self, name, data):
        """Add image file."""
        self.images.append(Image(next(self._image_id), name))
        with open(str(self.path / 'EPUB/images' / name), 'wb') as file:
            file.write(data)

    def set_cover(self, data):
        """Set the cover image to the given data."""
        self._cover = 'cover.' + imghdr.what(None, h=data)
        with open(str(self.path / 'EPUB/covers' / self._cover), 'wb') as file:
            file.write(data)
        self._write('cover.xhtml', 'EPUB/cover.xhtml', cover=self._cover)

    def set_stylesheet(self, data):
        """Set the stylesheet to the given css data."""
        with open(str(self.path / 'EPUB/css/stylesheet.css'), 'w') as file:
            file.write(data)

    def save(self, filename):
        """Save book to a file."""
        if pathlib.Path(filename).exists():
            raise FileExistsError
        self._write_spine()
        self._write('container.xml', 'META-INF/container.xml')
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

    ###########################################################################
    # Private Methods
    ###########################################################################

    def _write(self, template, path, **data):
        with open(str(self.path / path), 'w') as file:
            file.write(env.get_template(template).render(**data))

    def _write_page(self, page, content):
        """Write the contents of the page into an html file."""
        self._write(
            'page.xhtml', 'EPUB/page{}.xhtml'.format(page.page_id),
            title=page.title, body=content)

    def _write_spine(self):
        self._write(
            'package.opf', 'EPUB/package.opf',
            title=self.title,
            date=datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
            pages=list(self._flatten(self.root)), images=self.images,
            uuid=self.uuid, cover=self._cover,
            **self.metadata)

    def _write_toc(self):
        self._write(
            'toc.xhtml', 'EPUB/toc.xhtml', pages=self.root, title=self.title)
        self._write(
            'toc.ncx', 'EPUB/toc.ncx',
            pages=self.root, title=self.title, uuid=self.uuid)

    def _flatten(self, tree):
        for item in tree:
            yield item
            yield from self._flatten(item.children)
