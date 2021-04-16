
import collections, dataclasses, types
from dataclasses import dataclass
from sandbox import Registry, registry_arg_helper

NT = collections.namedtuple( 'nt', ['name','type','default'] )
REGISTRY_CLASSES_USED = set()

class NoDefault: pass


def create_registry_type( name, bases, attributes):
    annotations = {x.name:x.type for x in attributes}
    attr = dict( __annotations__=annotations )
    for x in attributes:
        if x.type != NoDefault:
            attr[x.name] = x.default

    this = type( name, bases, attr )
    return dataclass(frozen=True)(this)

class RegistryFactory(object):
    """A Factory to generate classes for registry items.
    
    Initialisation
    --------------
    rf = RegistryFactory( bases : tuple ) # creates a factory instance
           # rf = RegistryFactory( (object,) ) 

    RegistryClass = rf( attributes ) # creates a class
            # RC_mip_variable = rf( (name,title,description,standard_name,units,type,rdf) )
            # with name = NT_attr( ['name','Name of a concept', .....] )

    registry_item = RegistryClass( k1=v1, k2=v2, k3=v3 ) # creates a registry item as a class instance.
            # e.g.  tas = RC_mip_variable( 'tas','Near-surface Air Temperature', ' ...', ... )

    :bases: a tuple of base classes
    :attributes: a tuple of elements, each specifying an attribute, eg. as namedtuple instances.
    :k1,k2,k3: the expected arguments are specified by a1.name, a2.name, etx, where a1, a2 are elements of *attributes*.

    Would be good to have "rf" above as a class rather than a function.
    ... RF_operational : Callable[ tuple ] -> RF_operational
    i.e. RF_operational produces an instance of itself.

    """
    def __init__(self, bases : tuple, ):
        self.products = dict()
        self.input_bases = bases

##https://stackoverflow.com/questions/66222211/how-to-pass-class-keyword-arguments-with-the-type-built-in-function
##
## executes Registry.__call__
        Base = Registry( 'Base', bases, dict( _registry = dict(), _registry_info = dict() ) )
        self.bases = (Base, )
        self.ibases = ( Registry( 'InfoBase', bases, dict( _registry = dict()) ), )

    def make_instance_doc(self,attributes):
      """Creates a dataclass instance holding all the attribute definitions""" 
      attr = {x.name:x for x in attributes}
      annotations = {x.name:type(x) for x in attributes}
      This = dataclass()(type( 'doc', self.ibases, dict(__annotations__=annotations) ))
      return This(**attr)

    ##def __new__(cls, name, bases, dct ): 
        ##print( "xxxx" )
        ##obj = super(RegistryFactory, cls).__new__(cls,name,bases,dct)
        ##print('__new__ called. got new obj id=0x%x' % id(obj))
        ##return obj


    def __call__( self, name, attributes):
      print( 'RegistryFactory.__call__' )
      try:
          h = (name, self.bases, attributes) 
          if h in self.products:
              return self.products[h]
      except:
          h = None

      annotations = {x.name:x.type for x in attributes}
      attr = dict( __annotations__=annotations )


      for x in attributes:
        if x.type != NoDefault:
            attr[x.name] = x.default

      attr['__idoc__'] = self.make_instance_doc( attributes )
      attr['__factory__'] = self

      this = type( name, self.bases, attr )
      instance = dataclass(frozen=True)(this)
      self.products[h] = instance
      return instance

def make_instance_doc(self,attributes):
      """Creates a dataclass instance holding all the attribute definitions""" 
      attr = {x.name:x for x in attributes}
      annotations = {x.name:type(x) for x in attributes}
      This = dataclass()(type( 'doc', self.ibases, dict(__annotations__=annotations) ))
      return This(**attr)

