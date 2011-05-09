# Copyright (c) 2011, Roger Lew
# This software is funded in part by NIH Grant P20 RR016454.

"""
Simple example for interfacing pystaggrelite3 with sqlite3

For more information on using sqlite3 with python see:
    http://docs.python.org/library/sqlite3.html
"""

import sqlite3
import random

import pystaggrelite3

con = sqlite3.connect(":memory:")


con.create_aggregate("var", 1, pystaggrelite3.var)
con.create_aggregate("skew", 1, pystaggrelite3.skew)
con.create_aggregate("kurt", 1, pystaggrelite3.kurt)

cur = con.cursor()
cur.execute("create table test(f)")

for i in xrange(10000):
    cur.execute("insert into test(f) values (?)",
                (random.uniform(-1000.,1000.),))


cur.execute("select var(f) from test")
print 'var: ',cur.fetchone()[0],'(should be ~ 333,666.666)'

cur.execute("select skew(f) from test")
print 'skew:',cur.fetchone()[0],'(should be ~ 0.)'

cur.execute("select kurt(f) from test")
print 'kurt:',cur.fetchone()[0],'(should be ~ -1.2)'
