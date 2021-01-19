import re, collections

class Unlimited(object):
   """Class to be used to set 'unlimited' dimension."""
   pass

class ArgumentError(ValueError):
  def __init__(self,value,msg):
    self.value = value
    self.msg = msg

  def __str__(self):
    return repr( self.msg )

  def __repr__(self):
    return '%s:: %s' % (value,self.msg)



cdlTypesSrc = """
The CDL primitive data types for the classic model are:

    char - Characters.
    byte - Eight-bit integers.
    short - 16-bit signed integers.
    int - 32-bit signed integers.
    long - (Deprecated, synonymous with int)
    float - IEEE single-precision floating point (32 bits).
    real - (Synonymous with float).
    double - IEEE double-precision floating point (64 bits).

NetCDF-4 supports the additional primitive types:

    ubyte - Unsigned eight-bit integers.
    ushort - Unsigned 16-bit integers.
    uint - Unsigned 32-bit integers.
    int64 - 64-bit signed integers.
    uint64 - Unsigned 64-bit signed integers.
    string - Variable-length string of characters
"""

## attributes :  "0.1f" for float, "0.1d" of "0.1D" for double.  "f","l",... for char array, otherwise string (unless classic model).
## [1-9][0-9]*[sS] --> short integer
## 0[0-9]*[sS] --> octal
## 0x[0-9a-f]*s ---> hex

## octal and hex without trailing s --> fulllength integer

## more at https://www.unidata.ucar.edu/software/netcdf/netcdf/CDL-Notation-for-Data-Constants.html#CDL-Notation-for-Data-Constants

## Attribute values: if quoted --> string, char, or list of either.
## Otherwise, 
## ends in ".", s/S, d/D, f/F, [0-9]
## Don't have a complete system here ... in ambiguity, coerce to same type as variable (e.g. float --> double, int --> uint).
## Could also add comments of the form "//uint//"

this = [x.strip() for x in cdlTypesSrc.split( '\n' )]
cdlTypes = {}
for x in this:
  if len(x) > 0 and x.find( ' - ' ) != -1:
    a,b = [y.strip() for y in x.split( ' - ' )]
    cdlTypes[a] = b

for k in sorted( cdlTypes.keys() ):
  print ('%s: %s' % (k,cdlTypes[k]) )

#
# cdl allows multiple variable declarations on one line (not the CF Convention usage ....)
# this makes parsing a little trickier.
#
# cdl also allows ".", "-", "+" and "@" in names .....
# start character should be letter or "_"
#

class Cdlobject(object):
  def __init__(self,dimensions, variables):
    self.dimensions = dimensions
    self.variables = variables

  def set_dimension(self,name,val):
    if name not in self.dimensions.keys():
      raise ArgumentError( name, '%s not in dimensions: %s' % (name,self.dimensions.keys()) )
    if type( val ) not in [type(1),Unlimited]:
      raise ArgumentError( val, 'Value %s is not integer or Unlimited' % val)
    if type(val) == type(1) and val <= 0:
      raise ArgumentError( val, "Value %s is not positive" % val)

    self.dimensions[name] = val
      
    

class ParseCdl(object):
  dec2 = re.compile( '^(?P<type>%s)\s+(?P<vars>[a-zA-Z0-9_(),\s]+);.*' % ('|'.join( cdlTypes.keys() ) ) )
  dims = re.compile( '(?P<name>[a-zA-Z0-9_]+)\s*=\s*(?P<val>[0-9]+|unlimited)(\s*,\s*)?' )
  vars = re.compile( '(?P<var>[a-zA-Z0-9_]+)\s*(?P<dims>\(.*?\))?(\s*,\s*)?' )
  attr = re.compile( '(?P<var>[a-zA-Z0-9_(),\s]+)?:\s*(?P<name>[a-zA-Z0-9_(),]+)\s*=\s*(?P<val>.*)$' )
  NT_attr = collections.namedtuple( 'attribute', ['value','type','comment','rule'] )

  attrStrStr = re.compile( '"\s*,\s*"' )

##
## PERHAPS want to add capability to take type information from comment ...
##
## And also add directives to value declarations.
##
## e.g. source_id = @REQUIRED:FROM=wcrp.cmip6.source_id.
##

  outer = re.compile( '^netcdf\s+(?P<name>[a-zA-Z0-9_][a-zA-Z0-9_\-+@.]*)\s*{(?P<body>.*)}', re.MULTILINE|re.DOTALL )

##
## should match name and outer brackets .... leaving content consisting of comments and declarations.
## ... in 3 sections: dimensions, variables and data.
##

## dec2 amd varGet combined can parse the variable declaration line ...

  def __init__(self):
    self.dimGet = lambda x: [(m.groupdict()['name'],m.groupdict()['val']) for m in self.dims.finditer(x)]
    self.varGet = lambda x: [(m.groupdict()['var'],m.groupdict()['dims']) for m in self.vars.finditer(x)]
    self.cdl = '\n'.join( open( 'delme2.cdl', 'r' ).readlines() )

  def test(self):
    return self.__call__(self.cdl)

  def _strParse(self,val,ptype=None,ctype=None):
    if self.attrStrStr.match( val ):
      print ('STRING LIST: %s' % val )
      return (val, 'string')
    else:
      return (val[1:-1], 'string')
      
    
  def _strParse01(self,val,ptype=None,ctype=None):
    """
      Parse string of char attribute values and return value type tuple.

      ptype: type of parent variable, if applicable. Used as default where there is ambiguity.
      ctype: tpye specifed in comment: overrides 
    """

  def _numParse01(self,val,ptype=None,ctype=None):
    """
      Parse numerical attribute values and return value type tuple.

      ptype: type of parent variable, if applicable. Used as default where there is ambiguity.
      ctype: tpye specifed in comment: overrides 
    """

    if val[-1] in ['s','S']:
      vv = val[:-1]
      t = 'short'
      if ptype == 'ushort':
        t = 'ushort'
      if vv == '0':
        o = 0
      elif len(vv) ==1 :
        o = int(vv)
      elif vv[:2] == '0x':
        raise 'Not yet ready for hex'
      elif vv[:1] == '0':
        raise 'Not yet ready for octal'
    elif val[-1] in ['f','F']:
      vv = val[:-1]
      t = 'float'
      o = float(vv)
    elif val[-1] in ['d','D']:
      vv = val[:-1]
      t = 'double'
      o = float(vv)
    elif val.find( '.' ) == -1:
      if ptype in ['int','short','uint','ushort','int64','uint64']:
        t = ptype
      else:
        t = 'int'
      o = int(val)
    else:
