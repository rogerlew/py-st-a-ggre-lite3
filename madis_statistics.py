##import setpath
##import functions
import math
##from lib import iso8601
import re
import datetime
##from lib.buffer import CompBuffer


__docformat__ = 'reStructuredText en'

class modeop:

    """
    .. function:: modeop(X) -> [ModeOpElements int/str, ModeOpValue int]

    Returns the mode (i.e. the value that occurs the most frequently in a data set), along with the modevalue (i.e. the maximum frequency of occurrence)
    When more than one modes are found in a data set (i.e. when more than one values appear with the maximum frequency), all values are returned.

    For a sample from a continuous distribution, such as [0.935..., 1.211..., 2.430..., 3.668..., 3.874...], the concept of mode is unusable in its raw form,
    since each value will occur precisely once. Following the usual practice, data is discretized by rounding to the closer int value.
    For a textual sample, values are first converted to lowercase.

    :Returned multiset schema:
        Columns are automatically named as *ModeOpElements, ModeOpValue*

    .. seealso::

       * :ref:`tutmultiset` functions

    Examples:

    >>> table1('''
    ... 1
    ... 3
    ... 6
    ... 6
    ... 6
    ... 6
    ... 7
    ... 7
    ... 7
    ... 7
    ... 12
    ... 12
    ... 17
    ... ''')
    >>> sql("select modeop(a) from table1")
    ModeOpElements | ModeOpValue
    ----------------------------
    6              | 4
    7              | 4


    >>> table2('''
    ... 1.1235
    ... 1
    ... 5.1
    ... 5.2
    ... 5.3
    ... 5.5
    ... 5.6
    ... 5.7
    ... ''')
    >>> sql("select modeop(a) from table2")
    ModeOpElements | ModeOpValue
    ----------------------------
    5              | 3
    6              | 3

    >>> table3('''
    ... leuteris
    ... maria
    ... marialena
    ... Meili
    ... meili
    ... ''')
    >>> sql("select modeop(a) from table3")
    ModeOpElements | ModeOpValue
    ----------------------------
    meili          | 2

.. doctest::
    :hide:

    >>> sql("delete from table3")
    >>> sql("select modeop(a) from table3")
    ModeOpElements | ModeOpValue
    ----------------------------
    None           | None

    """
    registered=True #Value to define db operator
    multiset=True

    def __init__(self):
        self.init=True
        self.sample = []
        self.modevalue = 0

    def initargs(self, args):
        self.init=False
        if not args:
            raise functions.OperatorError("modeop","No arguments")
        if len(args)>1:
            raise functions.OperatorError("modeop","Wrong number of arguments")

    def step(self, *args):
        if self.init==True:
            self.initargs(args)

        if isinstance(args[0], basestring):
            #For the case of textual dataset, values are converted to lowercase
            self.element = (args[0]).lower()
        else:
            #For the case of arithmetic dataset, values are rounded and converted to int
            self.element = int(round(args[0]))
        self.sample.append(self.element)
        
    def finalize(self):
        output=[]

        if (not self.sample):
            output+=['None']
            modevalue='None'
        else:
            self.sample.sort()

            # Initialize a dictionary to store frequency data.
            frequency = {}
            # Build dictionary: key - data set values; item - data frequency.
            for x in self.sample:
                if (x in frequency.keys()):
                    frequency[x]+=1
                else:
                    frequency[x]=1
            # Find the modeval, i.e. the maximum frequency
            modevalue = max(frequency.values())

            # If the value of mode is 1, there is no mode for the given data set.
            if (modevalue == 1):
                 output+=['None']
                 modevalue='None'
            else:
                # Step through the frequency dictionary, looking for keys equaling
                # the current modevalue.  If found, append the key to output list.
                for x in frequency:
                    if (modevalue == frequency[x]):
                        output+=[x]

##        #CREATE MULTISET OUTPUT
##        #print all keys, along with the modevlaue
##        a=CompBuffer()
##        a.writeheader(["ModeOpElements", "ModeOpValue"])
##        for el in output:
##            a.write([el, modevalue])
##        return a.serialize()



