"""
Brutal selection of points that have both satellite value and 
ground based measurements

"""
# TODO: do this for all datasets, taking away repetition
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
# American Samoa, 04/2025
smo_path = f"{ground_path}/ch4_smo_surface-insitu_1_ccgg_MonthlyData.nc"
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

def plot_matching_data(gb_data, sat_data, station_name):
    sat_data = get_sat_data_at_ground_coords(gb_data, sat_data)

    mask = make_sat_times_mask(gb_data, sat_data)

    gb_time = gb_data['time'][mask]
    gb_ch4 = gb_data['value'][mask] /1e9

    sat_data['xch4'].plot(label=f"sat over {station_name} coords",
                           marker='o',
                           linestyle='None', )
    plt.plot(gb_time,
             gb_ch4, 
             label=f"{station_name}",
             marker='o',
             linestyle='None',)   
    plt.legend()
    plt.title(f"Comparing OBS4MIPs over {station_name} coords and ground based data")
    plt.savefig(f"{plots_path}sat_over_{station_name}_and_gb.png", format="png")
    plt.close() 

def scatter_plot(gb_data, sat_data, station_name):
    sat_data = get_sat_data_at_ground_coords(gb_data, sat_data)

    mask_ground = make_sat_times_mask(gb_data, sat_data)
    gb_ch4 = gb_data['value'][mask_ground].dropna(dim = 'obs') /1e9

    mask_sat = make_ground_times_mask(gb_data, sat_data)
    sat_data = sat_data['xch4'][mask_sat].dropna(dim = 'time')

    plt.scatter(
        gb_ch4,
        sat_data,
        alpha=0.7
    )

    plt.xlabel(f"{station_name} CH4")
    plt.ylabel("Satellite XCH4")
    plt.title(f"Satellite vs {station_name} CH4")
    plt.grid(True)
    plt.savefig(f"{plots_path}sat_vs_{station_name}_scatter.png", dpi=300)
    plt.close()


if __name__ == "__main__":

    # NOAA datasets
    mlo_data = xr.open_dataset(mlo_path)
    mko_data = xr.open_dataset(mko_path)
    smo_data = xr.open_dataset(smo_path)
    brw_data = xr.open_dataset(brw_path)
    
    # OBD4MIPs
    sat_data = xr.open_dataset(f"{sat_path}/200301_202312-C3S-L3_XCH4-GHG_PRODUCTS-MERGED-MERGED-OBS4MIPS-MERGED-v4.6.nc")
    sat_data['xch4'] = sat_data['xch4'].where(sat_data['xch4'] != 1.e+20, np.nan)


    ## Plot the comparison plots 
    plot_matching_data(mlo_data, sat_data, 'mlo')
    plot_matching_data(mko_data, sat_data, 'mko')
    plot_matching_data(smo_data, sat_data, 'smo')
    plot_matching_data(brw_data, sat_data, 'brw')

    ## Plot scatter plots
    scatter_plot(mlo_data, sat_data, 'mlo')
    scatter_plot(mko_data, sat_data, 'mko') 
    scatter_plot(smo_data, sat_data, 'smo')
    scatter_plot(brw_data, sat_data, 'brw')
