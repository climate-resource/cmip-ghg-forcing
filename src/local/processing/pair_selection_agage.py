"""

Select points

Brutal selection of points that have both satellite value and
ground based measurements from AGAGE

"""
# TODO: refactor to eliminate repetition.
# This code is highly duplicated from pair_selection.py

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

plots_path = "/home/anna_lanteri/code/cmip-ghg-forcing/plots/"
data_path = Path("/home/anna_lanteri/data/ground_based_data/AGAGE/")
sat_path = "/home/anna_lanteri/data/satellite_data/OBS4MIPs/"


def get_sat_data_at_ground_coords(gb_data, sat_data):
    """Return sat data overlapping with coordinates of ground data"""
    gb_lat = gb_data.attrs["inlet_latitude"]
    gb_lon = gb_data.attrs["inlet_longitude"]

    aligned = sat_data.sel(lat=gb_lat, lon=gb_lon, method="nearest")
    return set_sat_time_at_start_of_month(aligned)


def set_sat_time_at_start_of_month(sat_data):
    """Return sat data with timestamps at beginning of month"""
    return sat_data.assign_coords(
        time=pd.DatetimeIndex(sat_data.time.values).to_period("M").to_timestamp()
    )


def make_sat_times_mask(gb_data, sat_data):
    """Return mask of valid times with satellite values"""
    valid_sat_times = sat_data.time.values[~np.isnan(sat_data["xch4"].values)]
    gb_time = gb_data["time"]

    return np.isin(gb_time, valid_sat_times)


def make_ground_times_mask(gb_data, sat_data):
    """Return mask of valid times with ground values"""
    valid_ground_times = gb_data.time.values[~np.isnan(gb_data["time"].values)]
    sat_time = sat_data["time"]

    return np.isin(sat_time, valid_ground_times)


def get_matching_data(gb_data, sat_data):
    """Return the datasets where they match in time"""
    valid_gb_times = gb_data.time.values[~np.isnan(gb_data["mf"].values)]

    valid_sat_times = sat_data.time.values[~np.isnan(sat_data["xch4"].values)]

    common_times = np.intersect1d(valid_gb_times, valid_sat_times)

    gb_matched = gb_data["mf"].sel(time=common_times) / 1e9

    sat_matched = sat_data["xch4"].sel(time=common_times)

    return gb_matched, sat_matched


def plot_matching_data(gb_data, sat_data, station_name):
    """Plot matching points in over time"""
    sat_data = get_sat_data_at_ground_coords(gb_data, sat_data)

    mask = make_sat_times_mask(gb_data, sat_data)

    gb_time = gb_data["time"][mask]
    gb_ch4 = gb_data["mf"][mask] / 1e9

    sat_data["xch4"].plot(
        label=f"sat over {station_name} coords",
        marker="o",
        linestyle="None",
    )
    plt.plot(
        gb_time,
        gb_ch4,
        label=f"{station_name}",
        marker="o",
        linestyle="None",
    )
    plt.legend()
    plt.title(f"Comparing OBS4MIPs over {station_name} coords and ground based data")
    plt.savefig(f"{plots_path}sat_over_{station_name}_and_gb_AGAGE.png", format="png")
    plt.close()


def scatter_plot(gb_data, sat_data, station_name):
    """Plot scatter plot ground vs sat"""
    sat_data = get_sat_data_at_ground_coords(gb_data, sat_data)

    gb_ch4, sat_ch4 = get_matching_data(gb_data, sat_data)

    plt.scatter(gb_ch4, sat_ch4, alpha=0.7)

    plt.xlabel(f"{station_name} CH4")
    plt.ylabel("Satellite XCH4")
    plt.title(f"Satellite vs {station_name} CH4")
    plt.grid(True)
    plt.savefig(f"{plots_path}sat_vs_AGAGE_{station_name}_scatter.png", dpi=300)
    plt.close()


def get_station_code(filename):
    """Return station code after first _"""
    return Path(filename).stem.split("_")[1]


if __name__ == "__main__":
    # AGAGE datasets
    some_files = sorted(data_path.glob("*-20251230.nc"))
    some_files.append(
        Path(
            "/home/anna_lanteri/data/ground_based_data/AGAGE/agage_cgo_ch4_monthly-baseline-20250123.nc"
        )
    )
    # OBD4MIPs
    sat_default = 1.0e20
    sat_data = xr.open_dataset(
        f"{sat_path}/200301_202312-C3S-L3_XCH4-GHG_PRODUCTS-MERGED-MERGED-OBS4MIPS-MERGED-v4.6.nc"
    )
    sat_data["xch4"] = sat_data["xch4"].where(sat_data["xch4"] != sat_default, np.nan)

    for file in some_files:
        ds = xr.open_dataset(file)
        ds["mf"] = ds["mf"].where(ds["mf"] > 0, np.nan)
        station = get_station_code(file)

        # plot_matching_data(ds, sat_data, station)
        scatter_plot(ds, sat_data, station)

        ds.close()