class median:
    """
    .. function:: median(X) -> [median float]

    Returns the median, i.e.numeric value separating the higher half of a sample, a population, or a probability distribution, from the lower half.
    It is computed by arranging all the observations from lowest value to highest value and picking the middle one.
    If there is an even number of observations, then there is no single middle value, so the mean of the two middle values is obtained.
    Incoming textual values are simply ignored.

    Examples:

    >>> table1('''
    ... 1
    ... 3
    ... 6
    ... 6
    ... 6
    ... 6
    ... 7
    ... 7
    ... 7
    ... 7
    ... 12
    ... 12
    ... 17
    ... ''')
    >>> sql("select median(a) from table1")
    median(a)
    ---------
    7.0

    >>> table2('''
    ... 1
    ... 2
    ... 2
    ... 3
    ... 3
    ... 9
    ... ''')
    >>> sql("select median(a) from table2")
    median(a)
    ---------
    2.5

    >>> table3('''
    ... 1
    ... 2
    ... maria
    ... lala
    ... null
    ... 'None'
    ... 3
    ... 9
    ... ''')
    >>> sql("select median(a) from table3")
    median(a)
    ---------
    2.5

.. doctest::
    :hide:

    >>> sql("delete from table3")
    >>> sql("select median(a) from table3")
    median(a)
    ---------
    None

    """
    registered=True #Value to define db operator

    def __init__(self):
        self.init=True
        self.sample = []
        self.counter=0

    def initargs(self, args):
        self.init=False
        if not args:
            raise functions.OperatorError("median","No arguments")
        if len(args)>1:
            raise functions.OperatorError("median","Wrong number of arguments")

    def step(self, *args):
        if self.init==True:
            self.initargs(args)

        if not(isinstance(args[0], basestring)) and args[0]:
            self.counter +=1
            self.element = float((args[0]))
            self.sample.append(self.element)

    def finalize(self):
        if (not self.sample):
            return
        self.sample.sort()

        """Determine the value which is in the exact middle of the data set."""
        if (self.counter%2):		# Number of elements in data set is even.
            self.median = self.sample[self.counter/2]
        else:                           # Number of elements in data set is odd.
            midpt = self.counter/2
            self.median = (self.sample[midpt-1] + self.sample[midpt])/2.0

        return self.median



class variance:
    """
    .. function:: variance(X,[type]) -> [variance float]

    Determine the measure of the spread of the data set about the mean.
    Sample variance is determined by default; population variance can be
    determined by setting the (optional) second argument to values 'true' or 'population'.
    When values 'false' or 'sample' are entered for type, the default sample variance computation is performed.

    Examples:

    >>> table1('''
    ... 1
    ... 2
    ... 3
    ... 4
    ... 5
    ... 6
    ... 'text is ignored'
    ... 'none'
    ... ''')
    >>> sql("select variance(a) from table1")
    variance(a)
    -----------
    3.5
    >>> sql("select variance(a,'false') from table1")
    variance(a,'false')
    -------------------
    3.5
    >>> sql("select variance(a,'sample') from table1")
    variance(a,'sample')
    --------------------
    3.5
    >>> sql("select variance(a,'True') from table1")
    variance(a,'True')
    ------------------
    2.91666666667
    >>> sql("select variance(a,'Population') from table1")
    variance(a,'Population')
    ------------------------
    2.91666666667

.. doctest::
    :hide:

    >>> sql("delete from table1")
    >>> sql("select variance(a) from table1")
    variance(a)
    -----------
    None
    """
    registered=True #Value to define db operator

    def __init__(self):
        self.init=True
        self.sample = []
        self.tmpsum=0.0
        self.counter=0
        self.mean = 0.0
        self.population=False
        
    def initargs(self, args):
        self.init=False

        if not args:
            raise functions.OperatorError("variance","No arguments")
        elif len(args)==2:
            tmp = args[1].lower()
            if (tmp=='false' or tmp=='sample'):
                self.population=False
            elif (tmp=='true' or tmp=='population'):
                self.population=True
            else:
                raise functions.OperatorError("variance", "Wrong value in second argument"+'\n'+
            "Accepted Values:"+'\n'
            "----False, false, FALSE, sample---- for Sample Variance"+'\n'+
            "----True, true, TRUE, population---- for Population Variance"+'\n')
        elif len(args)>2:
            raise functions.OperatorError("variance","Wrong number of arguments")

    def step(self, *args):
        if self.init==True:
            self.initargs(args)

        if not(isinstance(args[0], basestring)) and args[0]:
            self.tmpsum += args[0]
            self.counter +=1
            self.element = float(args[0])
            self.sample.append(self.element)

    def finalize(self):
        if (not self.sample):
            return
        self.mean = self.tmpsum/self.counter
        x=0
        # Subtract the mean from each data item and square the difference.
        # Sum all the squared deviations.
        for item in self.sample:
            x += (item - self.mean)**2.0
        
        try:
            if (not self.population and self.counter>1):
            # Divide sum of squares by N-1 (sample variance).
                self.variance = x/(self.counter-1)
            else:
            # Divide sum of squares by N (population variance).
                self.variance = x/self.counter
        except:
            self.variance = 0
        return self.variance
        

