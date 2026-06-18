"""
Calculate the scaling factor in the simplest way 

"""

import xarray as xr 
import matplotlib.pyplot as plt 
import numpy as np
import pandas as pd 

plots_path = '/home/anna_lanteri/code/cmip-ghg-forcing/plots/'
ground_path = '/home/anna_lanteri/data/ground_based_data/NOAA/ch4_surface-insitu_ccgg_netCDF/'
sat_path = '/home/anna_lanteri/data/satellite_data/OBS4MIPs/'

# Mauna Loa, Hawaii, 01/1987
mlo_path = f"{ground_path}/ch4_mlo_surface-insitu_1_ccgg_MonthlyData.nc"
# Mauna Kea, Hawaii, 12/2022
mko_path = f"{ground_path}/ch4_mko_surface-insitu_1_ccgg_MonthlyData.nc"
# Utqiaġvik, Alaska, 04/1987
brw_path = f"{ground_path}/ch4_brw_surface-insitu_1_ccgg_MonthlyData.nc"

def get_sat_data_at_ground_coords(gb_data, sat_data):
    gb_lat = gb_data.attrs['site_latitude']
    gb_lon  = gb_data.attrs['site_longitude']

    aligned =  sat_data.sel(lat=gb_lat, lon=gb_lon, method="nearest")
    return set_sat_time_at_start_of_month(aligned)

def set_sat_time_at_start_of_month(sat_data):
    return sat_data.assign_coords(
        time=pd.DatetimeIndex(sat_data.time.values)
            .to_period("M")
            .to_timestamp()
    )

def make_sat_times_mask(gb_data, sat_data):
    valid_sat_times = sat_data.time.values[
        ~np.isnan(sat_data['xch4'].values)
    ]
    gb_time = gb_data['time']

    return np.isin(gb_time, valid_sat_times)

def make_ground_times_mask(gb_data, sat_data):
    valid_ground_times = gb_data.time.values[
        ~np.isnan(gb_data['time'].values)
    ]
    sat_time = sat_data['time']

    return np.isin(sat_time, valid_ground_times)

def plot_fit(sat, gb, station_name):

    sat = get_sat_data_at_ground_coords(gb, sat)
    mask_ground = make_sat_times_mask(gb, sat)
    gb_ch4 = gb['value'][mask_ground] /1e9

    mask_sat = make_ground_times_mask(gb, sat)
    sat = sat['xch4'][mask_sat].dropna(dim = 'time').squeeze().values

    sf = simple_fit(sat, gb_ch4)

    print(f"Scaling factor sf = {sf}")

    plt.scatter(sat, gb_ch4, label="measurements")

    x = np.linspace(sat.min(), sat.max(), 100)
    plt.plot(x, sf*x, 'r-', label=f"fit: gb = {sf:.3f} × sat")

    plt.xlabel("Satellite XCH4")
    plt.ylabel(f"{station_name} CH4")
    plt.legend()
    plt.grid(True)

    plt.savefig(f"{plots_path}{station_name}_vs_sat_fit.png", dpi=300)
    plt.close()


def simple_fit(sat, gb):
    # fit gb = sf * sat
    return (np.sum(sat * gb) / np.sum(sat**2)).values

#gb_fit = sf * sat
#epsilon = mlo_ch4_matched - gb_fit

if __name__ == "__main__":

    # NOAA datasets
    mlo_data = xr.open_dataset(mlo_path)
    mko_data = xr.open_dataset(mko_path)
    brw_data = xr.open_dataset(brw_path)

    # OBD4MIPs
    sat_data = xr.open_dataset(f"{sat_path}/200301_202312-C3S-L3_XCH4-GHG_PRODUCTS-MERGED-MERGED-OBS4MIPS-MERGED-v4.6.nc")
    sat_data['xch4'] = sat_data['xch4'].where(sat_data['xch4'] != 1.e+20, np.nan)

    #plot_fit(sat_data, mlo_data, 'mlo')
    #plot_fit(sat_data, mko_data, 'mko')
    #plot_fit(sat_data, brw_data, 'brw')

    # TODO: merge the datasets together, fit all data, derive 
    #       a total scaling factor for NOAA 


