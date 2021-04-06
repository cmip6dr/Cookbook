

import json



class Registry(type):
    """Metaclass designed to enable creation of classes which which maintain a registry of instances"""
    
    _instances = {}
    def __call__(cls, *args, **kwargs):
        l = list(args)
        for k,i in kwargs.items():
            if hasattr(i,'__hash__'):
                l += [k,i.__hash__()]
            else:
                l += [k,i]
        ##h = tuple([cls.__name__] + list(args) + [json.dumps(kwargs, sort_keys=True)] )
        h = tuple([cls.__name__] + l)
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


from dataclasses import dataclass

@dataclass
class InventoryItem:
    """Class for keeping track of an item in inventory."""
    name: str
    unit_price: float
    quantity_on_hand: int = 0

    def total_cost(self) -> float:
        return self.unit_price * self.quantity_on_hand


class BaseDelta(object, metaclass=Registry):
    _registry = dict()
    def __base_hash__(self):
        return self.__hash_value__ 
    def some_method(self):
        print( 'SOME METHOD' )

class BaseCV(object, metaclass=Registry):
    _registry = dict()
    def __base_hash__(self):
        return self.__hash_value__ 

    def __post_init__(self):
        assert self.value in self._permitted_values

class BuildCVs(object):
  def __init__(self,permitted_values):
    self.permitted_values = permitted_values
  def __call__(self,cls):
    cls._permitted_values = self.permitted_values
    cls.__annotations__ = {'value': str}
    return dataclass( frozen=True )(cls)


@dataclass(frozen=True)
class Delta(BaseDelta):
    name: str
    age: int

    def x__post_init__(self):
        print( 'At post init %s' % self.name )

    def x__repeat_init__(self):
       print( 'returning %s from regitsry' % self.name)

@BuildCVs(permitted_values=['a','b','c'])
class CV01(BaseCV): pass



@dataclass(frozen=True)
class FileSection(BaseDelta):
    name: str = None
    is_global: bool = False
    is_dimensions: bool = False

    def __post_init__(self):
        assert not ( self.is_global and self.is_dimensions )
        if self.is_global or self.is_dimensions:
            assert self.name == None

@dataclass(frozen=True)
class Attribute(BaseDelta):
    name: str
    section: FileSection
    def __post_init__(self):
        assert not self.section.is_dimensions

def ex01():

    x = InventoryItem( name='pen', unit_price=5, quantity_on_hand=5 )
    y = InventoryItem( name='pen', unit_price=5, quantity_on_hand=5 )
    print( 'x == y',x==y )
    print( 'x is y',x is y )

    print( '---- Delta ---- ' )
    h = Delta( name='Jones', age=10)
    print( '---- Delta ---- ' )
    i = Delta( age=10, name='Jones')
    ee = {h:'a'}
    print( 'i from ee',ee.get( i, '__ not found __') )




ex01()