class sdev:
    """
    .. function:: sdev(X,[type]) -> [sdev float]

    Computes standard deviation of a dataset X, i.e. the square root of its variance.
    Sample standard deviation is determined by default; population standard deviation can be
    determined by setting the (optional) second argument to values 'true' or 'population'.
    When values 'false' or 'sample' are entered for type, the default sample standard deviation
    computation is performed.

    Examples:

    >>> table1('''
    ... 3
    ... 7
    ... 7
    ... 19
    ... 'text is ignored'
    ... 'none'
    ... ''')
    >>> sql("select sdev(a) from table1")
    sdev(a)
    -------------
    6.92820323028
    >>> sql("select sdev(a,'population') from table1")
    sdev(a,'population')
    --------------------
    6.0
    >>> sql("select sdev(a,'true') from table1")
    sdev(a,'true')
    --------------
    6.0

.. doctest::
    :hide:

    >>> sql("delete from table1")
    >>> sql("select sdev(a) from table1")
    sdev(a)
    -------
    None
    
    """

    registered=True #Value to define db operator

    def __init__(self):
        self.init=True
        self.sample = []
        self.tmpsum=0.0
        self.counter=0
        self.mean = 0.0
        self.population=False
        self.stddev=0.0

    def initargs(self, args):
        self.init=False
        if not args:
            raise functions.OperatorError("sdev","No arguments")
        elif len(args)==2:
            tmp = args[1].lower()
            if tmp=='false' or tmp=='sample':
                self.population=False
            elif tmp=='true' or tmp=='population':
                self.population=True
            else:
                raise functions.OperatorError("sdev", "Wrong value in second argument"+'\n'+
            "Accepted Values:"+'\n'
            "----False, false, FALSE, sample---- for Sample Standard Deviation"+'\n'+
            "----True, true, TRUE, population---- for Population Standard Deviation"+'\n')
        elif len(args)>2:
            raise functions.OperatorError("sdev","Wrong number of arguments")

    def step(self, *args):
        if self.init==True:
            self.initargs(args)
        
        if not(isinstance(args[0], basestring)) and args[0]:
            self.tmpsum += args[0]
            self.counter +=1
            self.element = float(args[0])
            self.sample.append(self.element)

    def finalize(self):
        if (not self.sample):
            return
        self.mean = self.tmpsum/self.counter
        #variance computation, as in variance operator
        x=0
        for item in self.sample:
            x += (item - self.mean)**2.0
        try:
            if (not self.population and self.counter>1):   # Divide sum of squares by N-1 (sample variance).
                self.variance = x/(self.counter-1)
            else:                       # Divide sum of squares by N (population variance).
                self.variance = x/self.counter
        except:
            self.variance = 0
        
        #Determine the measure of the dispersion of the data set based on the variance.
        self.stddev = math.sqrt(self.variance) # Take the square root of the variance.
        return self.stddev



