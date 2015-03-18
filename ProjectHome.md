## General Description ##
> The increasing complexity of scientific datasets provide increasing neccesity for integrating mature database technologies with scientific programming. Python and [sqlite3](http://docs.python.org/library/sqlite3.html) provides a fast means of accessing and filtering tabulated data. While the built-in sqlite3 aggregators are fast they are somewhat limited in that they only provide: avg, count, group\_concat, max, min, sum, and total.

> This project provides a extends this collection with user-defined statistical aggregate functions (coded in pure python) for sqlite3. All aggregates except for mode and median are implemented using running calculations to improve performance and conserve memory. (Still slower then the built-in sqlite methods, but faster compared to appending and using numpy functions in `finalize`). Unit testing is performed with `unittest`. `TestCase` classes are implemented as metaclasses to test aggregates over a collection of test cases.

> The running variance estimates (and estimates based on variance) are calculated using B.P. Welford's 1962 method. More details can be found here: [Accurately computing running variance](http://www.johndcook.com/standard_deviation.html)

> The project described was supported by NIH Grant Number P20 RR016454 from the INBRE Program of the National Center for Research Resources.

---

> ### Table of Contents ###
> 

---

## Requirements ##
> Tested with Python 2.7 or greater. The mode aggregate class uses collections which was introduced in 2.7. It is also Python 3 compatible (tested with 3.2, 64-bit). If you use it with Python 2.7 and 3 you should know that `Counter.most_common` behaves differently between the versions when multiple items have the same frequency. With 2.7 the median is returned. However with Python 3, the first item encountered is returned. (At least with the particular releases I'm using.)

---


## Getting Started ##
> ### Acquiring pystaggrelite3 directly from cheese shop ###
> > Dictset is in the cheese shop (pypi) under "pystaggrelite3." If you have setuptools all you need to do is:
```
    easy_install pystaggrelite3
```
> > and you are done.

> _This is assuming easy\_install (part of setuptools) is in your path. If you are not familiar with easy\_install it should be in the Scripts folder of your installation._
> > Example:
```
    C:\Python27\Scripts\easy_install.exe pystaggrelite3
```

> ### Acquiring setuptools so you can acquire pystaggrelite3 directly from the cheeseshop ###
> > If you don't have setuptools, it is available [here](http://pypi.python.org/pypi/setuptools) (assumming you are not using Python 3).

> ### Manual installation ###
> > If you don't want to install setuptools or cannot install setuptools you can install pystaggrelite3 manually from the source. Just download and extract the module from http://pypi.python.org/pypi/pystaggrelite3/.
> > And then run:
```
    setup.py install
```

---


## Table Implemented Aggregate Functions ##

| **Function**        | **Returns**                                           | **Notes** |
|:--------------------|:------------------------------------------------------|:----------|
| abs\_mean(X)       | mean of the absolute values of X                    |         |
| arbitrary(X)      | an arbitrary element of X                           |         |
| ci(X)             | 95% confidence interval of X                        | ‡       |
| datarange(X)      | range of X                                          |         |
| geometric\_mean(X) | geometric mean of X                                 | †       |
| hasinf(X)         | `True` if X contains any `inf` values               |         |
| hasnan(X)         | `True` if X contains any `nan` values               |         |
| kurt(X)           | sample kurtosis estimate of X                       |         |
| kurtp(X)          | population kurtosis estimate of X                   |         |
| median(X)         | median of X                                         | ζ₁      |
| mode(X)           | mode of X                                           | ζ₂      |
| prod(X)           | product of the elements of X                        |         |
| rms(X)            | root mean square of X                               |         |
| sem(X)            | standard error of the mean of X                     | ‡       |
| skew(X)           | sample skewness estimate of X                       |         |
| skew(X)           | population skewness estimate of X                   |         |
| stdev(X)          | standard deviation estimate of the samples in X     | ‡, N-1  |
| stdevp(X)         | standard deviation of the population X              | ‡, N    |
| var(X)            | variance estimate of the samples in X               | ‡, N-1  |
| varp(X)           | variance of the population X                        | ‡, N    |

‡ - Uses Welford's 1962 method for estimating running variance

† - Modeled after `scipy.stats.gmean`.
```
  if:   any([x<0  for x in X]): returns None
  elif: any([x==0 for x in X]): returns 0.
  else: return exp(sum([log(10) for x in X]))
```

> (_actual function is a running function_)

ζ₁ - Not a running calculation. Appends values to list, sorts, and returns

ζ₂ - Not a running calculation. Uses `collections.Counter` object

---

## Example ##
```
import sqlite3
import random

# import pystaggrelite3
import pystaggrelite3

con = sqlite3.connect(":memory:")

# bind aggregate functions to sqlite3
con.create_aggregate("var", 1, pystaggrelite3.var)
con.create_aggregate("skew", 1, pystaggrelite3.skew)
con.create_aggregate("kurt", 1, pystaggrelite3.kurt)

cur = con.cursor()
cur.execute("create table test(f)")

for i in xrange(10000):
    cur.execute("insert into test(f) values (?)",
                (random.uniform(-1000.,1000.),))

# Use aggregate
cur.execute("select var(f) from test")
print 'var: ',cur.fetchone()[0],'(should be ~ 333,666.666)'

cur.execute("select skew(f) from test")
print 'skew:',cur.fetchone()[0],'(should be ~ 0.)'

cur.execute("select kurt(f) from test")
print 'kurt:',cur.fetchone()[0],'(should be ~ -1.2)'
```

## Example Output ##
```
>>> ================================ RESTART ================================
>>> 
var:  334483.299084 (should be ~ 333,333.333)
skew: -0.0235807238813 (should be ~ 0.)
kurt: -1.20059644856 (should be ~ -1.2)
>>>
```
> See: http://mathworld.wolfram.com/UniformDistribution.html


---


## Use the `getaggregators` method to bind all aggregate functions ##
```
import random
import sqlite3
import pystaggrelite3

con = sqlite3.connect(":memory:")

for (name,arity,func) in pystaggrelite3.getaggregators():
    con.create_aggregate(name,arity,func)
```


---

## Related Projects ##
  * [madis](http://code.google.com/p/madis/) - Complex data analysis/processing made easy
> > _madis has other functionality besides aggregate functions. This project is much smaller in scope and oriented primarily to statistics._

---

## Performance Tests ##

> With timeit we can compare the performance of py-st-a-ggre-lite3 to madis (at least where they possess similar functions).

```
import sqlite3
import random

import pystaggrelite3
import madis_statistics

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


```
> From the results we can see that py-st-aggre-lite3 is significantly faster than madis for mode calculations. This is due to the fact that we are using Python's collections.Counter type while madis is appending the items to a list and then sorting them into a dict in final.

> ![http://chart.apis.google.com/chart?chxl=0:|var|stdev|mode|median|range|geomean&chxr=0,0,50|1,0,50&chxt=x,y&chbh=a&chs=480x300&cht=bvg&chco=80C65A,3D7930&chds=0,50,0,50&chd=t:17.781,17.707,49.091,18.595,16.102,17.187|16.559,16.565,19.24,17.446,14.878,16.799&chdl=madis|py-st-a-ggre-lite3&chdlp=b&chtt=Computation+time+in+seconds++(lower+is+better)&chts=676767,14.5&nonsense=something_that_ends_with.png](http://chart.apis.google.com/chart?chxl=0:|var|stdev|mode|median|range|geomean&chxr=0,0,50|1,0,50&chxt=x,y&chbh=a&chs=480x300&cht=bvg&chco=80C65A,3D7930&chds=0,50,0,50&chd=t:17.781,17.707,49.091,18.595,16.102,17.187|16.559,16.565,19.24,17.446,14.878,16.799&chdl=madis|py-st-a-ggre-lite3&chdlp=b&chtt=Computation+time+in+seconds++(lower+is+better)&chts=676767,14.5&nonsense=something_that_ends_with.png)

> On the other aggregate operations we still have a slight edge with computation time. Also keep in mind madis always appends the elements to a list, while py-st-aggre-lite3 uses running calculations were possible. When aggregating extremely large datasets this could play an important factor.

### Table of Computation Times ###
| **function**      | **pystaggrelite3** | **madis** | **time delta** | **% faster** |
|:------------------|:-------------------|:----------|:---------------|:-------------|
| varp            |  16.558          | 17.780  | 1.192        | 6.7%       |
| stdevp          |  16.564          | 17.707  | 1.143        | 6.4%       |
| mode            |  19.239          | 49.090  | 29.851       | 60.8%      |
| median          |  17.445          | 18.595  | 1.140        | 6.1%       |
| datarange       |  14.877          | 16.101  | 1.224        | 7.6%       |
| geometric\_mean  |  16.798          | 17.186  | 0.388        | 2.3%       |
