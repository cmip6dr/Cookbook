
def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

##
## this works .. but is messy .. repetition of argmument "name" and hash calculation. 
##   hash can be cleaned up by using __hash__ ...
## first time init should use properties of self, not arguments ...
## 
## need to delegate this effort to a Factory or to methods in a parentclass
##
## Improved a bit ... could work with this ...
##
class Alpha(object):
    registry = dict()
    def __init__(self,name: str):
        self.name = name
        if self.__hash__() not in self.registry:
            self.__first_time_init__()

    def __first_time_init__(self):
        h = self.__hash__()
        assert h not in self.registry
        self.registry[h] = self
        print( 'returning new instance for %s' % self.name)

    def __new__(cls,name):
        h = ('Alpha',name).__hash__()
        if h in cls.registry:
            print( 'returning %s from regitsry' % name)
            return cls.registry[h]
        return super(Alpha, cls).__new__(cls)

    def __eq__(self,other):
        if isinstance( other, Alpha) and other.name == self.name:
            return True
        return False

    def __hash__(self):
        if not hasattr( self, '__hashed__' ):
            self.__hashed__ = ('Alpha',self.name).__hash__()
        return self.__hashed__ 





def ex01():
    a = Alpha('Fred')
    b = Alpha('John')
    c = Alpha('Fred')


    print( 'a == c',a==c )
    print( 'a is c',a is c )
    ee = {a:'a', b:'b' }
    print( 'c from ee',ee.get( c, '__ not found __') )


ex01()