class rangef:

    """
     .. function:: rangef(X) -> [rangef float]

    Computes the numerical range for a dataset X, substracting the minimum value from the maximum value.
    Textal and NULL data entries are simply ignored.

    Examples:
    
    >>> table1('''
    ... 1
    ... 3
    ... 6
    ... 6
    ... 7
    ... 12
    ... 12
    ... 17
    ... 'text is ignored'
    ... 'None'
    ... ''')
    >>> sql("select rangef(a) from table1")
    rangef(a)
    ---------
    16.0

.. doctest::
    :hide:

    >>> sql("delete from table1")
    >>> sql("select rangef(a) from table1")
    rangef(a)
    ---------
    None
    """
    registered=True #Value to define db operator
    

    def __init__(self):
        self.init=True
        self.sample=[]

    def initargs(self, args):
        self.init=False
        if len(args)<>1:
            raise functions.OperatorError("rangef","Wrong number of arguments")
    
    def step(self, *args):
        if not(isinstance(args[0], basestring)) and args[0]:
            self.sample.append(float(args[0]))
        
    def finalize(self):
        if (not self.sample):
            return
        self.range=max(self.sample) - min(self.sample)
        return self.range

class amean:
    """
    .. function:: amean(X) -> [amean float]

    Computes the arithmetic mean, i.e. the average, thus providing an alternative choise
    to traditional *avg*  offered by
    sqlite.

    Examples:

    >>> table1('''
    ... 1
    ... 2
    ... 2
    ... 3
    ... 'text is ignored, as well as null values'
    ... 'none'
    ... ''')
    >>> sql("select amean(a) from table1")
    amean(a)
    --------
    2.0

.. doctest::
    :hide:

    >>> sql("delete from table1")
    >>> sql("select amean(a) from table1")
    amean(a)
    --------
    None
    
    """
    registered=True #Value to define db function

    def __init__(self):
        self.init=True
        self.counter=0
        self.sum=0.0
        self.sample=[]

    def initargs(self, args):
        self.init=False
        if not args:
            raise functions.OperatorError("amean","No arguments")
        elif len(args)>1:
            raise functions.OperatorError("amean","Wrong number of arguments")

    def step(self, *args):
        if self.init==True:
            self.initargs(args)

        if not(isinstance(args[0], basestring)) and args[0]:
            self.sample.append(float(args[0]))
            self.sum += float(args[0])
            self.counter+=1

    def finalize(self):
        if (not self.sample):
            return
        return self.sum/self.counter

class wamean:
    """
    .. function:: wamean(W,X) -> [wamean float]

    Computes the weighted arithmetic mean, i.e. the weighted average.
    First column contains the weights and second column contains the actual data values.

    .. math::

        wamean_{\mathrm} = \sum_{i=1}^{N} w_i x_i / \sum_{i=1}^{N} w_i
    

    Examples:

    >>> table1('''
    ... 2 1
    ... 2 2
    ... 1 2
    ... 'text is ignored, as well as null values' 3
    ... 'none' 2
    ... 1 'text is ignored, as well as null values'
    ... 2 'none'
    ... 2 3
    ... ''')
    >>> sql("select wamean(a,b) from table1")
    wamean(a,b)
    -----------
    2.0

.. doctest::
    :hide:

    >>> sql("delete from table1")
    >>> sql("select wamean(a) from table1")
    wamean(a)
    ---------
    None

    """
    registered=True #Value to define db operator

    def __init__(self):
        self.init=True
        self.counter=0
        self.sum=0.0

    def initargs(self, args):
        self.init=False
        if (len(args)<>2):
            raise functions.OperatorError("wamean","Wrong number of arguments")

    def step(self, *args):
        if self.init==True:
            self.initargs(args)

        if not(isinstance(args[0], basestring)) and args[0] and not(isinstance(args[1], basestring)) and args[1]:
            self.sum += args[0]*args[1]
            self.counter+=args[0]

    def finalize(self):
        if (self.counter==0):
            return
        return self.sum/self.counter

