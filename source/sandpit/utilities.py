import collections, uuid, re, json
from dreqPy import dreq
from dreqPy.extensions import collect
##
## supported in python3.5 on laptop .....
import netCDF4
import cfdm
import numpy

class VariableTemplateNC4(netCDF4._netCDF4.Variable):
    nc4Help = '''createVariable(self, varname, datatype, dimensions=(), zlib=False,
    complevel=4, shuffle=True, fletcher32=False, contiguous=False, chunksizes=None,
    endian='native', least_significant_digit=None, fill_value=None)'''

class Constraints(object):
  def __init__(self,dd):
    pass

class FormulaTerms(object):
  def __init__(self,ancestor):
    self.ancestor = ancestor
    self.terms = {"atmosphere_ln_pressure_coordinate":('=p0','-lev'),
                  "atmosphere_sigma_coordinate":('-sigma','=ps','=ptop'),
                  "atmosphere_hybrid_sigma_pressure_coordinate":{'a':('-a','-b','=p0','=ps'),'ap':('=ap','-b','=ps')},
                  "atmosphere_hybrid_height_coordinate":('=a','-b','=orog'),
                  "atmosphere_sleve_coordinate":('-a','-b1','-b2','=ztop','=zsurf1','=zsurf2','@ztop_name')}

    self.termData = {'ztop':'Height of top of model, see %s: formula_terms and formula', 
                     'ptop':'Pressure at top of model, see %s: formula_terms and formula', 
                     'zsurf1':'Large scale component of orography, see %s: formula_terms and formula',
                     'zsurf2':'Small scale component of orography, see %s: formula_terms and formula',
                     'orog':'Orography, see %s: formula_terms and formula',
                     'lev':'Dimensionless height coordinate, see %s: formula_terms and formula',
                     'sigma':'Dimensionless height coordinate between 0 and 1, see %s: formula_terms and formula',
                     'ps':'Surface pressure, see %s: formula_terms and formula',
                     'p0':'Reference surface pressure, see %s: formula_terms and formula',
                      }
                  

    self.zarray = set( [ 'lev','sigma','a','b','ap','b','b1','b2'] )
    self.scalar = set( [ 'p0'] )

    self.optionDefaults = {"atmosphere_hybrid_height_coordinate":'altitude' }
    self.sn = {"atmosphere_hybrid_height_coordinate":{
                     'formula':'z(n,k,j,i) = a(k) + b(k)*orog(n,j,i)',
                     'altitude':{'orog':'surface_altitude', 'csn':'altitude'},
                     'datum':{'orog':'surface_height_above_geopotential_datum', 'csn':'height_above_geopotential_datum'} },
               "atmosphere_ln_pressure_coordinate":{'p0':'reference_air_pressure_for_atmosphere_vertical_coordinate air_pressure'},
               "atmosphere_sigma_coordinate":{
                      'csn':'air_pressure',
                      'formula':'p(n,k,j,i) = sigma(k)*ps(n,j,i)',
                      'ps':'surface_air_pressure',
                      'ptop':'air_pressure_at_top_of_atmosphere_model' }
              }


  def formula_class_factory(self,name,opt=None):
    class Base(object):
      def __init__(self,parent_info,**kwargs):
        assert len( kwargs.keys() ) == len( self.required ), 'Arguments missing'
        req = set( self.required.keys() )
        d = req.difference( set( kwargs.keys() ) )
        assert len( d ) == 0, 'Arguments missing'

        self.parent_info = parent_info
        self.zdc = parent_info['z_dc']

        self.pp = {}
        for x,v in kwargs.items():
          if self.re1.search( x ):
            pass
          else:
            this = {}
            this['label'] = x
            properties = {}
            if v.__class__ == Ldp:
              this['data'] = v.data
              properties = v.properties
              if v.label != None:
                this['label'] = v.label
            else:
              this['data'] = numpy.array( v, dtype=parent_info['dtype'])

            if self.required[x]['unitsKey'] == '=':
              properties['units'] = parent_info['units']
            elif self.required[x]['unitsKey'] == '-':
              properties['units'] = '1'

