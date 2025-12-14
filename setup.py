import setuptools

with open('README.rst') as f:
    readme = f.read()

setuptools.setup(
    name='mkepub',
    version='1.2',
    description='Simple minimalistic library for creating EPUB3 files',
    long_description=readme,
    url='https://github.com/anqxyr/mkepub/',
    author='anqxyr',
    author_email='anqxyr@gmail.com',
    license='MIT',
    keywords='epub epub3',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13'],
    python_requires='>=3.10',
    packages=['mkepub'],
    package_data={'mkepub': ['templates/*']},
    tests_require=['epubcheck', 'pytest', 'pytest-cov', 'python-coveralls'],
    install_requires=['jinja2'],
)
