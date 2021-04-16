from dataclasses import dataclass
from sandbox import Registry, REGISTRY_CLASSES_USED, SelfReference, BaseDelta, UnsetParameter
from typing import List, Set, Tuple, Dict
import time

##
## ideas from iso standard on metadata registries
##

## registry element formed from "property", "object" and "data type".

##
## instantiation is an event ... in EIC (ISO 19440) an event is represented in terms of date and ownership and links to an Enterprise Objects via Object Views.
## relavant Objects are the Factory and its arguments. If "type" is used, these would be "name", "bases" and "attributes".
##
## pythonic instantiation expresses attributes as key-value pairs, with the key expressed as a token.
##    "key" can be generalised to a instance combining name etc ... and 
##    ---- this will allow the pythonic interface to be used. 
## but don't want to be passing the full details of the keys at the instantiation .. should be enough at the definition.
##

### e.g. name = BasicAttribute( name='Name of an Object', description='...', type='str', xx='skos:techLabel' )
### Rclass = rclass_gen( 'Rclass', (RecordBase,), {attributes=(name,)} )

### The entreprise object here is a class factory together with arguments.
###  Event = Factory execution, -- Factory + arguments + output

### orchestration vs. factory execution ... since everying thing is a function or everything is a class .. how do we distinguish between execution and orchestration?
## in python, it may make sense to consider the module as the orchestration : The module load typically creates a set of classes.
## "orchestration" is a sys. admin word .. may be better to avoid.
##

## need __class__ .. the parent class, 

## object is created by an event ..

class BaseEvent(object):
    def run(self):
        self.product = self.factory( *self.args )
        self.timestamp = time.ctime()

@dataclass
class Event(BaseEvent):
    """In the MDR context, rather than executing the factory and then documenting it, we place the factory and argumenst in an object, and then execute then call the factory a to create the output."""
    factory = object
    args  = tuple



class RegistryProperty(object,metaclass=Registry):
    _registry = dict()

class RegistryObject(object,metaclass=Registry): 
    _registry = dict()

class RegistryType: pass

@dataclass
class BasicRegistryProperty(RegistryProperty):
    name: str
    description: str

##
## putting parameter descriptions in the doc string works.
##
## if we use MyType('BasicRegistryObject', (RegustryObject,), dict( .... ) ) there would be the option of getting label
## type and decsription out of an object .... but might fool sphinx.
##
## alternatively, a pre-processing step could be used to autogenerate the class definitions
##
@dataclass
class BasicRegistryObject(RegistryObject):
    """Define a simple registry object.

    - **parameters**, **types**, **return** and **return types**::

          :param name: The name of the object
          :param description: A description of the object.

          :Example:

          x = BasicRegistryObject(name='FileAttribute',description='An attribute in a data file' )
    """
    name: str
    description: str
    object: object

Unset = UnsetParameter


##
## reloading will create a new Identifier type, potentially creating confusion. 
## for this system to be robust, these classes need to be protected from reloads 
##
@dataclass(frozen=True)
class Identifier(BaseDelta):
    id: str

@dataclass
class LanguageIdentifier(BaseDelta):
    identifier: str = 'en-us'

@dataclass
class Notation(BaseDelta):
    name: str
    description: str = Unset

@dataclass
class Organization(BaseDelta):
    name: (str,list)
    email_address: (str,List) = Unset
    uri: str = Unset

@dataclass
class DocumentType(BaseDelta):
    identifier: str = Unset
    description: str = Unset
    scheme_reference: str = Unset

@dataclass
class ReferenceDocument(BaseDelta):
    id: Identifier
    description: DocumentType
    language_identifier: LanguageIdentifier
    title: str
    notation: Notation = Unset
    uri: str = Unset
    provider: Organization = Unset

@dataclass
class RDT(BaseDelta):
    name: str
    description: str
    reference_document: ReferenceDocument
    annotation: str = Unset

website = DocumentType(identifier='this:DocumentType:website',description='An online resource accessible through a browser, designed to be human readable', scheme_reference='html')
en = LanguageIdentifier()

nota = Notation(name='1.8', description='version')
cf_ref_doc = ReferenceDocument( id=Identifier( 'cfconventions_1.8' ), description=website, language_identifier=en,
                title='NetCDF Climate and Forecast (CF) Metadata Conventions', notation=nota,
                uri='http://cfconventions.org/Data/cf-conventions/cf-conventions-1.8/cf-conventions.pdf',
                provider=Organization( name='CF Conventions', uri='http://cfconventions.org' ) )


@dataclass
class RegistryElement(object):
    property: RegistryProperty
    object: RegistryObject
    type: (RegistryType, type)

##@dataclass
##
## 
class RegistryType(type):
    property: RegistryProperty
    object: RegistryObject
    type: (RegistryType, type)