#
# ugly logic here to extract standard name of parameters dependent in options.
#
# this would be better placed in the class factory.
#
            ##csn = None
            if x in self.sn:
              if type( self.sn[x] ) == type( 'x' ):
                ss = self.sn[x]
                ##if ss.find( ' ' ) != -1:
                  ##ss,csn = ss.split()
              elif self.opt in self.sn and x in self.sn[self.opt]:
                ss = self.sn[self.opt][x]
                ##assert '%s_name' % x in kwargs
                ##ss = kwargs[ '%s_name' % x ]
                ##assert ss in self.sn[x]
                ##if type( self.sn[x] ) == type( {} ):
                  ##csn = self.sn[x][ss]
              properties['standard_name'] = ss
              ##self.computed_standard_name = csn

            properties['long_name'] = self.termData.get( x, '%s, see %%s: formula_terms and formula' % x ) 
            this['properties'] = properties
            self.pp[x] = this
 
      def set(self,f):
        zdcc = self.ancestor.constructs()[self.zdc]
        try:
          zaxn = zdcc.nc_get_variable()
        except:
          print ( dir( zaxc ) )
          raise
        dc = dict()
        vname = f.nc_get_variable()
        for x,this in self.pp.items():
          properties=this['properties']

          if 'long_name' in properties and properties['long_name'].find( '%s' ) != -1:
              properties['long_name'] = properties['long_name'] % zaxn

          domain_ancillary = cfdm.DomainAncillary(
                               properties=this['properties'],
                               data=cfdm.Data( this['data'] ) )

          if 'label' in this:
              domain_ancillary.nc_set_variable( this['label'] )

          if x in self.zarray:
            dom_construct = f.set_construct(domain_ancillary, axes=[self.parent_info['z_axis'],])
          else:
            dom_construct = f.set_construct(domain_ancillary, axes=self.parent_info['other_axes'])

          dc[x] = dom_construct


        # Create the datum for the coordinate reference constructs
        datum = cfdm.Datum(parameters={'earth_radius': 6371007.})

        # Set the netCDF name for a grid mapping variable that might be created from this datum
        datum.nc_set_variable('datum')
        print (dc)
        coordinate_conversion_v = cfdm.CoordinateConversion(
                   parameters={'standard_name': self.name,
                               'computed_standard_name': 'altitude'},
                           domain_ancillaries=dc )

        self.coordinate_conversion_v = coordinate_conversion_v
        datum = cfdm.Datum(parameters={'earth_radius': 6371007.})

        ##coordinate_conversion_h = cfdm.CoordinateConversion()
        ##horizontal_crs = cfdm.CoordinateReference( datum=datum, coordinate_conversion=coordinate_conversion_h, coordinates=[])

        vertical_crs = cfdm.CoordinateReference(
                 datum=datum,
                 coordinate_conversion=coordinate_conversion_v,
                 coordinates=[self.parent_info['z_dc']])

##
## not working
## issue reproduced in ex03 (by deleting horizontal_crs call
## github issue raised in cfdm repo
##
        ##f.set_construct(horizontal_crs)
        f.set_construct(vertical_crs)

      def dumpJ(self,fname):
        oo = open( fname, 'w' )
        ppo = dict()
        for k,v in self.pp.items():
          ee = dict()
          for kk in v:
            if kk == 'data':
              ee[kk] = str( type( v[kk] ) )
            else:
              ee[kk] = v[kk]
          ppo[k] = ee
    
        self.ppo = ppo
        json.dump( ppo, oo, indent=4, sort_keys=True )
        oo.close()
                  
    assert name in self.terms
    if name == "atmosphere_hybrid_sigma_pressure_coordinate":
      assert opt in ['a','ap']
      required = { x[1:]:{'unitsKey':x[0]}  for x in self.terms[name][opt] }
    else:
      required = { x[1:]:{'unitsKey':x[0]}  for x in self.terms[name] }
    
    Base.re1 = re.compile( '_name$' )
    Base.required = required
    Base.sn = self.sn[name]
    Base.zarray = [x for x in self.zarray if x in required]
    Base.termData = self.termData
    Base.ancestor = self.ancestor.f
    Base.name = name
    
    if opt == None and name in self.optionDefaults:
       opt = self.optionDefaults[name]
    Base.opt = opt

    if 'csn' in Base.sn:
      Base.computed_standard_name = Base.sn['csn']
    elif opt in Base.sn:
      Base.computed_standard_name = Base.sn[opt]

    return Base

