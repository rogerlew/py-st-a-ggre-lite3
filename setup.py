# Copyright (c) 2011, Roger Lew [see LICENSE.txt]
# This software is funded in part by NIH Grant P20 RR016454.

##from distutils.core import setup
from setuptools import setup

setup(name='pystaggrelite3',
    version='0.1.3',
    description='Pure Python sqlite3 statistics aggregate functions',
    author='Roger Lew',
    author_email='rogerlew@gmail.com',
    license = "BSD",
    classifiers=["Development Status :: 5 - Production/Stable",
                 "Intended Audience :: Developers",
                 "License :: OSI Approved :: BSD License",
                 "Natural Language :: English",
                 "Programming Language :: Python :: 2.5",
                 "Programming Language :: Python :: 2.6",
                 "Programming Language :: Python :: 2.7",
                 "Programming Language :: Python :: 3",
                 "Programming Language :: Python :: 3.0",
                 "Programming Language :: Python :: 3.1",
                 "Programming Language :: Python :: 3.2",
                 "Topic :: Database",
                 "Topic :: Database :: Database Engines/Servers",
                 "Topic :: Scientific/Engineering :: Information Analysis",
                 "Topic :: Scientific/Engineering :: Mathematics",
                 "Topic :: Software Development :: Libraries :: Python Modules"],
    url='http://code.google.com/p/py-st-a-ggre-lite3/',
    py_modules=['pystaggrelite3',],
)

"""setup.py sdist upload --identity="Roger Lew" --sign"""
