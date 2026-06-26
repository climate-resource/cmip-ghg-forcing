"""

Point selection

Brutal selection of points that have both satellite value and
ground based measurements from NOAA

"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

from local.processing.utils import extract_ground_data, get_scaling

gas = 'co2'
sat_gas = "x"+gas

if gas == 'co2':
    uppercase_gas = "CO2"
elif gas == 'ch4':
    uppercase_gas = 'CH4'

plots_path = "/home/anna_lanteri/code/cmip-ghg-forcing/plots/"
data_path = Path(
    f"/home/anna_lanteri/data/ground_based_data/NOAA/{gas}_surface-insitu_ccgg_netCDF/"
)
sat_path = "/home/anna_lanteri/data/satellite_data/OBS4MIPs/"

## Mauna Loa, Hawaii, 01/1987
## Mauna Kea, Hawaii, 12/2022
# American Samoa, 04/2025
# Utqiaġvik, Alaska, 04/1987


def get_sat_data_at_ground_coords(gb_data: xr.Dataset, sat_data):
    """Return sat data at ground coords"""
    gb_lat = gb_data.attrs["site_latitude"]
    gb_lon = gb_data.attrs["site_longitude"]
    print(gb_lon)
    print(gb_lat)

    aligned = sat_data.sel(lat=gb_lat, lon=gb_lon, method="nearest")
    return set_sat_time_at_start_of_month(aligned)


def set_sat_time_at_start_of_month(sat_data):
    """Set timestamp of satellite at the beginning of the month"""
    return sat_data.assign_coords(
        time=pd.DatetimeIndex(sat_data.time.values).to_period("M").to_timestamp()
    )


def make_sat_times_mask(gb_data, sat_data):
    """Maybe not useful"""
    valid_sat_times = sat_data.time.values[~np.isnan(sat_data[sat_gas].values)]
    gb_time = gb_data["time"]

    return np.isin(gb_time, valid_sat_times)


def make_ground_times_mask(gb_data, sat_data):
    """Like I thin kI have a better way to do this somewhere"""
    valid_ground_times = gb_data.time.values[~np.isnan(gb_data["time"].values)]
    sat_time = sat_data["time"]

    return np.isin(sat_time, valid_ground_times)


def plot_matching_data(gb, sat, gas, station_name):
    """Plot matching data of sat and ground based obs"""
    scaling = get_scaling(gas)

    gb["value"] = gb["value"].where(gb["value"] >= 0, np.nan)
    sat[sat_gas] = sat[sat_gas].where(sat[sat_gas] >= 0, np.nan)


    sat_data_ground = get_sat_data_at_ground_coords(gb, sat)

    mask = make_sat_times_mask(gb, sat_data_ground)

    gb_time = gb["time"][mask]
    gb_gas = gb["value"][mask] / scaling

    sat_data_ground[sat_gas].plot(
        label=f"sat over {station_name} coords",
        marker="o",
        linestyle="None",
    )
    plt.plot(
        gb_time,
        gb_gas,
        label=f"{station_name}",
        marker="o",
        linestyle="None",
    )
    plt.legend()
    plt.title(f"Comparing OBS4MIPs over {station_name} coords and ground based data")
    plt.savefig(f"{plots_path}sat_over_{station_name}_and_gb_{gas}.png", format="png")
    plt.close()


def get_matching_data(gb, sat, gas="ch4"):
    """Return matched satellite and ground observations."""
    sat_ground = get_sat_data_at_ground_coords(gb, sat)

    gb_times, gb_values = extract_ground_data(gb, gas)

    valid_sat = np.isfinite(sat_ground["x" + gas].values)

    sat_times = sat_ground.time.values[valid_sat]
    sat_values = sat_ground["x" + gas].values[valid_sat]

    common_times = np.intersect1d(gb_times, sat_times)

    gb_mask = np.isin(gb_times, common_times)
    sat_mask = np.isin(sat_times, common_times)

    gb_matched = gb_values[gb_mask]
    sat_matched = sat_values[sat_mask]

    valid = np.isfinite(gb_matched) & np.isfinite(sat_matched)

    return sat_matched[valid], gb_matched[valid]

def scatter_plot(gb, sat, station_name):
    """Scatter plot of sat vs gd data"""
    gb["value"] = gb["value"].where(gb["value"] >= 0, np.nan)
    sat[sat_gas] = sat[sat_gas].where(sat[sat_gas] >= 0, np.nan)

    gb_matched, sat_matched = get_matching_data(gb, sat, gas)

    plt.scatter(gb_matched, sat_matched, alpha=0.7)

    plt.xlabel(f"{station_name} {uppercase_gas}")
    plt.ylabel(f"Satellite X{uppercase_gas}")
    plt.title(f"Satellite vs {station_name} {uppercase_gas}")
    plt.grid(True)
    plt.savefig(f"{plots_path}sat_vs_{station_name}_scatter_{gas}.png", dpi=300)
    plt.close()


def get_station_code(filename):
    """Return station code after first _"""
    return Path(filename).stem.split("_")[1]


if __name__ == "__main__":
    sat_default = 1.0e20

    # OBD4MIPs
    sat_data = xr.open_dataset(
        f"{sat_path}/200301_202312-C3S-L3_X{uppercase_gas}-GHG_PRODUCTS-MERGED-MERGED-OBS4MIPS-MERGED-v4.6.nc"
    )
    sat_data[sat_gas] = sat_data[sat_gas].where(sat_data[sat_gas] != sat_default, np.nan)

    ## Plot the comparison plots
    files = sorted(data_path.glob(f"{gas}_*_MonthlyData.nc"))

    for file in files:
        ds = xr.open_dataset(file)
        station_name = get_station_code(file)
        print(station_name)
        #plot_matching_data(ds, sat_data, gas, station_name=station_name)
        print('scatter')
        scatter_plot(ds, sat_data, station_name=station_name)