class Ldp(object):
  def __init__(self,label,data,properties={}):
    self.label = label
    self.data = data
    self.properties = properties

ldp = Ldp('dummy',[0.,1.])

class Field(object):
  __extra__ = dict()

  def __init__(self,**kwargs):
  
##
## tried making this a sub-class of Field ... but it messed up something in the cfdm.write() methods.
## Something must be keyed on "Field..." .. perhaps on copy of construct ...
##
    self.f = cfdm.Field( kwargs )
    ##super(Field, self).__init__(kwargs)
    ##self.f = self

  def _dim_coord( self, label, data, properties = {}, bounds=None, formula_data=None ):
    bnds = False
    if bounds != None:
      if type(bounds) in [type(x) for x in [[],set()]]:
         bnds = 'data'
      elif bounds.__class__ == Ldp:
         bnds = 'full'
      else:
          assert False, 'bounds value invalid type'

##    if formula_data != None:

    cfdata = cfdm.Data( data ) 
    if not bounds:
      dc = cfdm.DimensionCoordinate( data = cfdata, properties = properties)
    else:
      if bnds == 'full':
         bnds_construct=cfdm.Bounds( data=cfdm.Data(bounds.data), properties=bounds.properties)
         bnds_construct.nc_set_variable(bounds.label)
      else:
         bdat = cfdm.Data(bounds)
         bnds_construct=cfdm.Bounds( data=bdat )
      dc = cfdm.DimensionCoordinate( data = cfdata, properties = properties, bounds=bnds_construct)

    axis = cfdm.DomainAxis(dc.data.size)
    ##axis.nc_set_dimension( label )
    dc.nc_set_variable( label )
    axis_tag = self.f.set_construct(axis)
    dim = self.f.set_construct(dc, axes=axis_tag)
    return (dc, axis_tag, axis, dim )

  def defaults01(self,heightCoord="atmosphere_hybrid_height_coordinate", aux='altitude'):
    fac = FormulaTerms(self )
    F1 = fac.formula_class_factory( heightCoord, opt=aux )
    
    dc_time, axis_t, axis_time, dim_time = self._dim_coord( 'time',
                numpy.array( [1.,], dtype='double'),
                properties = {'standard_name':'time', 'units':'days since 2000-01-01 00:00:00', 'calendar':'gregorian'} )
                

    dc_lat, axis_la, axis_lat, dim_lat = self._dim_coord( 'lat',
                      numpy.arange(9.,  dtype='double' ),
                      properties={'standard_name': 'latitude', 'units': 'degrees_north'})


    dc_lon, axis_lo, axis_lon, dim_lon = self._dim_coord( 'lon',
                          numpy.arange(9.,  dtype='double' ),
                          properties={'standard_name': 'longitude', 'units': 'degrees_east'} )

