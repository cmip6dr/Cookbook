import numpy
import cfdm

# Initialize the field construct
tas = cfdm.Field(
    properties={'project': 'research',
                'standard_name': 'air_temperature',
                'units': 'K'})

# Create and set domain axis constructs
axis_T = tas.set_construct(cfdm.DomainAxis(1))
axis_Z = tas.set_construct(cfdm.DomainAxis(1))
axis_Y = tas.set_construct(cfdm.DomainAxis(10))
axis_X = tas.set_construct(cfdm.DomainAxis(9))

# Set the field construct data
tas.set_data(cfdm.Data(numpy.arange(90.).reshape(10, 9)),
             axes=[axis_Y, axis_X])

# Create and set the cell method constructs
cell_method1 = cfdm.CellMethod(
          axes=[axis_Y, axis_X],
          method='mean',
          qualifiers={'where': 'land',
                      'interval': [cfdm.Data(0.1, units='degrees')]})

cell_method2 = cfdm.CellMethod(axes=axis_T, method='maximum')

tas.set_construct(cell_method1)
tas.set_construct(cell_method2)

# Create and set the field ancillary constructs
field_ancillary = cfdm.FieldAncillary(
             properties={'standard_name': 'air_temperature standard_error',
                          'units': 'K'},
             data=cfdm.Data(numpy.arange(90.).reshape(10, 9)))

tas.set_construct(field_ancillary, axes=[axis_Y, axis_X])

# Create and set the dimension coordinate constructs
dimension_coordinate_T = cfdm.DimensionCoordinate(
                           properties={'standard_name': 'time',
                                       'units': 'days since 2018-12-01'},
                           data=cfdm.Data([15.5]),
                           bounds=cfdm.Bounds(data=cfdm.Data([[0., 31]])))

dimension_coordinate_Z = cfdm.DimensionCoordinate(
        properties={'computed_standard_name': 'altitude',
                    'standard_name': 'atmosphere_hybrid_height_coordinate'},
        data = cfdm.Data([1.5]),
        bounds=cfdm.Bounds(data=cfdm.Data([[1.0, 2.0]])))

dimension_coordinate_Y = cfdm.DimensionCoordinate(
        properties={'standard_name': 'grid_latitude',
                    'units': 'degrees'},
        data=cfdm.Data(numpy.arange(10.)),
        bounds=cfdm.Bounds(data=cfdm.Data(numpy.arange(20).reshape(10, 2))))

dimension_coordinate_X = cfdm.DimensionCoordinate(
        properties={'standard_name': 'grid_longitude',
                    'units': 'degrees'},
    data=cfdm.Data(numpy.arange(9.)),
    bounds=cfdm.Bounds(data=cfdm.Data(numpy.arange(18).reshape(9, 2))))

dim_T = tas.set_construct(dimension_coordinate_T, axes=axis_T)
dim_Z = tas.set_construct(dimension_coordinate_Z, axes=axis_Z)
dim_Y = tas.set_construct(dimension_coordinate_Y, axes=axis_Y)
dim_X = tas.set_construct(dimension_coordinate_X, axes=axis_X)

# Create and set the auxiliary coordinate constructs
auxiliary_coordinate_lat = cfdm.AuxiliaryCoordinate(
                      properties={'standard_name': 'latitude',
                                  'units': 'degrees_north'},
                      data=cfdm.Data(numpy.arange(90.).reshape(10, 9)))

auxiliary_coordinate_lon = cfdm.AuxiliaryCoordinate(
                  properties={'standard_name': 'longitude',
                              'units': 'degrees_east'},
                  data=cfdm.Data(numpy.arange(90.).reshape(9, 10)))

array = numpy.ma.array(list('abcdefghij'))
array[0] = numpy.ma.masked
auxiliary_coordinate_name = cfdm.AuxiliaryCoordinate(
                       properties={'long_name': 'Grid latitude name'},
                       data=cfdm.Data(array))

aux_LAT  = tas.set_construct(auxiliary_coordinate_lat, axes=[axis_Y, axis_X])
aux_LON  = tas.set_construct(auxiliary_coordinate_lon, axes=[axis_X, axis_Y])
aux_NAME = tas.set_construct(auxiliary_coordinate_name, axes=[axis_Y])

# Create and set domain ancillary constructs
domain_ancillary_a = cfdm.DomainAncillary(
                   properties={'units': 'm'},
                   data=cfdm.Data([10.]),
                   bounds=cfdm.Bounds(data=cfdm.Data([[5., 15.]])))

domain_ancillary_b = cfdm.DomainAncillary(
                       properties={'units': '1'},
                       data=cfdm.Data([20.]),
                       bounds=cfdm.Bounds(data=cfdm.Data([[14, 26.]])))

domain_ancillary_orog = cfdm.DomainAncillary(
                          properties={'standard_name': 'surface_altitude',
                                      'units': 'm'},
                          data=cfdm.Data(numpy.arange(90.).reshape(10, 9)))

domain_anc_A    = tas.set_construct(domain_ancillary_a, axes=axis_Z)
domain_anc_B    = tas.set_construct(domain_ancillary_b, axes=axis_Z)
domain_anc_OROG = tas.set_construct(domain_ancillary_orog,
                                    axes=[axis_Y, axis_X])

# Create the datum for the coordinate reference constructs
datum = cfdm.Datum(parameters={'earth_radius': 6371007.5})

# Set the netCDF name for a grid mapping variable that might be created from this datum

# Create the coordinate conversion for the horizontal coordinate
# reference construct
coordinate_conversion_h = cfdm.CoordinateConversion(
              parameters={'grid_mapping_name': 'rotated_latitude_longitude',
                          'grid_north_pole_latitude': 38.0,
                          'grid_north_pole_longitude': 190.0})

# Create the coordinate conversion for the vertical coordinate
# reference construct
coordinate_conversion_v = cfdm.CoordinateConversion(
         parameters={'standard_name': 'atmosphere_hybrid_height_coordinate',
                     'computed_standard_name': 'altitude'},
         domain_ancillaries={'a': domain_anc_A,
                             'b': domain_anc_B,
                             'orog': domain_anc_OROG})

# Create the vertical coordinate reference construct
horizontal_crs = cfdm.CoordinateReference(
                   datum=datum,
                   coordinate_conversion=coordinate_conversion_h,
                   coordinates=[dim_X,
                                dim_Y,
                                aux_LAT,
                                aux_LON])


horizontal_crs.datum.nc_set_variable('my_datum_name')
tas.set_construct(horizontal_crs)

# Create the vertical coordinate reference construct
vertical_crs = cfdm.CoordinateReference(
                 datum=horizontal_crs.datum,
                 coordinate_conversion=coordinate_conversion_v,
                 coordinates=[dim_Z])
vertical_crs.datum.nc_set_variable('my_datum_name')

# Set the coordinate reference constructs
tas.set_construct(vertical_crs)

# Create and set the cell measure constructs
cell_measure = cfdm.CellMeasure(measure='area',
                 properties={'units': 'km2'},
                 data=cfdm.Data(numpy.arange(90.).reshape(9, 10)))

tas.set_construct(cell_measure, axes=[axis_X, axis_Y])

print(tas)

cfdm.write(tas, 'delme.nc', verbose=True)
cfdm.environment()
