import setuptools

with open('README.rst') as f:
    readme = f.read()

setuptools.setup(
    name='mkepub',
    version='1.1',
    description='Simple minimalistic library for creating EPUB3 files',
    long_description=readme,
    url='https://github.com/anqxyr/mkepub/',
    author='anqxyr',
    author_email='anqxyr@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'],
    packages=['mkepub'],
    package_data={'mkepub': ['templates/*']},
    tests_require=['epubcheck', 'pytest', 'pytest-cov', 'python-coveralls'],
    install_requires=['jinja2'],
)