##
## ## logic of program flow is messed up here .... orog_name is passed to F1 below, along with axis_zz which is generated
## by call to _dim_coord ...
##    but ... want the computed standard name ... which depends on orog_name ....
##

    if heightCoord == "atmosphere_hybrid_height_coordinate":
      csn = F1.computed_standard_name
      zprop = {'computed_standard_name': csn, 'standard_name': heightCoord}

    if 'formula' in F1.sn:
       zprop['formula'] = F1.sn['formula']

    dc_z, axis_zz, axis_z, dim_z = self._dim_coord( 'lev',
                          numpy.arange(3.,  dtype='double' ),
                          properties=zprop )

    if heightCoord == "atmosphere_hybrid_height_coordinate":
      nn = dc_lat.data.size*dc_lon.data.size
      o = Ldp( 'orog',numpy.array( range(nn), dtype='float' ).reshape(dc_lat.data.size,dc_lon.data.size),
                       properties={'long_name':'Orographic Height'} )

      self.formula_info = F1({'units':'m', 'dtype':'double',
                              'other_axes':[axis_la, axis_lo],'z_axis':axis_zz,'z_dc':dim_z},
                      orog=o, a=[0,0.5,1.], b=[0,.1,.2] )

    self.f.set_data(cfdm.Data(numpy.arange(243.).reshape(1,3,9, 9)),
             axes=[axis_t, axis_zz, axis_la, axis_lo])
    self.f.nc_set_variable( 'tas' )

    self.formula_info.set( self.f )
    axis_z.nc_set_dimension( 'height' )

    self.f.set_properties( {'project': 'research',
                    'standard_name': 'air_temperature', 'units': 'K'} )

    return (dc_time, dc_lon, dc_lat,self.formula_info.coordinate_conversion_v)

  def defaults(self):

    dc_time, axis_t, axis_time, dim_time = self._dim_coord( 'time',
                numpy.array( [float(x) for x in range(2)], dtype='double'),
                properties = {'standard_name':'time', 'units':'days since 2000-01-01 00:00:00'} )
                

    dc_lat, axis_la, axis_lat, dim_lat = self._dim_coord( 'lat',
                      numpy.arange(9.,  dtype='double' ),
                      properties={'standard_name': 'latitude', 'units': 'degrees_north'})


    dc_lon, axis_lo, axis_lon, dim_lon = self._dim_coord( 'lon',
                          numpy.arange(9.,  dtype='double' ),
                          properties={'standard_name': 'longitude', 'units': 'degrees_east'} )

    self.f.set_data(cfdm.Data(numpy.arange(162.).reshape(2,9, 9)),
             axes=[axis_t, axis_la, axis_lo])

    self.f.set_properties( {'project': 'research',
                    'standard_name': 'air_temperature', 'units': 'K'} )

    return (dc_time, dc_lon, dc_lat)