class RegistryFactory_Generator(type):
    """Adapted from RegistryFactory ... trying to get a class rather than a callable.
    rf = RegistryFactory_Generator( name, bases, body ) # creates a factory instance


    ... first step is to adapt creae_registry_type



    .......................................
    
    Initialisation
    --------------
    rf = RegistryFactory( bases : tuple ) # creates a factory instance
           # rf = RegistryFactory( (object,) ) 

    RegistryClass = rf( attributes ) # creates a class
            # RC_mip_variable = rf( (name,title,description,standard_name,units,type,rdf) )
            # with name = NT_attr( ['name','Name of a concept', .....] )

    registry_item = RegistryClass( k1=v1, k2=v2, k3=v3 ) # creates a registry item as a class instance.
            # e.g.  tas = RC_mip_variable( 'tas','Near-surface Air Temperature', ' ...', ... )

    :bases: a tuple of base classes
    :attributes: a tuple of elements, each specifying an attribute, eg. as namedtuple instances.
    :k1,k2,k3: the expected arguments are specified by a1.name, a2.name, etx, where a1, a2 are elements of *attributes*.

    Would be good to have "rf" above as a class rather than a function.
    ... RF_operational : Callable[ tuple ] -> RF_operational
    i.e. RF_operational produces an instance of itself.

    """
    def __xx__init__(self, bases : tuple, ):
        self.products = dict()
        self.input_bases = bases

##https://stackoverflow.com/questions/66222211/how-to-pass-class-keyword-arguments-with-the-type-built-in-function
### executes Registry.__call__ and returns an instance of Registry.
        Base = Registry( 'Base', bases, dict( _registry = dict(), _registry_info = dict() ) )
        self.bases = (Base, )
        self.ibases = ( Registry( 'InfoBase', bases, dict( _registry = dict()) ), )

    def make_instance_doc(self,attributes):
      """Creates a dataclass instance holding all the attribute definitions""" 
      attr = {x.name:x for x in attributes}
      annotations = {x.name:type(x) for x in attributes}
      This = dataclass()(type( 'doc', self.ibases, dict(__annotations__=annotations) ))
      return This(**attr)

    def __new__(cls, name, bases, dct ):
        """RegistryFactory_Generator.__new__ .. create a RegistryFactory"""
        print( "xxxx" )
        Base = Registry( 'Base', (object,), dict( _registry = dict(), _registry_info = dict() ) )
        # type(Base) = Registry
        dct['ibases'] = ( Registry( 'InfoBase', (object,), dict( _registry = dict()) ), )
        dct['bases'] = (Base,)
        dct['products'] = dict()
        dct['make_instance_doc'] = make_instance_doc
        ##obj = super(RegistryFactory_Generator, cls).__new__(cls,name,(RegistryFactory_Generator_Base,),dct)
        obj = type.__new__(cls,name,(RegistryFactory_Generator_Base,),dct)
       ## obj = type( name,(RegistryFactory_Generator_Base,),dct)
        ##print('__new__ called. got new obj id=0x%x' % id(obj))
        return obj


class RegistryFactory_Generator_Base(type):


    ### getting stuck here ... instantiated class tries to execute new .....
    ##
    ## override type.__init__
    ##
    def __init__(self,*args,**kwargs):
        print( 'RegistryFactory_Generator_Base.__post_init__' )

    ## override 
    ## change in signature does not feel comforatable
    ## causes problems with smooth sub-classing ...
    def __new__( cls, name, attributes):
      """RegistryFactory_Generator_Base.__new__: Create a new object"""
      print( 'RegistryFactory_Generator_Base.__new__' )
      print( cls.__name__, cls.__class__ )
      try:
          h = (name, cls.bases, attributes) 
          if h in cls.products:
              return cls.products[h]
      except:
          h = None

      annotations = {x.name:x.type for x in attributes}
      attr = dict( __annotations__=annotations,  _registry = dict(), _registry_info = dict() )


      for x in attributes:
        if x.type != NoDefault:
            attr[x.name] = x.default

      attr['__idoc__'] = make_instance_doc( cls, attributes )
      attr['__factory__'] = cls

      this = type( name, cls.bases, attr )
      print( type(this), type(this) == type(cls.bases[0]), type(cls))
      ## this is an instance of Registry but inherits from base,
      ## see also https://stackoverflow.com/questions/64361857/why-is-python-isinstance-transitive-with-base-classes-and-intransitive-with-me
      
      ## with this version, instance is an instance of cls
      ## attributes added to cls.bases are lost ... 
      ## see inheritance rules ....
      ## also loses call to Registry.__new__
      this = type.__new__(cls,name,(object,),attr)
      ##bases = cls.mro() ## does not work ... 
      ##print( bases )
      ## cls has metaclass RegistryFactiry_Genrator_Base
      ##this = type.__new__(cls,name,(Mobject,),attr)
      ##this = types.new_class(name, (object,), {'metaclass':Registry_L2}, exec_body=lambda d: d.update(**attr))
      print( 'INFO.901: ',type(this), type(this) == cls)
      ##this = type('xxxx',self.bases, attr)
      instance = dataclass(frozen=True)(this)
      cls.products[h] = instance
      return instance

