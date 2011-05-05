# Copyright (c) 2011, Roger Lew
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above
#     copyright notice, this list of conditions and the following
#     disclaimer in the documentation and/or other materials provided
#     with the distribution.
#   * Neither the name of the organizations affiliated with the
#     contributors or the names of its contributors themselves may be
#     used to endorse or promote products derived from this software
#     without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
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
print ' var:',cur.fetchone()[0],'(should be ~ 333,666.666)'

cur.execute("select skew(f) from test")
print 'skew:',cur.fetchone()[0],'(should be ~ 0.)'

cur.execute("select kurt(f) from test")
print 'kurt:',cur.fetchone()[0],'(should be ~ -1.2)'
