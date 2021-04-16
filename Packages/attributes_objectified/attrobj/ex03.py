# https://stackoverflow.com/questions/64361857/why-is-python-isinstance-transitive-with-base-classes-and-intransitive-with-me
##
## take at least two reloads to fully reload .. this was because of class definition order ... fails to import with this corrected.
##
class RootMethods(type):
###   something odd about inheritance of G ... cannot be sure which "cls" is used as the argument.
###   a lot of work to make this consistent over the generations.
    _root_methods_annotation = 'RootMethods'

    @classmethod
    def G(self):
        """Class method to return the generation index of a class"""
        return self.__G__[self]

    @classmethod
    def GX(self):
        """Class method to return the generation index of a class (GX)"""
        print (self, self.__name__, self.__generation__ )
        return self.__G__[self]

class MetaDataElement(type):
    __G__ = dict()
    __generation__ = 0

    def __new__(cls,name,initialisation_function, helptext ):
        print( """MetaDataElement.__new__: """ )
        ### order of bases matters here.
        ### 
        result = type.__new__(cls,name,(RootSelf,RootBase,RootMethods), dict(help=helptext) )
        result.__initialisation_function__  = staticmethod(initialisation_function)
        result.__G__[result] = 0
        return result

class RootSelf(type):

    def __call__(cls, *args, **kwargs):
        """RootSelf.__call__: can be used to work on arguments passed to init """
        print( """RootSelf.__call__: """ )
        print( super() )

        ## this call requires a type ... but can use for object in ChildBase.
        result = super().__call__(*args,**kwargs)
        result.__generation__ += 1
        if hasattr( result, '__G__'):
          result.__G__[result] = result.__G__.get(result.__class__,0) + 1

        result.value2 = args[0]
        return result

class ParentMethods(RootMethods):  pass

class RootBase(MetaDataElement):
    def __init__(self,value, check):
        print( """RootBase.__init__: """ )
        self.value = self.__initialisation_function__(value)
        self.check = check

## the signature for instantiation of Root is defined here
    def __new__(cls, value, check):
        print( """RootBase.__new__: """ )
        result = type.__new__(cls,'Parent',(ParentBase,ParentMethods), dict(comment='hello') )
        result.__G__[result] = result.__G__[result.__class__] + 1
        result.__generation__ += 1
        return result


class ParentBase(RootBase):
    """Base class for Parent generation (i.e. provides interface to instantiate from Parent to Child)"""
    def __init__(self,value):
        print( """ParentBase.__init__: """ )
        self.value = value

## the signature for instantiation of Parent is defined here
    def __new__(cls, *args, **kwargs):
        print( """ParentBase.__new__: """ )
        result = type.__new__(cls,'Child',(ChildBase,ChildMethods), dict(comment='hello') )
        result.__G__[result] = result.__G__.get(result.__class__,0) + 1
        result.__generation__ += 1
        return result

class ParentSelf(type):

    def __call__(cls, *args, **kwargs):
        """ParentSelf.__call__: can be used to work on arguments passed to init:
            Placing call here, rather than in ParentBase, prevents inheritance and
            avoids conflicts in instantiation of descendants."""
        print( """ParentSelf.__call__: """ )


        ## this call requires a type ... but can use for object in ChildBase.
        result = super().__call__(*args,**kwargs)
        result.__generation__ += 1
        if hasattr( result, '__G__'):
          result.__G__[result] = result.__G__.get(result.__class__,0) + 1

        if result.__generation__ == 1:
          ## check on generation prevents spurious execution in Child instances 
          print( """ParentSelf.__call__.actions: """ )
          result.value2 = args[0]
        
        return result

class ChildMethods(object):

    #
    # if Child accesses __class__.G implicitly it returns the gneration of the parent
    # need an indirect approach here
    #
    @classmethod
    def G(cls):
        """ChildMethods.G: Method to return the generation index of a class"""
        return cls.__class__.G()+ 1

class ChildBase(object):
    def __init__(self,value,petname=None):
        print( """GC.__init__: """  )
        self.value = value
        self.petname = petname
        self.__name__ = 'Child_00'

        self.G = self.GG 

##
## declaring G here does not create a working function .. possibly some name-space conflict with the classmethod declared in 
## ChildMethods
##
    def GG(self):
        """ChildBase.GG: Method to return the generation index of a class"""
        return self.__class__.G()+ 1

    def __call__(cls, *args, **kwargs):
        """ChildBase.__call__: """
        print( """ChildBase.__call__: """ )
        #
        result = super().__call__(*args,**kwargs)
        result.__name__ = 'gc'
        
        return result

class ChildBase0(ParentBase):
    """Base class for Child generation (i.e. provides interface to instantiate from Parent to Child)"""
    def __init__(self,value):
        print( """Child.__init__: """ )
        self.value = value

    def __xxxnew__(cls, *args, **kwargs):
        print( """Child.__new__: """ )
        #value = cls.__initialisation_function__(args[0])
        result = type.__new__(cls,'GC',(GCBase,), dict(comment='welcome') )
        result.__G__[result] = result.__G__.get(result.__class__,0) + 1
        result.__generation__ += 1
        return result

    def __call__(cls, *args, **kwargs):
        """Child.__call__: """
        print( """Child.__call__: """ )
        #
        result = super().__call__(*args,**kwargs)
        result.__generation__ += 1
        result.Child_value = args[0]
        result.__name__ = 'gc'
        
        return result

###  test code  ####

# create a class from the metaclass
print( '#### -> MyClass' )
Root = MetaDataElement( 'Root01', float, "Value is obtained as float of user input" )

# create an instance of the class
print( '#### -> Parent' )
Parent = Root( '4.55', 'check_value' )
print( '#### -> Child' )
Child = Parent( 3. )
print( '#### -> gc' )
gc = Child( 5. )

def has_rma( obj ):
    a = '_root_methods_annotation'
    x = {True:'has', False:'does not have'}[hasattr(obj,a)]
    print( '%s %s attribute %s' % (obj.__name__,x,a) )

print ( 'Root is instance of MetaDataElement? %s' % isinstance( Root, MetaDataElement ) )
print ( 'Parent is instance of Root? %s' % isinstance( Parent, Root ) )
print ( 'Parent is instance of MetaDataElement? %s' % isinstance( Parent, MetaDataElement ) )
print ( 'Parent is instance of ParentBase? %s' % isinstance( Parent, ParentBase ) )
print ( 'Child is instance of Parent? %s' % isinstance( Child, Parent ) )
print ( 'Child is instance of ChildBase? %s' % isinstance( Child, ChildBase ) )
print ( 'gc is instance of Child? %s' % isinstance( gc, Child ) )
print ( 'gc is instance of Root? %s' % isinstance( gc, Root ) )
print ( 'gc is instance of Parent? %s' % isinstance( gc, Parent ) )
for obj in [Root,Parent,Child,gc]:
      has_rma( obj )
