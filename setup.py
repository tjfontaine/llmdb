import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "llmdb",
    version = "0.0.1",
    author = "Timothy J Fontaine",
    author_email = "tjfontaine@gmail.com",
    description = ("Shell Pipeline REPL for Debugging with LLDB"),
    license = "MIT",
    keywords = "lldb mdb debugging repl",
    url = "http://github.com/tjfontaine/llmdb",
    packages=['llmdb', 'llmdb.builtins'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
    scripts=['bin/llmdb'],
    install_requires=['funcy'],
)
