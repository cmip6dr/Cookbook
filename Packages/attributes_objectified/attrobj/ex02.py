# https://stackoverflow.com/questions/64361857/why-is-python-isinstance-transitive-with-base-classes-and-intransitive-with-me
class DataElementBase(object):
    def __init__(self,value):
        self.value = self.__initialisation_function__(value)

class MetaDataElement(type):
    def __new__(cls,name,initialisation_function, helptext ):
        result = type.__new__(cls,name,(DataElementBase,), dict(help=helptext) )
        result.__initialisation_function__  = staticmethod(initialisation_function)
        return result


###  test code  ####

# create a class from the metaclass
MyClass = MetaDataElement( 'myclass', float, "Value is obtained as float of user input" )

# create an instance of the class
my_instance = MyClass( '4.55' )

print ( 'MyClass is instance of MetaDataElement? %s' % isinstance( MyClass, MetaDataElement ) )
print ( 'MyClass is instance of DataElementBase? %s' % isinstance( MyClass, DataElementBase ) )
print ( 'my_instance is instance of MyClass? %s' % isinstance( my_instance, MyClass ) )
print ( 'my_instance is instance of MetaDataElement? %s' % isinstance( my_instance, MetaDataElement ) )
print ( 'my_instance is instance of DataElementBase? %s' % isinstance( my_instance, DataElementBase ) )