class gmean:
    """
    .. function:: gmean(X,[m]) -> [gmean float]
    
    Computes the genaralized mean (also known as the power mean or Holder mean),
    which is an abstraction of the *Pythagorean means* including *arithmetic*, *geometric*, and *harmonic* means.
    
    It is defined for a set of *n* positive real numbers as follows:

    .. math::

        gmean_{\mathrm} = 	\Big ( {1 \over N} \sum_{i=1}^{N} x_i ^p  \Big ) ^{1/p}



    The (optional) second argument stands for the *p* paramteter, thus determining the exact mean type:

    - p=2 : *Quadratic mean*     (computed for both negative and positive values)

    - p=1 : *Artihmetic mean*

    - p=0 : *Geometric mean*     (only for positive real numbers)

    - p=-1: *Harmonian mean*     (only for positive real numbers)

    By default, i.e. in absence of second argument, p is set to 0, computing
    the geometric mean.

    Examples:

    >>> table1('''
    ... 6
    ... 50
    ... 9
    ... 1200
    ... 'text is ignored, as well as None values'
    ... 'None'
    ... ''')
    >>> sql("select gmean(a) from table1")
    gmean(a)
    -------------
    42.4264068712

    >>> table2('''
    ... 34
    ... 27
    ... 45
    ... 55
    ... 22
    ... 34
    ... ''')
    >>> sql("select gmean(a,1) from table2")
    gmean(a,1)
    -------------
    36.1666666667
    >>> sql("select gmean(a,0) from table2")
    gmean(a,0)
    -------------
    34.5451100372
    >>> sql("select gmean(a) from table2")
    gmean(a)
    -------------
    34.5451100372
    >>> sql("select gmean(a,-1) from table2")
    gmean(a,-1)
    -------------
    33.0179836512
    >>> sql("select gmean(a,2) from table2")
    gmean(a,2)
    -------------
    37.8043207407

    

    """
    registered=True #Value to define db operator

    def __init__(self):
        self.init=True
        self.counter=0
        self.sum=0.0
        self.p=0.0
        self.result=0.0

    def initargs(self, args):
        self.init=False

        if not args:
            raise functions.OperatorError("gmean","No arguments")
        elif len(args)>2:
            raise functions.OperatorError("gmean","Wrong number of arguments")
        elif len(args)==2:
            self.p=args[1]
            if self.p>2 or self.p<-1:
                raise functions.OperatorError("\n gmean","Second argument takes values from -1 to 2\n"+
        "p=2 :quadratic mean     (for both negative and positive values)\n"+
        "p=1 :artihmetic mean\n"+
        "p=0 :geometric mean     (for positive real numbers)\n"+
        "p=-1:harmonian mean     (for positive real numbers)\n")

    def step(self, *args):
        if self.init==True:
            self.initargs(args)
        if not(isinstance(args[0], basestring)) and args[0]:
            if self.p<1 and args[0]<1:
                raise functions.OperatorError("gmean","The specified type of mean applies only to positive numbers")
        # The easiest way to think of the geometric mean is that
        #it is the average of the logarithmic values, converted back to a base 10 number.
            if self.p==0:
                self.sum += math.log10(args[0])
            else:
                self.sum += args[0]**self.p
            self.counter +=1

    def finalize(self):
        if (self.counter==0):
            return
        if self.p==0:
            result = 10**(self.sum/self.counter)
            return result
        else:
            return  (self.sum/self.counter)**(1.0/self.p)

re_now=re.compile('now:(?P<now>.*)')

