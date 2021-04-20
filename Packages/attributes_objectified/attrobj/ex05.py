"""Working example showing simple construction of an instantiation tree"""

## Next steps: think about different flavours.
## if everything is created as an instance of the apex class, the apex class must impose little or no constraint.
##
## E.g. SB = type.__new__( NewBase, 'SB', (OtherAbstract,), dict() ) works and SB is an instance of NewBase.
## class A(SB):
##.   def __init__(self): pass
##
## generates warnings from unwanted parts of NewBase
##
## a = A() works OK.




class SomeAbstract(type):
    some_abstract_value = 9.
    def some_abstract_method(self):
        print( 'Hello from SomeAbstract.some_abstract_method' )


class OtherAbstract(object):
    other_abstract_value = 9.
    def other_abstract_method(self):
        print( 'Hello from OtherAbstract.other_abstract_method' )


class NewBase(type):
    __G__ = dict()
    __generation__ = 0

    def __new__(cls,name,dummybases,body_input ):
        print( """NewBase.__new__: %s -> %s""" % (cls,name) )

        body = cls.__interface__(body_input)
        bases = cls.__base_interface__(dummybases)

        result = type.__new__(cls,name,bases, body )
        result.__generation__ = cls.__generation__ + 1
        return result

    @classmethod
    def __interface__(cls,body):
        expected = {'n':str, 'y':int}
        for k,t in expected.items():
            if k not in body:
                print( 'WARNING [%s] interface: expected  key %s not in body' % (cls,k ) )
            elif type( body[k] ) != t :
                print( 'WARNING [%s] interface: value [%s,%s] of key %s is not expected type' % (cls,body[k],type(body[k]),k ) )
        return body

    @classmethod
    def __base_interface__(cls,bases):
        if len(bases) == 0:
          if cls.__generation__ == 0:
            bases = (NewBase,)
          else:
            bases = cls.__bases__
        elif len(bases) == 1 and bases[0] == None:
            bases = tuple()
        return bases


print( '--> Ancestor')
Ancestor = NewBase('Ancestor',tuple(),dict(n='Sarah',y=1506))
print( '\n--> Next')
Next = Ancestor('Next',tuple(),dict(n='Jane',y=1536))

print( '\n--> G2a')
G2a = Next('G2a',tuple(),dict(n='Mary',y=1551))

print( '\n--> G2b')
G2b = Next('G2b',tuple(),dict(n='Ann',y=1553))

print( '\n--> G3aa')
G3aa = G2a('G3aa',tuple(),dict(n='Dot',y=1584))
G3ba = G2b('G3ba',tuple(),dict(n='Phylis'))
G3bb = G2b('G3bb',tuple(),dict(n='Anna',y='1584'))

G3ab = G2a('G3ab',(None,),dict(n='Greta',y=1587))

#Ancestor = Root('Ancestor',dict(n='Sarah',y=1506))