class WrapNetCDF4(netCDF4.Dataset):
  """Wraps the NetCDF4 Dataset class ... with the idea of being able to add a cdml writer"""
  __extra__ = dict()
  __help__ = dict()

  def __init__(self,file=None):
    self.__extra__['uid'] = str( uuid.uuid1() )
    if file == None:
       super(WrapNetCDF4, self).__init__('%s.nc' % self.__extra__['uid'], diskless=True, mode='w')
    else:
       super(WrapNetCDF4, self).__init__(file, mode='w')

  def help(self):
    for k,v in self.__help__.items():
      print ('%s: %s' % (k,v) )

  def loadDreq(self,dq=None):
    if dq == None:
      dq = dreq.loadDreq()
      collect.add( dq )
    self.__extra__['dq'] = dq

  def create01( self, name, table, time=[0.,1.], lat=[-30.,0.,30.],lon=[-180.,0.,180.] ):
    dq = self.__extra__['dq']
    assert name in dq.coll['var'].items[0]._labelDict
    this = dq.coll['var'].items[0]._labelDict[name]
    cmvs = [dq.inx.uid[x] for x in dq.inx.iref_by_sect[this.uid].a['CMORvar']]
    cmv = [x for x in cmvs if x.mipTable == table][0]
    cm = dq.inx.uid[cmv.stid].cell_methods
    cms = dq.inx.uid[cmv.stid].cell_measures
    self.createDimension( 'time',len(time) )
    self.createDimension( 'lat',len(lat) )
    self.createDimension( 'lon',len(lon) )
    
    this.__info__()

    self.set_var( 'time', 'double', ('time',), attributes={'standard_name':'time', 'units':'days since 2000-01-01 00:00:00'},
              data = time )

    self.set_var( 'lon', 'double', ('lon',),  attributes={'standard_name':'longitude', 'units':'degrees_east'},
              data = lon )
    self.set_var( 'lat', 'double', ('lat',),  attributes={'standard_name':'latitude', 'units':'degrees_north'},
              data = lat )

    attr = {'standard_name':this.sn, 'long_name':this.title, 'units':this.units, 'cell_methods':cm, 'cell_measures':cms }
    self.set_var( this.label, 'float', ('time','lat','lon'), attributes=attr)

  def defaults(self):
    for k,v in {'time': 10, 'lat':90, 'lon':180}.items():
       self.createDimension( k,v )
    self.__extra__['main'] = 'orog'
    self.set_var( 'time', 'double', ('time',), attributes={'standard_name':'time', 'units':'days since 2000-01-01 00:00:00'},
              data = [float(x) for x in range(10)] )

    self.set_var( 'lon', 'double', ('lon',),  attributes={'standard_name':'longitude', 'units':'degrees_east'},
              data = [float(x)*2. for x in range(180)] )
    self.set_var( 'lat', 'double', ('lat',),  attributes={'standard_name':'latitude', 'units':'degrees_north'},
              data = [float(x)*2. - 89. for x in range(90)] )

    self.set_var( 'orog', 'float', ('time','lat','lon'), attributes={'standard_name':'orography', 'units':'m'})


  def set_var(self,*args,**kwargs):
    attributes = None
    data = None
    if 'attributes' in kwargs:
      attributes = kwargs.pop( 'attributes' )
    if 'data' in kwargs:
      data = kwargs.pop( 'data' )

##
## initially tried using VariableTemplateNC4 ...
##   but this messed up assigment of the self.variables object, so that variables created ended up in limbo.
##   a single level of wrapping appears the best option here (alternative to find out what createVariable is actually
##   doing ... but this is probably in C++ code).
##
    var = self.createVariable(*args,**kwargs)

## use of setncatts causes some problems ... AttributeError: __getattribute__ when displaying a slice
    if attributes != None:
##      var.setncatts( attributes )
      for k,v in attributes.items():
        setattr( var, k, v )

    if data != None:
      var[...] = data
    return var

  def defaults(self):
    for k,v in {'time': 10, 'lat':90, 'lon':180}.items():
       self.createDimension( k,v )
    self.__extra__['main'] = 'orog'
    self.set_var( 'time', 'double', ('time',), attributes={'standard_name':'time', 'units':'days since 2000-01-01 00:00:00'},
              data = [float(x) for x in range(10)] )

    self.set_var( 'lon', 'double', ('lon',),  attributes={'standard_name':'longitude', 'units':'degree_east'},
              data = [float(x)*2. for x in range(180)] )
    self.set_var( 'lat', 'double', ('lat',),  attributes={'standard_name':'latitude', 'units':'degree_north'},
              data = [float(x)*2. - 89. for x in range(90)] )

    self.set_var( 'orog', 'float', ('time','lat','lon'), attributes={'standard_name':'orography', 'units':'m'})

class VariableTemplate(object):
  attributes = dict()
  attribute_intent = dict()
  dimensions = list()
  intent = 'float'
  data = list()

  def set(self,dimensions, attributes, data=None, intent=None, attribute_intent=None):
    self.dimensions = dimensions
    self.attributes = attributes
    if data != None:
      self.data = data
    if intent != None:
      self.intent = intent
    if attribute_intent != None:
      self.attribute_intent = attribute_intent