class frecency:
    """
    .. function:: frecency(actiondate[,points[,now:date]])

    Returns a float weighted sum assigning to each action *points* or less, depending on the *actiondate* distance to the current date (or *now:date*).
    In detail the action points decrease 30% at distance 10-30 days, 50% at  1-3 months, 70% at 3-6 months and 90% at greater distance. Date parameters should be in ISO8601 format.

    .. _iso8601:

     **ISO 8601 format** :

    Year:
      YYYY (eg 1997)
    Year and month:
      YYYY-MM (eg 1997-07)
    Complete date:
      YYYY-MM-DD (eg 1997-07-16)
    Complete date plus hours and minutes:
      YYYY-MM-DD hh:mmTZD (eg 1997-07-16 19:20+01:00)
    Complete date plus hours, minutes and seconds:
      YYYY-MM-DD hh:mm:ssTZD (eg 1997-07-16 19:20:30+01:00)
    Complete date plus hours and minutes:
      YYYY-MM-DDThh:mmTZD (eg 1997-07-16T19:20+01:00)
    Complete date plus hours, minutes and seconds:
      YYYY-MM-DDThh:mm:ssTZD (eg 1997-07-16T19:20:30+01:00)

    Examples:
    
    >>> table1('''
    ... 2009-06-01	1
    ... 2009-08-28	2
    ... 2009-09-17	3
    ... ''')
    >>> sql("select frecency(a,'now:2009-09-26 04:38:30') from table1")
    frecency(a,'now:2009-09-26 04:38:30')
    -------------------------------------
    200.0

   
    """


    registered=True #Value to define db operator

    def __init__(self):
        self.frecency=0
        self.initstatic=False
        self.points=None
        self.now=None

    def __decrease(self,offsettimedelta):
        if offsettimedelta<=datetime.timedelta(days=10):
            return 1.0
        if offsettimedelta<=datetime.timedelta(days=30):
            return 0.7
        if offsettimedelta<=datetime.timedelta(days=(30*3)):
            return 0.5
        if offsettimedelta<=datetime.timedelta(days=(30*6)):
            return 0.3
        return 0.1

    def step(self, *args):
        if not args:
            raise functions.OperatorError("frecency","No arguments")
        # last 2 arguments are static , so they are parse only the first time
        if not self.initstatic:
            self.initstatic=True
            self.points=100.0
            self.now=datetime.datetime.now()
            if len(args)>=2:
                for arg in args[1:]:
                    isnowarg=re_now.match(arg)
                    if isnowarg:
                      nowdate=isnowarg.groupdict()['now']
                      self.now=iso8601.parse_date(nowdate)
                    else:
                        self.points=int(arg)

        input=args[0]
        dt=iso8601.parse_date(input)
        self.frecency+=self.__decrease(self.now-dt)*self.points

    def finalize(self):
        return self.frecency



class pearson:

    """
     .. function:: pearson(X,Y) -> float

    Computes the pearson coefficient of X and Y datasets

    Examples:

    >>> sql("select pearson(value,1/value) from range(1,91)")
    pearson(value,1/value)
    ----------------------
    -0.181568259801
    >>> sql("select pearson(value,17*value+5) from range(1,91)")
    pearson(value,17*value+5)
    -------------------------
    1.0
    >>> sql("select pearson(value,pyfun('math.pow',2,value)) from range(1,41)")
    pearson(value,pyfun('math.pow',2,value))
    ----------------------------------------
    0.456349821381
    """

    registered=True #Value to define db operator
    sum_x=0
    sum_y=0

    def __init__(self):
        self.a = []
        self.b = []

    def step(self,*args):
        if len(args)<2:pass ####ERROR
        x, y = [float(i) for i in args[:2]]
        self.sum_x+=x
        self.sum_y+=y
        self.a+=[float(x)]
        self.b+=[float(y)]

    def finalize(self):
        sum_XX=0
        sum_YY=0
        sum_XY=0
        n=len(self.a)
        p=self.sum_x/n    #mean of x
        q=self.sum_y/n    #mean of y

        for i in range(n):
            X=self.a[i]-p
            Y=self.b[i]-q
            XX=math.pow(X,2)
            YY=math.pow(Y,2)
            sum_XX+=XX
            sum_YY+=YY
            XY=X*Y
            sum_XY+=XY
        return sum_XY/(math.sqrt(sum_XX*sum_YY))

##
##if not ('.' in __name__):
##    """
##    This is needed to be able to test the function, put it at the end of every
##    new function you create
##    """
##    import sys
##    import setpath
##    from functions import *
##    testfunction()
##    if __name__ == "__main__":
##        reload(sys)
##        sys.setdefaultencoding('utf-8')
##        import doctest
##        doctest.testmod()