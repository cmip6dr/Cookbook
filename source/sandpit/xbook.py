
class Dummy(object):
  nlev = 50
  sigma = [ 0.01 + 0.02*x for x in range( nlev ) ]
  sigma_bnds = [[x*0.02,(x+1)*0.02] for x in range( nlev ) ]


class Open(object):
  """Open a file object a write (or read?) a representation of the CF object"""

  def __init__(self,file,mode='w',fmt='cdml'):
    self.oo = open( file, mode )

    self.fmt = fmt
    self.mode = mode

  def write(self,obj):
    
class VariableTemplate(dict):
  attributes = dict()

class ContentTemplate(dict):
  variables = VariableTemplate()
  globals = dict()

class GridBase(object):
  _dimensions = ['nlev','nlat','nlon','nlevo']
  def __init__(self,grid):
    if grid not in self.grids:
      raise

    self.required = self.grids[grid].required
    self.defaults = self.grids[grid].defaults
    self.optional = self.grids[grid].optional
    self.load(mode='init')

  def config( self, **kwargs ):
    missing = [k for k in self.required if k not in kwargs]
    unwanted = [k for k in kwargs if not [k in self.required or k in self.optional]
    assert len(missing) == 0
    assert len(unwanted) == 0
    for k in kwargs:
      self.settings[k] = kwargs[k]
      if k in self.done:
        self.done.remove( k )
    self.load()
    
  def load(self,mode='add'):
    """Process required and default objects"""
    if mode == 'init':
      self.settings = {}
      self.done = set()
      for k in self.defaults:
        self.settings[k] = self.defaults[k]

    for k in self.settings:
      if k not in self.done:
        if k in self._dimensions:
          self.__class__.dimensions[k] = self.settings[k]
        elif k in self._anc..


  def cdml(self):
    """ ..... need a nice structure to go through these bits ...... """

    self.dimensions.cdml()
    self.class_arrays.cdml()
    self.arrays.cdml()
    self.class_globals.cdml()
    self.globals.cdml()
    self.class_data.cdml()
    self.data.cdml()
    


class Frame(object):
  """
  Usage: 
  #
  # generate a base class associated with your model name
  #
  MyBase = Frame().get( 'MyModel' )
  ## generate a set of grids
  grids = {x:MyBase(x) for x in ['latitude','longitude','standard_sigma','plev8'] }

  # this approach is not looking like dealing with bounds 
  grids['standard_sigma'].config( nlev=Dummy.nlev, levels=Dummy.sigma, bounds=Dummy.sigma_bnds )
  grids['standard_sigma'].cdml()
  """

  class GridTemplate(GridBase):
    pass

  def __init__(self,model_name):
    self.grids = dict()
    self.import_defs()
    self.model_name = model_name

  def get(self):
    GT = self.GridTemplate
    GT.grids = self.grids
    GT.__name__ = self.model_name

    return GT
