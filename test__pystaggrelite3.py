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
This unittests the pure python aggregate functions
defined in the stat_aggregate_funcs module.
"""

import unittest
import sqlite3 as sqlite
import new

import pystaggrelite3
from pystaggrelite3 import isfloat



class aggTests(unittest.TestCase):
    """
    this is a generic class for testing the user defined aggregators
    """
    
    def setUp(self):
        # create an sqlite table
        self.con = sqlite.connect(":memory:")
        cur = self.con.cursor()
        cur.execute("""
            create table test(
                t text,
                i integer,
                f float,
                neg float,
                empty float,
                hasnan float,
                hasinf float,
                modefive float,
                n,
                b blob
                )
            """)

        # add data to table
        # data = [ 1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9, 
        #          10.10, 11.11, 12.12, 13.13, 14.14 ]
        cur.executemany("insert into test(t) values (?)",
                        [('%i.%i'%(i,i),) for i in xrange(1,15)])
        
        cur.executemany("insert into test(f) values (?)",
                        [('%i.%i'%(i,i),) for i in xrange(1,15)])
        
        cur.executemany("insert into test(neg) values (?)",
                        [('-%i.%i'%(i,i),) for i in xrange(1,15)])
        
        cur.executemany("insert into test(hasnan) values (?)",
                        [('%i.%i'%(i,i),) for i in xrange(1,7)]+\
                        [('NaN',)]+\
                        [('%i.%i'%(i,i),) for i in xrange(8,15)])
        
        cur.executemany("insert into test(hasinf) values (?)",
                        [('%i.%i'%(i,i),) for i in xrange(1,7)]+\
                        [('Inf',)]+\
                        [('%i.%i'%(i,i),) for i in xrange(8,15)])
        
        cur.executemany("insert into test(modefive) values (?)",
                        [('%i'%i,) for i in xrange(1,6)]+\
                        [('5',)]+\
                        [('%i'%i,) for i in xrange(5,15)])

        # register user defined aggregate with sqlite
        self.con.create_aggregate(self.name, 1, self.aggregate)

    def tearDown(self):
        #self.cur.close()
        #self.con.close()
        pass

    def Check_float(self):
        """check how aggregate handles float data"""
        cur = self.con.cursor()
        cur.execute("select %s(f) from test"%self.name)
        val = cur.fetchone()[0]
        
        if isfloat(val) and isfloat(self.expect_float):
            self.failUnlessAlmostEqual(val, self.expect_float, 6)
        else:
            self.failUnlessEqual(val, self.expect_float)

    def Check_neg(self):
        """check how aggregate handles negative float data"""
        cur = self.con.cursor()
        cur.execute("select %s(neg) from test"%self.name)
        val = cur.fetchone()[0]
        
        if isfloat(val) and isfloat(self.expect_neg):
            self.failUnlessAlmostEqual(val, self.expect_neg, 6)
        else:
            self.failUnlessEqual(val, self.expect_neg)
            
    def Check_text(self):
        """check how aggregate handles text data"""
        cur = self.con.cursor()
        cur.execute("select %s(t) from test"%self.name)
        val = cur.fetchone()[0]
        
        if isfloat(val) and isfloat(self.expect_float):
            self.failUnlessAlmostEqual(val, self.expect_text, 6)
        else:
            self.failUnlessEqual(val, self.expect_text)
        
    def Check_empty(self):
        """check how aggregate handles an empty list"""
        cur = self.con.cursor()
        cur.execute("select %s(empty) from test"%self.name)
        val = cur.fetchone()[0]
        
        if isfloat(val) and isfloat(self.expect_float):
            self.failUnlessAlmostEqual(val, self.expect_empty, 6)
        else:
            self.failUnlessEqual(val, self.expect_empty)

    def Check_nan(self):
        """check how aggregate handles float data containing nan values"""
        cur = self.con.cursor()
        cur.execute("select %s(hasnan) from test"%self.name)
        val = cur.fetchone()[0]
        
        if isfloat(val) and isfloat(self.expect_float):
            self.failUnlessAlmostEqual(val, self.expect_nan, 6)
        else:
            self.failUnlessEqual(val, self.expect_nan)

    def Check_inf(self):
        """check how aggregate handles float data containing inf values"""
        cur = self.con.cursor()
        cur.execute("select %s(hasinf) from test"%self.name)
        val = cur.fetchone()[0]
        
        if isfloat(val) and isfloat(self.expect_float):
            self.failUnlessAlmostEqual(val, self.expect_inf, 6)
        else:
            self.failUnlessEqual(val, self.expect_inf)

    def Check_modefive(self):
        """special func to check mode aggregate"""

        if hasattr(self,'expect_modefive'):
            cur = self.con.cursor()
            cur.execute("select %s(modefive) from test"%self.name)
            val = cur.fetchone()[0]
            
            if isfloat(val) and isfloat(self.expect_modefive):
                self.failUnlessAlmostEqual(val, self.expect_modefive, 6)
            else:
                self.failUnlessEqual(val, self.expect_modefive)

# Here a test class is defined for each aggregator as a metaclass

hasnanTests=\
    new.classobj('hasnanTests',(aggTests,),
                 { 'name':'kurt',
                   'aggregate':pystaggrelite3.hasnan,
                   'expect_float':False,
                   'expect_neg':False,
                   'expect_text':False,
                   'expect_empty':False,
                   'expect_nan':True,
                   'expect_inf':False
                 }
                )

hasinfTests=\
    new.classobj('hasinfTests',(aggTests,),
                 { 'name':'kurt',
                   'aggregate':pystaggrelite3.hasinf,
                   'expect_float':False,
                   'expect_neg':False,
                   'expect_text':False,
                   'expect_empty':False,
                   'expect_nan':False,
                   'expect_inf':True
                 }
                )

arbitraryTests=\
    new.classobj('arbitraryTests',(aggTests,),
                 { 'name':'arbitrary',
                   'aggregate':pystaggrelite3.arbitrary,
                   'expect_float':1.1,
                   'expect_neg':-1.1,
                   'expect_text':u'1.1',
                   'expect_empty':None,
                   'expect_nan':1.1,
                   'expect_inf':1.1
                  }
                 )

datarangeTests=\
    new.classobj('datarangeTests',(aggTests,),
                 {'name':'datarange',
                  'aggregate':pystaggrelite3.datarange,
                  'expect_float':13.040000000000001,
                   'expect_neg':13.040000000000001,
                  'expect_text':13.040000000000001,
                  'expect_empty':None,
                  'expect_nan':13.040000000000001,
                  'expect_inf':float('inf')
                 }
                )

abs_meanTests=\
    new.classobj('abs_meanTests',(aggTests,),
                 {'name':'abs_mean',
                  'aggregate':pystaggrelite3.abs_mean,
                  'expect_float':7.864285714285715,
                   'expect_neg':7.864285714285715,
                  'expect_text':7.864285714285715,
                  'expect_empty':None,
                  'expect_nan':7.876923076923077,
                  'expect_inf':float('inf')
                 }
                )

geometric_meanTests=\
    new.classobj('geometric_meanTests',(aggTests,),
                 {'name':'geometric_mean',
                  'aggregate':pystaggrelite3.geometric_mean,
                  'expect_float':6.450756824711689,
                  'expect_neg':None,
                  'expect_text':6.450756824711689,
                  'expect_empty':None,
                  'expect_nan':6.363511307721573,
                  'expect_inf':float('inf')
                 }
                )

medianTests=\
    new.classobj('medianTests',(aggTests,),
                 {'name':'median',
                  'aggregate':pystaggrelite3.median,
                  'expect_float':8.25,
                   'expect_neg':-8.25,
                  'expect_text':8.25,
                  'expect_empty':None,
                  'expect_nan':8.8,
                  'expect_inf':9.350000000000001,
                  'expect_modefive':6.5
                 }
                )

modeTests=\
    new.classobj('modeTests',(aggTests,),
                 { 'name':'mode',
                   'aggregate':pystaggrelite3.mode,
                   'expect_float':5.5,
                   'expect_neg':-5.5,
                   'expect_text':5.5,
                   'expect_empty':None,
                   'expect_nan':5.5,
                   'expect_inf':5.5,
                   'expect_modefive':5.0
                 }
                )

varpTests=\
    new.classobj('varpTests',(aggTests,),
                 { 'name':'varp',
                   'aggregate':pystaggrelite3.varp,
                   'expect_float':15.976081632653049,
                   'expect_neg':15.976081632653049,
                   'expect_text':15.976081632653049,
                   'expect_empty':None,
                   'expect_nan':17.20277514792899 ,
                   'expect_inf':None
                 }
                )

varTests=\
    new.classobj('varTests',(aggTests,),
                 { 'name':'var',
                   'aggregate':pystaggrelite3.var,
                   'expect_float':17.205010989010976,
                   'expect_neg':17.205010989010976,
                   'expect_text':17.205010989010976,
                   'expect_empty':None,
                   'expect_nan':18.636339743589737,
                   'expect_inf':None
                 }
                )

stdevpTests=\
    new.classobj('stdevpTests',(aggTests,),
                 { 'name':'stdevp',
                   'aggregate':pystaggrelite3.stdevp,
                   'expect_float':3.9970090858857263,
                   'expect_neg':3.9970090858857263,
                   'expect_text':3.9970090858857263,
                   'expect_empty':None,
                   'expect_nan':4.147622830963417,
                   'expect_inf':None
                 }
                )

stdevTests=\
    new.classobj('stdevTests',(aggTests,),
                 { 'name':'stdev',
                   'aggregate':pystaggrelite3.stdev,
                   'expect_float':4.14789235504141,
                   'expect_neg':4.14789235504141,
                   'expect_text':4.14789235504141,
                   'expect_empty':None,
                   'expect_nan':4.316982712913006,
                   'expect_inf':None
                 }
                )

semTests=\
    new.classobj('semTests',(aggTests,),
                 { 'name':'sem',
                   'aggregate':pystaggrelite3.sem,
                   'expect_float':1.108570862127418,
                   'expect_neg':1.108570862127418,
                   'expect_text':1.108570862127418,
                   'expect_empty':None,
                   'expect_nan':1.1973155789768832,
                   'expect_inf':None
                 }
                )

ciTests=\
    new.classobj('ciTests',(aggTests,),
                 { 'name':'ci',
                   'aggregate':pystaggrelite3.ci,
                   'expect_float':2.1727988897697394,
                   'expect_neg':2.1727988897697394,
                   'expect_text':2.1727988897697394,
                   'expect_empty':None,
                   'expect_nan':2.3467385347946914,
                   'expect_inf':None
                 }
                )

rmsTests=\
    new.classobj('rmsTests',(aggTests,),
                 { 'name':'rms',
                   'aggregate':pystaggrelite3.rms,
                   'expect_float':8.821738571765286,
                   'expect_neg':8.821738571765286,
                   'expect_text':8.821738571765286,
                   'expect_empty':None,
                   'expect_nan':8.902173459762077,
                   'expect_inf':float('inf')
                 }
                )

prodTests=\
    new.classobj('prodTests',(aggTests,),
                 { 'name':'prod',
                   'aggregate':pystaggrelite3.prod,
                   'expect_float':216047570729.97736,
                   'expect_neg':216047570729.97736,
                   'expect_text':216047570729.97736,
                   'expect_empty':None,
                   'expect_nan':28058126068.82824,
                   'expect_inf':float('inf')
                 }
                )

skewTests=\
    new.classobj('skewTests',(aggTests,),
                 { 'name':'skew',
                   'aggregate':pystaggrelite3.skew,
                   'expect_float':-0.1322935682076316,
                   'expect_neg':0.1322935682076316,
                   'expect_text':-0.1322935682076316,
                   'expect_empty':None,
                   'expect_nan':-0.13664205273197477,
                   'expect_inf':None
                 }
                )

kurtTests=\
    new.classobj('kurtTests',(aggTests,),
                 { 'name':'kurt',
                   'aggregate':pystaggrelite3.kurt,
                   'expect_float':-1.1706824430972933,
                   'expect_neg':-1.1706824430972933,
                   'expect_text':-1.1706824430972933,
                   'expect_empty':None,
                   'expect_nan':-1.2992969632487026,
                   'expect_inf':None
                 }
                )

def suite():
    return unittest.TestSuite((
               unittest.makeSuite(hasnanTests,         "Check"),
               unittest.makeSuite(hasinfTests,         "Check"),
               unittest.makeSuite(arbitraryTests,      "Check"),
               unittest.makeSuite(varpTests,           "Check"),
               unittest.makeSuite(varTests,            "Check"),
               unittest.makeSuite(stdevpTests,         "Check"),
               unittest.makeSuite(stdevTests,          "Check"),
               unittest.makeSuite(semTests,            "Check"),
               unittest.makeSuite(ciTests,             "Check"),
               unittest.makeSuite(rmsTests,            "Check"),
               unittest.makeSuite(prodTests,           "Check"),
               unittest.makeSuite(skewTests,           "Check"),
               unittest.makeSuite(kurtTests,           "Check"),
               unittest.makeSuite(datarangeTests,      "Check"),
               unittest.makeSuite(abs_meanTests,       "Check"),
               unittest.makeSuite(geometric_meanTests, "Check"),
               unittest.makeSuite(modeTests,           "Check"),
               unittest.makeSuite(medianTests,         "Check")
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
