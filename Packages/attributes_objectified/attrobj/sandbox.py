
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
        if not hasattr( self, '__hash_value__' ):
            self.__hash_value__ = ('Alpha',self.name).__hash__()
        return self.__hash_value__ 
 

 ##  https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

import json

class Registry_i(type):
    """Metaclass designed to enable creation of classes which which maintain a registry of instances"""
    
    _instances = {}
    def __call__(cls, *args, **kwargs):
        h = tuple([cls.__name__] + list(args) + [json.dumps(kwargs, sort_keys=True)] ).__hash__()
        print( cls.__name__, args, h )

        ## if the hash is not in the dictionary, create a new instance, save in dictionary, and return.
        if h not in cls._instances:
            this_instance = super(Registry_i, cls).__call__(*args, **kwargs)
            cls._instances[h] = this_instance
            if hasattr( this_instance, '__post_init__' ):
              this_instance.__post_init__()

        ## if the hash is found, retrieve existing instance.
        ## there is an optional call to the __repeat_init__ method, of present. This method could be used for
        ## logging etc, but should not modify the instance.
        else:
            this_instance = cls._instances[h]
            if hasattr( this_instance, '__repeat_init__' ):
               this_instance.__repeat_init__()

        this_instance.__hash_value__ = h
        return this_instance


class Registry(type):
    """Metaclass designed to enable creation of classes which which maintain a registry of instances"""
    
    _instances = {}
    def __call__(cls, *args, **kwargs):
        h = tuple([cls.__name__] + list(args) + [json.dumps(kwargs, sort_keys=True)] )
        ##h = tuple([cls.__name__] + list(args) + [json.dumps(kwargs, sort_keys=True)] ).__hash__()
        print( cls.__name__, args, h )

        ## if the hash is not in the dictionary, create a new instance, save in dictionary, and return.
        if h not in cls._registry:
            this_instance = super(Registry, cls).__call__(*args, **kwargs)

        ### a bit hacky ... because dataclass decorator overwrites __hash__ in baseclass
            ##this_instance.__hash__ = this_instance.__base_hash__

            cls._registry[h] = this_instance
            if hasattr( this_instance, '__post_init__' ):
              this_instance.__post_init__()

        ## if the hash is found, retrieve existing instance.
        ## there is an optional call to the __repeat_init__ method, of present. This method could be used for
        ## logging etc, but should not modify the instance.
        else:
            this_instance = cls._registry[h]
            if hasattr( this_instance, '__repeat_init__' ):
               this_instance.__repeat_init__()

        try:
          this_instance.__hash_value__ = h
        except:
            pass

        return this_instance


#Python3
##class MyClass(BaseClass, metaclass=Singleton):
    ##pass

class Beta(object, metaclass=Registry_i):
    def __init__(self,name: str):
        self.name = name
        print( 'returning new instance for %s' % self.name)

    def __first_time_init__(self):
        print( 'Running extras: %s ' % self.name)

    def __repeat_init__(self):
        print( 'returning %s from regitsry' % self.name)

    def __eq__(self,other):
        if isinstance( other, Alpha) and other.name == self.name:
            return True
        return False

    def __hash__(self):
        return self.__hash_value__ 

from dataclasses import dataclass

@dataclass
class InventoryItem:
    """Class for keeping track of an item in inventory."""
    name: str
    unit_price: float
    quantity_on_hand: int = 0

    def total_cost(self) -> float:
        return self.unit_price * self.quantity_on_hand


@dataclass
class Gamma(object, metaclass=Registry_i):
    name: str
    age: int

    def __post_init__(self):
        print( 'Running extras: %s ' % self.name)

    def __repeat_init__(self):
        print( 'returning %s from regitsry' % self.name)

    def __hash__(self):
        return self.__hash_value__ 


class BaseDelta(object, metaclass=Registry):
    _registry = dict()
    def __base_hash__(self):
        return self.__hash_value__ 
    def some_method(self):
        print( 'SOME METHOD' )

class x(BaseDelta):
    def __init__(self):
        self.__hash_value__ = 33



@dataclass(frozen=True)
class Delta(BaseDelta):
    name: str
    age: int

    def x__post_init__(self):
        print( 'At post init %s' % self.name )

    def x__repeat_init__(self):
        print( 'returning %s from regitsry' % self.name)

def ex01():
    a = Beta('Fred')
    b = Beta('John')
    c = Beta('Fred')


    x = InventoryItem( name='pen', unit_price=5, quantity_on_hand=5 )
    y = InventoryItem( name='pen', unit_price=5, quantity_on_hand=5 )

    print( '---- Delta ---- ' )
    h = Delta( name='Jones', age=10)
    print( '---- Delta ---- ' )
    i = Delta( age=10, name='Jones')
    ee = {h:'a'}
    print( 'i from ee',ee.get( i, '__ not found __') )


    print( 'a == c',a==c )
    print( 'a is c',a is c )
    ee = {a:'a', b:'b' }
    print( 'c from ee',ee.get( c, '__ not found __') )
    print( 'x == y',x==y )
    print( 'x is y',x is y )
    print( 'h == i',h==i )
    print( 'h is i',h is i )


ex01()