class ContentTemplateBasic(dict):
  """A simple representation of NetCDF file contents.
  
  Contains
  --------
  dimensions : a dictionary of key-value pairs. Keys should be valid NetCDF dimension names and values positive integers;
  globals: a dictionary of key-value pairs. [[TODO: need to distinguish single vs. double precision in intent]]
  globals_intent: where needed, specify the intended type of a variable (needed to distingush between float and double)
  variables : a dictionary of variables .. including variables for dimensions if provided;
  unlimited: name of unlimited dimension, if set;
  main: name of main data variable, if set;


  Methods:
    validate_dimensions: verify that dimensions of variables are defined in parent instance;
    defaults: load the instance with default contents representing an orographic field on a regular grid [TIME EVOLVING]
  """
  
  variables = collections.defaultdict( VariableTemplate )
  globals = dict()
  dimensions = dict()
  unlimited = None
  main = None

  def validate_dimensions(self):
    for n,v in self.variables.items():
      for d in v.dimensions:
        assert d in self.dimensions

  def defaults(self):
    self.dimensions = {'time': 10, 'lat':90, 'lon':180}
    self.unlimited = 'time'
    self.main = 'orog'
    self.variables['time'].set( ['time'], {'standard_name':'time', 'units':'days since 2000-01-01 00:00:00'},
              data = [float(x) for x in range(10)], intent='double' )

    self.variables['lon'].set( ['lon'], {'standard_name':'longitude', 'units':'degree_east'},
              data = [float(x)*2. for x in range(180)], intent='double' )
    self.variables['lat'].set( ['lat'], {'standard_name':'latitude', 'units':'degree_north'},
              data = [float(x)*2. - 89. for x in range(90)], intent='double' )

    self.variables['orog'].set( ['time','lat','lon'], {'standard_name':'orography', 'units':'m'})
    self.globals = {'comment':'dummy dataset generated by ContentTemplate',
                    'institute':'Centre for Environmental Data Analysis'}

class ContentTemplate(dict):
  """A simple representation of NetCDF file contents. Using NetCDF4
  
  Contains
  --------
  dimensions : a dictionary of key-value pairs. Keys should be valid NetCDF dimension names and values positive integers;
  globals: a dictionary of key-value pairs. [[TODO: need to distinguish single vs. double precision in intent]]
  globals_intent: where needed, specify the intended type of a variable (needed to distingush between float and double)
  variables : a dictionary of variables .. including variables for dimensions if provided;
  unlimited: name of unlimited dimension, if set;
  main: name of main data variable, if set;


  Methods:
    validate_dimensions: verify that dimensions of variables are defined in parent instance;
    defaults: load the instance with default contents representing an orographic field on a regular grid [TIME EVOLVING]
  """
  
  variables = collections.defaultdict( VariableTemplate )
  globals = dict()
  dimensions = dict()
  unlimited = None
  main = None

  def __init__(self):
    nc = netCDF4.Dataset( 'dummy.nc', diskless=True, mode='w' )

  def validate_dimensions(self):
    for n,v in self.variables.items():
      for d in v.dimensions:
        assert d in self.dimensions

  def defaults(self):
    self.dimensions = {'time': 10, 'lat':90, 'lon':180}
    self.unlimited = 'time'
    self.main = 'orog'
    self.variables['time'].set( ['time'], {'standard_name':'time', 'units':'days since 2000-01-01 00:00:00'},
              data = [float(x) for x in range(10)], intent='double' )

    self.variables['lon'].set( ['lon'], {'standard_name':'longitude', 'units':'degree_east'},
              data = [float(x)*2. for x in range(180)], intent='double' )
    self.variables['lat'].set( ['lat'], {'standard_name':'latitude', 'units':'degree_north'},
              data = [float(x)*2. - 89. for x in range(90)], intent='double' )

    self.variables['orog'].set( ['time','lat','lon'], {'standard_name':'orography', 'units':'m'})
    self.globals = {'comment':'dummy dataset generated by ContentTemplate',
                    'institute':'Centre for Environmental Data Analysis'}
