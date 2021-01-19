
import netCDF4
import cfdm
import numpy


f = cfdm.Field(properties={'standard_name': 'precipitation_flux'})

dc = cfdm.DimensionCoordinate(properties={'long_name': 'Longitude'},
                               data=cfdm.Data([0, 1, 2.]))

fa = cfdm.FieldAncillary(
        properties={'standard_name': 'precipitation_flux status_flag'},
        data=cfdm.Data(numpy.array([0, 0, 2], dtype='int8')))

longitude_axis = f.set_construct(cfdm.DomainAxis(3))

key = f.set_construct(dc, axes=longitude_axis)

cm = cfdm.CellMethod(axes=longitude_axis, method='minimum')
f.set_construct(cm)