class Registry_L2(RegistryFactory_Generator_Base):
    """Metaclass designed to enable creation of classes which which maintain a registry of instances"""

    def __Registry__(self):
        print( '__Registry__: a method from the sandbox.Registry metaclass' )

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
            print( 'INFO.601: ',cls.__name__,type(cls))
            this_instance = super(Registry, cls).__call__(*args, **kwargs)
            if self_ref != None:
                setattr( this_instance, self_ref, this_instance )

            cls._registry[h] = this_instance

            if hasattr( cls, '_registry_info' ):
               cls._registry_info[id(this_instance)] = dict( __creation__=(Registry, '__call__', (cls,args,kwargs), time.ctime()) )
            if hasattr( this_instance, '__post_init__' ):
               this_instance.__post_init__()

        ## if the hash is found, retrieve existing instance.
        ## there is an optional call to the __repeat_init__ method, of present. This method could be used for
        ## logging etc, but should not modify the instance.
        else:
            this_instance = cls._registry[h]
            if hasattr( this_instance, '__repeat_init__' ):
               this_instance.__repeat_init__()

class MMeta(Registry,RegistryFactory_Generator): pass

##class Mobject(object,metaclass=Registry_L2):pass


sn = NT(name='standard_name',type=str,default=NoDefault)
units = NT(name='units',type=str,default=NoDefault)
name = NT(name='label',type=str,default='NAME UNSET')

var = create_registry_type( 'Var', (object, ), (name,sn, units) )

##
## creates an instance of RegistryFactory ... 
print( 'RegistryFactory --> rf' )
# initialise ...
rf = RegistryFactory( (object,) )
print( 'RegistryFactory --> rf', type(rf) )
# run __call__
V2 = rf( 'Var2', (name,sn, units)  )
print( 'rf --> V2 OK',type(V2))
tas = V2( 'ta', 'air_temperature', 'K' )
# run __new__
rf_obj = RegistryFactory_Generator( 'rf_obj', (Registry,), dict( ex01_attr='x') )
try:
    ## this executes __call__ ... there is no instantiation
    ## need 3 args to trigger call to __new__ from type.__init__
    ##
    ## this error not reproduce ....
    ##
    ## can avoid this by overriding type.__init__ ... but is change in signature OK?
    ##
    ## this works wxcept that V2b is an instance of sandbox.Registry, not of rf_obj
  V2b = rf_obj( 'V2b', (name,sn, units)  )
  print( 'rf_obj --> V2b OK',type(V2b))
except:
  print( 'FAILED to instantiate V2b' )
  raise
try:
    ## this executes __call__ ... now appears as instantiation .. by chnage to __new__
  tas_b = V2b( 'ta', 'air_temperature', 'K' )
  tas_b2 = V2b( 'ta', 'air_temperature', 'K' )
except:
  print( 'FAILED to instantiate tas_b' )
  raise
