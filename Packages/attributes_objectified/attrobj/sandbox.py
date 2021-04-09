import json, numpy, collections, netCDF4

__doc__ = """
A set of classes to generate vocabulary items.
Designed to treat attributes as objects.
Instances should be identified by their values, so classes are designed to yield existing instances if arguments are re-used.
Instances are hashable, so they can be used as dictionary keys (but hash values may vary between thredds and executables).

E.g. code scans a list of constraints, and finds a constraint on NetCDF file global attribute "source_id" and saves in as "constraints[Attributes(name='source_id',global=True)]; the code then opens a file, and for each global attribute checks to see whether "Attributes(name=key, global=True)" is in constraints, and, if it is, executesthe "apply" method .. or the "format" method: "constraints[Attributes(name=key, global=True)].format( nc )

In format.
 if type(other) == netCDF4.Dataset:
   this = getattr( nc, self.name )
   try:
     self( value=this )
   except:
     print ('ERROR...')
     ## need to catch exceptions here
"""

class TestData(object):
    def __init__(self):
        self.nc = netCDF4.Dataset( 'test.nc', 'w' )
        self.nc.history = 'Created by sandbox ... please delete'
        self.nc.source_id = 'model1'
        self.source_cv = ['model1','model2','model3']


class RegistryArg(object):
    def __init__(self,key,value):
        self.key=key
        self.value = value

def registry_arg_helper(input_list):
    l = list()
    e = dict()
    for item in input_list:
        if isinstance( item, RegistryArg ):
            e[item.key] = item.value
        else:
            l.append( item )
    return l,e



class Registry01(type):
    """Metaclass designed to enable creation of classes which which maintain a registry of instances"""
    
    _instances = {}
    def __call__(cls, *args, **kwargs):
        l, registry_args = registry_arg_helper( args )
        for k,i in kwargs.items():
            if type(i) == type:
                l += [k,id(i)]
            elif hasattr(i,'__hash__'):
                try:
                    this_hash = i.__hash__()
                except:
                    this_hash = str( i.__hash__ )
                l += [k,this_hash]
            else:
                l += [k,i]
        h = tuple([cls.__name__] + l)
        ##h = tuple([cls.__name__] + list(args) + [json.dumps(kwargs, sort_keys=True)] ).__hash__()
        print( cls.__name__, args, h )

        ## if the hash is not in the dictionary, create a new instance, save in dictionary, and return.
        if h not in cls._registry:
            this_instance = super(Registry, cls).__call__(*args, **kwargs)

        ### a bit hacky ... because dataclass decorator overwrites __hash__ in baseclass
            ##this_instance.__hash__ = this_instance.__base_hash__

            cls._registry[h] = this_instance
            if 'info' in registry_args:
              cls._registry_info[this_instance] = registry_args[info]

##
## this naieve approach does not make instance a class .....
##
            if hasattr( this_instance, '__child_init__' ):
                setattr( this_instance, '__init__', this_instance.__child_init__ )

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

REGISTRY_CLASSES_USED = set()

class SelfReference(object): pass

class Registry(type):
    """Metaclass designed to enable creation of classes which which maintain a registry of instances"""
    
    def __call__(cls, *args, **kwargs):
        ##
        ## maintain a record of all classes 
        ## note that Registry is called with a target class as argument .. it does not have its "own" scope
        ##
        REGISTRY_CLASSES_USED.add( cls )

        l, registry_args = registry_arg_helper( args )
        verbose = registry_args.get( 'verbose', False )

