import numpy as np
import matplotlib.pyplot as plt # to generate plots
import matplotlib.dates as mdates
from mpl_toolkits.basemap import Basemap #plot on map projections
import datetime
from netCDF4 import Dataset # http://unidata.github.io/netcdf4-python/
from netCDF4 import netcdftime
from netcdftime import utime


class PrecipitationNetCDF:
    """
    Wrapper for computation of precipitation
    """
    def __init__(self, data_file, variable='precip'):
        self.data_file = data_file
        self.variable = variable

    def _extract_variables(self):
        """
        Extract variables
        """
        self.file_handle = Dataset(self.data_file, mode='r') #file handle. open in readonly mode
        fh = self.file_handle
        self.lon = fh.variables['lon'][:]
        self.lat = fh.variables['lat'][:]
        self.nctime = fh.variables['time'][:]
        self.time_unit = fh.variables['time'].units
        self.precipitation = fh.variables[self.variable][:]
        try:
            self.calendar = fh.variables['time'].calendar
        except AttributeError: #attribute does not exist
            self.calendar = u"gregorian" # or standard
        
        fh.close()

    def _parse_time(self):
        utime = netcdftime.utime(self.time_unit, calendar=self.calendar)
        self.date_variable = utime.num2date(self.nctime)

    def _visualize(self):
        """
        Pass
        """
        plt.imshow(self.precipitation[0]) #data for the first time-step (January 1901)
        plt.title('Jan 1901 Monthly rainfall [mm]') # save map instead

        lons, lats = np.meshgrid(self.lon, self.lat)
        m = Basemap(projection='kav7', lon_0=0)
        m.drawmapboundary(fill_color='Gray', zorder=0)
        m.drawparallels(np.arange(-90, 99., 30.), labels=[1,0,0,0])
        m.drawmeridians(np.arange(-180.,180., 60.), labels=[0,0,0,1])

        h = m.pcolormesh(lons, lats, self.precipitation[0], shading='flat', latlon=True)
        m.colorbar(h, location='bottom', pad='15%', label='Rainfall [mm/month]')
        plt.title('Jan 1901 Monthly Rainfall [mm]')




    def calculate(self):
        self._extract_variables()
        self._parse_time()
        self._visualize()


