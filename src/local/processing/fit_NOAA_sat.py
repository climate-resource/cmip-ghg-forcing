"""
Calculate the scaling factor in the simplest way

"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

plots_path = "/home/anna_lanteri/code/cmip-ghg-forcing/plots/"
data_path = Path(
    "/home/anna_lanteri/data/ground_based_data/NOAA/ch4_surface-insitu_ccgg_netCDF/"
)
sat_path = "/home/anna_lanteri/data/satellite_data/OBS4MIPs/"

def get_sat_data_at_ground_coords(gb_data, sat_data):
    """Return sat data overlapping with coordinates of ground data"""
    gb_lat = gb_data.attrs["site_latitude"]
    gb_lon = gb_data.attrs["site_longitude"]

    aligned = sat_data.sel(lat=gb_lat, lon=gb_lon, method="nearest")
    return set_sat_time_at_start_of_month(aligned)


def set_sat_time_at_start_of_month(sat_data):
    """Return sat data with timestamps at beginning of month"""
    return sat_data.assign_coords(
        time=pd.DatetimeIndex(sat_data.time.values).to_period("M").to_timestamp()
    )


def make_sat_times_mask(gb_data, sat_data):
    """Return mask of valid times with sat values"""
    valid_sat_times = sat_data.time.values[~np.isnan(sat_data["xch4"].values)]
    gb_time = gb_data["time"]

    return np.isin(gb_time, valid_sat_times)


def make_ground_times_mask(gb_data, sat_data):
    """Return mask of valid times with ground values"""
    valid_ground_times = gb_data.time.values[~np.isnan(gb_data["time"].values)]
    sat_time = sat_data["time"]

    return np.isin(sat_time, valid_ground_times)


def get_matched_data(sat, gb):
    """Get matched satellite and ground obs"""
    sat = get_sat_data_at_ground_coords(gb, sat)
    mask_ground = make_sat_times_mask(gb, sat)
    gb_ch4 = gb["value"][mask_ground] / 1e9

    mask_sat = make_ground_times_mask(gb, sat)
    sat_ch4 = sat["xch4"][mask_sat].dropna(dim="time").squeeze().values

    return sat_ch4, gb_ch4

def plot_fit(sat, gb, sf, station_name):
    """Plot the fit"""
    print(f"Scaling factor sf = {sf}")

    plt.scatter(sat, gb_ch4, label="measurements")

    x = np.linspace(sat.min(), sat.max(), 100)
    plt.plot(x, sf * x, "r-", label=f"fit: gb = {sf:.3f} * sat")

    plt.xlabel("Satellite XCH4")
    plt.ylabel(f"{station_name} CH4")
    plt.legend()
    plt.grid(True)

    plt.savefig(f"{plots_path}NOAA_{station_name}_vs_sat_fit.png", dpi=300)
    plt.close()


def get_station_code(filename):
    """Return station code after first _"""
    return Path(filename).stem.split("_")[1]

def simple_fit(sat, gb):
    """Perform simple fit"""
    # fit gb = sf * sat
    return (np.sum(sat * gb) / np.sum(sat**2)).values


# gb_fit = sf * sat
# epsilon = mlo_ch4_matched - gb_fit

if __name__ == "__main__":
    sat_default = 1.0e20

    # NOAA datasets
    files = sorted(data_path.glob("ch4_*_MonthlyData.nc"))

    # OBD4MIPs
    sat_data = xr.open_dataset(
        f"{sat_path}/200301_202312-C3S-L3_XCH4-GHG_PRODUCTS-MERGED-MERGED-OBS4MIPS-MERGED-v4.6.nc"
    )
    sat_data["xch4"] = sat_data["xch4"].where(sat_data["xch4"] != sat_default, np.nan)

    for file in files:
        gb = xr.open_dataset(file)
        sat_ch4, gb_ch4 = get_matched_data(sat_data, gb)
        sf = simple_fit(sat_ch4, gb_ch4)
        station_name = get_station_code(file)
        if not np.isnan(sf):
            print('plot')
            plot_fit(sat_ch4, gb_ch4, sf, station_name)