## create a pseudo hash from arguments, ignoring RegistryArg instances.

        self_ref = None
        for k in sorted( list( kwargs.keys() ) ):
            if k[:2] != '__':
              i = kwargs[k]
              if i == SelfReference:
                  self_ref = k
              if type(i) == type:
                  l += [k,id(i)]
              elif hasattr(i,'__hash__'):
                  try:
                      this_hash = i.__hash__()
                  except:
                      this_hash = str( i.__hash__ )
                  l += [k,this_hash]
              else:
                  l += [k,i]
        h = tuple([cls.__name__] + l)
        ##h = tuple([cls.__name__] + list(args) + [json.dumps(kwargs, sort_keys=True)] ).__hash__()

        if verbose:
          print( cls.__name__, args, h )

        ## if the hash is not in the dictionary, create a new instance, save in dictionary, and return.
        if h not in cls._registry:
            
            ##
            ## make dictionary hashable ... note there is some risk of mutability here .. 
            ## can possibly do better with modification of map to json code ...
            ##
            for k,item in kwargs.items():
               if type(item) == type( dict() ):
                   kwargs[k] =  ImDict( **item )
            this_instance = super(Registry, cls).__call__(*args, **kwargs)
            if self_ref != None:
                setattr( this_instance, self_ref, this_instance )

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

        return this_instance


from dataclasses import dataclass

@dataclass
class InventoryItem:
    """Class for keeping track of an item in inventory."""
    name: str
    unit_price: (float,int)
    quantity_on_hand: int = 0


    def total_cost(self) -> float:
        return self.unit_price * self.quantity_on_hand


class UnsetParameter(object):
    pass

class BaseCommon(object):
    _UNSET_PARAMETER = UnsetParameter

    def __post_init__(self):
        """ type is given for each field and held in __dataclass_fields__
        None can be used to indicate that a value has not been set ... could have a specific value for this instead .. defined in a base class
        """
        for k,item in self.__dataclass_fields__.items():
          value = getattr(self,k)
          if value != self._UNSET_PARAMETER:
            test = isinstance( getattr(self,k), item.type ) or type( getattr(self,k) ) == item.type
            assert test, 'attribute %s, value %s, not of type %s' % (k,getattr(self,k),item.type)

        if hasattr(self,'__post_init_extra__'):
            self.__post_init_extra__()

class BaseDelta(BaseCommon, metaclass=Registry):
    _registry = dict()
    _registry_info = dict()
    def some_method(self):
        print( 'SOME METHOD' )

    def info(self):
        return self._registry_info.get( self, None )

class BaseCV(object, metaclass=Registry01):
    _registry = dict()
    def __base_hash__(self):
        return self.__hash_value__ 

    def __post_init__(self):
        assert self.value in self._permitted_values

class BaseNumeric(object, metaclass=Registry):
    _registry = dict()
    def __base_hash__(self):
        return self.__hash_value__ 

    def __post_init__(self):
        if self._max_value != None:
          assert self.value <= self._max_value
        if self._min_value != None:
          assert self.value >= self._min_value

        if self._max_abs != None:
          assert abs(self.value) <= self._max_abs
        if self._min_abs != None:
          assert abs(self.value) >= self._min_abs

class BaseItem(BaseCommon, metaclass=Registry):
    _registry = dict()
    ##_UNSET_PARAMETER = UnsetParameter()

    def xx__post_init__(self):
        """ type is given for each field and held in __dataclass_fields__
        None can be used to indicate that a value has not been set ... could have a specific value for this instead .. defined in a base class
        """
        for k,item in self.__dataclass_fields__.items():
          value = getattr(self,k)
          if value != self._UNSET_PARAMETER:
            assert isinstance( getattr(self,k), item.type ), 'attribute %s, value %s, not of type %s' % (k,getattr(self,k),item.type)

        if hasattr(self,'__post_init_extra__'):
            self.__post_init_extra__()


class BuildCVs(object):
  def __init__(self,permitted_values):
    self.permitted_values = permitted_values
  def __call__(self,cls):
    cls._permitted_values = self.permitted_values
    cls.__annotations__ = {'value': str}
    return dataclass( frozen=True )(cls)

