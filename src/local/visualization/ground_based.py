"""
Plotting trends for CH4 for all ground based observation stations from NOAA

"""

import xarray as xr
import matplotlib.pyplot as plt 
import numpy as np

ground_path = '/home/anna_lanteri/data/ground_based_data/NOAA/ch4_surface-insitu_ccgg_netCDF/'
plots_path = '/home/anna_lanteri/code/cmip-ghg-forcing/plots/'

# Mauna Loa, Hawaii, 01/1987
mlo_path = f"{ground_path}/ch4_mlo_surface-insitu_1_ccgg_MonthlyData.nc"
# Mauna Kea, Hawaii, 12/2022
mko_path = f"{ground_path}/ch4_mko_surface-insitu_1_ccgg_MonthlyData.nc"
# American Samoa, 04/2025
smo_path = f"{ground_path}/ch4_smo_surface-insitu_1_ccgg_MonthlyData.nc"
# Utqiaġvik, Alaska, 04/1987
brw_path = f"{ground_path}/ch4_brw_surface-insitu_1_ccgg_MonthlyData.nc"

mlo_data = xr.open_dataset(mlo_path)
mko_data = xr.open_dataset(mko_path)
smo_data = xr.open_dataset(smo_path)
brw_data = xr.open_dataset(brw_path)

#mlo_data['value'] = mlo_data.where(mlo_data['value'] >=0, np.nan)
#mko_data['value'] = mko_data.where(mko_data['value'] >=0, np.nan)
#smo_data['value'] = smo_data.where(smo_data['value'] >=0, np.nan)
#brw_data['value'] = brw_data.where(brw_data['value'] >=0, np.nan)

# TODO: filter better
mlo_ch4 = mlo_data['value'][3:]
mko_ch4 = mko_data['value'][3:]
smo_ch4 = smo_data['value'][3:]
brw_ch4 = brw_data['value'][3:]

mlo_time = mlo_data['time'][3:]
mko_time = mko_data['time'][3:]
smo_time = smo_data['time'][3:]
brw_time = brw_data['time'][3:]

mlo_std = mlo_data['value_std_dev'][3:]
mko_std = mko_data['value_std_dev'][3:]
smo_std = smo_data['value_std_dev'][3:]
brw_std = brw_data['value_std_dev'][3:]

plt.plot(mlo_time, mlo_ch4, label = 'mlo')
plt.plot(mko_time, mko_ch4, label = 'mko')
plt.plot(smo_time, smo_ch4, label = 'smo')
plt.plot(brw_time, brw_ch4, label = 'brw')



plt.fill_between(
    mlo_time,  
    mlo_ch4 - mlo_std, 
    mlo_ch4 + mlo_std,  
    alpha=0.2,
    color='blue',  
)

plt.fill_between(
    mko_time,  
    mko_ch4 - mko_std, 
    mko_ch4 + mko_std,  
    alpha=0.2,
    color='orange',  
)

plt.fill_between(
    smo_time,  
    smo_ch4 - smo_std, 
    smo_ch4 + smo_std,  
    alpha=0.2,
    color='green',  
)


plt.fill_between(
    brw_time,
    brw_ch4 - brw_std, 
    brw_ch4 + brw_std, 
    alpha=0.2,  
    color='red',  
)

plt.legend()
plt.title('Ground based obs')
plt.savefig(f"{plots_path}NOAA_gb_trends.png", format = 'png')


