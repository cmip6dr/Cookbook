

class B(object):
   def __init__(self,x):
        print( 'B.__init__: x=%s' % x )
        self.x = x

class A(object):
   def __init__(self,x):
        print( 'A.__init__: x=%s' % x )
        self.x = x


   def __call__(cls, *args, **kwargs):
        """A.__call__: can be used to work on arguments passed to init """
        print( "A.__call__: args=%s " % list(args) )
        print( cls )

        ## this call requires a type ... but can use for object in ChildBase.
        result = type('NewClass',(B,cls), dict(help='helptext') )
        return result


a1 = A(1)


## a1 is a callable ... but not "class-like" ... cannot x = a1() is not an instance of a1.