class BuildNumeric(object):
  def __init__(self,max_value=None,min_value=None,max_abs=None,min_abs=None):
    self.max_value = max_value
    self.min_value = min_value 
    self.max_abs = max_abs
    self.min_abs = min_abs 

  def __call__(self,cls):
    for x in ['max_value','min_value','max_abs','min_abs']:
      setattr( cls, '_' + x, self.__dict__[x] )
    cls.__annotations__ = {'value': (float,int,numpy.integer)}
    return dataclass( frozen=True, order=True )(cls)

class BuildItemClass(object):
  def __init__(self,attributes):
    self.attributes = attributes
  def __call__(self,cls):
    cls._attributes = {i.name:i for i in self.attributes}
    cls.__annotations__ = {i.name:i.type for i in self.attributes}
    return dataclass( frozen=True )(cls)


@dataclass(frozen=True)
class Delta(BaseDelta):
    name: str
    age: int
    extra: tuple = BaseDelta._UNSET_PARAMETER

    def x__post_init__(self):
        print( 'At post init %s' % self.name )

    def x__repeat_init__(self):
       print( 'returning %s from regitsry' % self.name)

@dataclass(frozen=True)
class BasicAttribute(BaseDelta):
    name: str
    description: str
    type: type = str

    def __child_init__(self,value):
        self.value = self.type(value)

    def __post_init__(self):
        assert self.name.find(' ') == -1

name = BasicAttribute( name='name', description='Name of a concept' )

td = TestData()

###
## breakdown in thought process here ,,,,
## need o get clearer about different objects ....
##
## the thing to be "formatted" is the container which maps value into the class instantiation
## the class associated with the attribute needs to be defined via the BuildItemClass decorator
##
## OR .. the first thing is to define the type (e.g. CV01) and then try instantiating, -- so this is going to be another dataclass with attribute and type
@BuildCVs(permitted_values=td.source_cv)
class NCCV01(BaseCV): 
    def format( self, other ):
         if type(other) == netCDF4.Dataset:
             this = getattr( nc, self.value )
             try:
               return self.type( this )
             except:
               print ('ERROR...')
               return None

  

@BuildCVs(permitted_values=['a','b','c'])
class CV01(BaseCV): pass

@BuildNumeric(min_abs=0.1)
class N01(BaseNumeric): pass

@BuildItemClass((BasicAttribute(name='x',description='an integer',type=int),))
class Item01(BaseItem): pass

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

##
## https://stackoverflow.com/questions/11014262/how-to-create-an-immutable-dictionary-in-python
## https://stackoverflow.com/questions/1151658/python-hashable-dicts
## can improve on this and aboe answers with the map mapper.
##
## it may in anycase be better to have __info__ as a tuple of BasicAttribute instances.
## don't really wnat to pass the info string anyway ... want something in the class, not in the instances ...
## BuildCVs does something similar .. adding attributes to the class before passing to dataclass.
##
class ImDict(dict):
    def __hash__(self):
        return id(self)

    def _immutable(self, *args, **kws):
        raise TypeError('object is immutable')

    __setitem__ = _immutable
    __delitem__ = _immutable
    clear       = _immutable
    update      = _immutable
    setdefault  = _immutable
    pop         = _immutable
    popitem     = _immutable

def ex01():

    x = InventoryItem( name='pen', unit_price=5, quantity_on_hand=5 )
    y = InventoryItem( name='pen', unit_price=5, quantity_on_hand=5 )
    print( 'x == y',x==y )
    print( 'x is y',x is y )

    print( '---- Delta ---- ' )

    ## RegistryArg approach is not working because of the way that the dataclass decorator sets 
    ## expected args of Delta.
    ##
    ##h = Delta( RegistryArg('info','An example'),name='Jones', age=10 )
    ##h = Delta( name='Jones', age=10, __info__=(('x','this')) )
    ##h = Delta( name='Jones', age=10, __info__={'x':'this'} )
    h = Delta( name='Jones', age=10 )
    print( '---- Delta ---- ' )
    i = Delta( age=10, name='Jones')
    print ('i is h',i is h)
    ee = {h:'a'}
    print( 'i from ee',ee.get( i, '__ not found __') )


ex01()
