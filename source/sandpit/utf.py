

import netCDF4

nc = netCDF4.Dataset( 'example_utf.nc', 'w' )

t = nc.createVariable( 'Temperature (°C)', 'f' )
tt = nc.createVariable( 'Umeå_station', 'f' )

nc.close()