## float.
      if ptype in ['float','double']:
        t = ptype
      else:
        t = 'float'
      o = float(val)
    if ctype != None:
      if t != ctype:
        pass
        ## need a logger here ...
      t = ctype
    return (o,t)
    
  def _attrParse(self,val):
    this = None
    if val[0] == '"' and val[-1] == '"':
      return self._strParse( val )
    else:
      return self._numParse( val )
      
  def _numParse(self,val):
    """
---
--- not clear what to do about logic of parsing lists .....
--- really need a collective type decision before decoding strings

-- interim solution: exception if the simple logic assigns multiple types (e.. integer in float array)
---
    """

    if val.find(',') != -1:
      vs = [x.strip() for x in val.split( ',' )]
      vv = [] 
      tt = set()
      for v in vs:
        o,t = self._numParse01( v )
        vv.append( o )
        tt.add( t )
      assert len(tt) == 1, 'Multiple types implied ... formulation of CDL not supported: %s: %s' % (str(val),str(tt))
      return vv,t
    else:
      return self._numParse01( val )

  def __call__(self,cdl=None,fn=None):
    assert not all( [cdl==None,fn==None] ), 'Either cdl (string CDL) of fn (file containing CDL) must be specified as argument'
    assert not all( [cdl!=None,fn!=None] ), 'Only one of cdl (string CDL) or fn (file containing CDL) must be specified as argument: %s' % [cdl==None,fn==None]

    if fn != None:
      cdl = ''.join( [x for x in open( fn ).readlines() ] )
    
    m = self.outer.match( cdl )
    if m == None:
       print ("Failed to parse file name .. should be 'netcdf <name> { <body> }'" )
       self.cdl = cdl
       return None

    self._dims = {}
    self._vars = collections.defaultdict( dict )

    gd = m.groupdict()
    self.name = gd['name']
    body = gd['body']
    bb = [(y.split(';')[0].strip(),y) for y  in [x.strip() for x in body.split( '\n' ) ] if y[:2] != '//']
    cc = collections.defaultdict(list)
    this = None
    for b,l0 in bb:
      if b == 'dimensions:':
        this = 'dim'
      elif b == 'variables:':
        this = 'var'
      elif b == 'data:':
        this = 'dat'
      else:
        cc[this].append((b,l0))

    for b,l0 in cc['dim']:
      for d,v in self.dimGet( b ):
        if v == 'unlimited':
          self._dims[d] = v
        else:
          self._dims[d] = int(v)
    print (self._dims )

##
## l0 appended so that comment can be extracted here ..... 
##
    for b,l0 in cc['var']:
      #
      # each line should be either an attribute or a variable
      #
      m = self.attr.match( b )
      if m == None:
        m2 = ParseCdl.dec2.match(s )
        if m2 == None:
          print ('no match: %s' % s )
        else:
          t = m2.groupdict()['type']
          vl = self.varGet( m2.groupdict()['vars'] )
          for n,v in vl:
            self._vars[n]['__type__'] = t
            self._vars[n]['__dims__'] = v
      else:
        gd = m.groupdict()
        v,n,val = [gd[x] for x in ['var','name','val']]
        if l0.find( '//' ) != -1:
          comment = l0.split( '//', maxsplit = 1 )[1]
        else:
          comment = None

        val1, tt = self._attrParse(val)
        if v in [None,'']:
          v = '__global__'
        self._vars[v][n] = self.NT_attr(val1,tt,comment,None)

    print (self._vars )
    self.cc = cc

    return Cdlobject( self._dims, self._vars )


class Cdl2nc(object):
  def __init__(self,cdl,fn):
    self.cdl = cdl
    nc = netCDF4.Dataset( fn, 'w' )
    dims = {}
    vars = {}
    for d,l in cdl.dimensions.items():
      dims[d] = nc.createDimension( d,l )

    for v,dd in cdl.variables.items():
      t = dd['__type__']
      dstr = tuple( dd['__dims__'].strip()[1:-1].split(',') )
      vars[v] = nc.createVariable( v, t, dstr )

    nc.close()

dec = re.compile( '^(?P<type>%s)\s+(?P<var>[a-zA-Z0-9_]+)\s*(?P<dims>\(.*\))?\s*;.*' % ('|'.join( cdlTypes.keys() ) ) )

decSamples = [ "int     lat(lat), lon(lon), time(time);",
               "float   z(time,lat,lon), t(time,lat,lon);",
               "double  p(time,lat,lon);",
               "int     rh(time,lat,lon);"]

dimSamples = ['lat = 10, lon = 5, time = unlimited;']

p = ParseCdl()
for s in decSamples:
  m = ParseCdl.dec2.match(s )
  if m == None:
    print ('no match: %s' % s )
  else:
    vl = p.varGet( m.groupdict()['vars'] )
    print (m.groupdict(), vl)


print (p.dimGet( dimSamples[0] ) )



