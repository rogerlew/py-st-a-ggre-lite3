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

import sqlite3
import random

import pystaggrelite3
import madis_statistics

"""
function         pystaggrelite3 madis
varp             16.558735      17.7806623929
stdevp           16.564954      17.7071257728
mode             19.239616      49.0906918286
median           17.445850      18.5950308343
datarange        14.877920      16.1017565178
geometric_mean   16.798725      17.1868062916
"""

def aggregate_tester(func):

    con = sqlite3.connect(":memory:")

    con.create_aggregate("func", 1, func)

    cur = con.cursor()
    cur.execute("create table test(f)")

    for i in xrange(1000000):
        cur.execute("insert into test(f) values (?)",
                    (random.uniform(1.,1000.),))


    cur.execute("select func(f) from test")
    cur.fetchone()[0]
    
if __name__=='__main__':
    from timeit import Timer
    num=1

    testlist=[
                'pystaggrelite3.varp',          'madis_statistics.variance',
                'pystaggrelite3.stdevp',        'madis_statistics.sdev',
                'pystaggrelite3.mode',          'madis_statistics.modeop',
                'pystaggrelite3.median',        'madis_statistics.median',
                'pystaggrelite3.datarange',     'madis_statistics.rangef',
                'pystaggrelite3.geometric_mean','madis_statistics.gmean'
              ]


    print 'function'.ljust(16),'pystaggrelite3\tmadis'
    
    for test in testlist:
        
        t = Timer("aggregate_tester(%s)"%test,
                  "from __main__ import aggregate_tester,%s"%test.split('.')[0])

        ctime=t.timeit(number=num)

        if 'pystaggrelite3' in test:
            print test.split('.')[1].ljust(16),'%f\t'%ctime,
        else:
            print ctime

