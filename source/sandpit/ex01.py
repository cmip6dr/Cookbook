
import netCDF4
import cfdm
import numpy


f = cfdm.Field()

time = cfdm.DimensionCoordinate(
                 data = cfdm.Data( numpy.array( [float(x) for x in range(10)], dtype='double' ) ),
                 properties = {'standard_name':'time', 'units':'days since 2000-01-01 00:00:00'}
               )


cr = cfdm.CoordinateReference( ('time', ) )

time_dim = cfdm.DomainAxis( 10 )
time_dim.nc_set_dimension( 'time' )

dom = cfdm.Domain()

time_construct = f.set_construct(  time_dim )
key = f.set_construct(  time, axes=time_construct )

dom.set_data_axes( ['time',], key=key )

##    self.set_var( 'lon', 'double', ('lon',),  attributes={'standard_name':'longitude', 'units':'degree_east'},
##              data = [float(x)*2. for x in range(180)] )
##    self.set_var( 'lat', 'double', ('lat',),  attributes={'standard_name':'latitude', 'units':'degree_north'},
##              data = [float(x)*2. - 89. for x in range(90)] )

data = cfdm.Data( numpy.array( [float(x) for x in range(10)], dtype='float' ) )

##f.set_data_axes('time', key=None)
##f.set_data( data, ('time', ) )

##f.set_properties( {'standard_name':'orography', 'units':'m'} )

