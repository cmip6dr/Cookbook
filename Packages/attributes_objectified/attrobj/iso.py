from dataclasses import dataclass
from sandbox import Registry, REGISTRY_CLASSES_USED, SelfReference, BaseDelta, UnsetParameter
from typing import List, Set, Tuple, Dict

##
## ideas from iso standard on metadata registries
##

## registry element formed from "property", "object" and "data type".

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
