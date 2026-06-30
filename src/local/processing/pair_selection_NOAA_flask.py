"""
Plotting trends for CH4 for all flask observation stations from NOAA

"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

from local.processing.utils import (
    extract_ground_data,
    get_sat_data,
    get_sat_data_at_ground_coords,
    get_scaling,
    get_station_code,
    make_sat_times_mask,
    set_time_at_start_of_month,
)

gas = "ch4"
method = "flask"

gas = "ch4"
method = "flask"

data_path = Path(
    f"/home/anna_lanteri/data/ground_based_data/NOAA/{gas}_surface-{method}_ccgg_netCDF/"
)

plots_path = "/home/anna_lanteri/code/cmip-ghg-forcing/plots/"

def filter_qc(
    ds,
    filter_config,
    qc_var="qcflag"
):
    """
    Filter an xarray Dataset based on NOAA 3-character QC flags.
    """
    # Convert bytes -> unicode strings if needed
    flags = ds[qc_var].astype(str)

    mask = xr.ones_like(flags, dtype=bool)

    if filter_config['reject']:
        mask &= flags.str[0] == "."

    if filter_config['selection']:
        mask &= flags.str[1] == "."

    if filter_config['information']:
        mask &= flags.str[2] == "."

    return ds.where(mask, drop=True)


filter_config = {
    'reject':True,
    'selection':False,
    'information':False,
}

def scatter_plot(gb, sat, gas, station_name):
    """Plot scatter plot ground vs sat"""
    sat[f"x{gas}"] = sat[f"x{gas}"].where(sat[f"x{gas}"] >= 0, np.nan)

    gb_matched, sat_matched = get_matching_data(gb, sat, gas)

    plt.scatter(gb_matched, sat_matched, alpha=0.7)

    plt.xlabel(f"{station_name} {gas}")
    plt.ylabel(f"Satellite x{gas}")
    plt.title(f"Satellite vs {station_name} {gas}")
    plt.grid(True)
    plt.savefig(f"{plots_path}sat_vs_NOAA_flask_{station_name}_scatter_{gas}.png", dpi=300)
    plt.close()

def plot_matching_data(gb, sat, gas, station_name):
    """Plot matching points in over time"""
    scaling = get_scaling(gas)

    sat = get_sat_data_at_ground_coords(gb, sat)

    mask = make_sat_times_mask(gb, sat, gas)

    gb_time = gb["time"][mask]
    gb_gas = gb["value"][mask] / scaling

    sat[f"x{gas}"].plot(
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
    plt.savefig(f"{plots_path}sat_over_{station_name}_and_NOAA_flask_{gas}.png", format="png")
    plt.close()


def get_matching_data(gb, sat, gas):
    """Return matched monthly-mean ground and satellite observations."""
    sat_ground = get_sat_data_at_ground_coords(gb, sat)

    gb_times, gb_values = extract_ground_data(gb, gas)

    # Convert both time arrays to monthly timestamps
    gb_months = pd.DatetimeIndex(gb_times).to_period("M").to_timestamp()
    sat_months = pd.DatetimeIndex(sat_ground.time.values).to_period("M").to_timestamp()

    # Average ground observations within each month
    gb_series = (
        pd.Series(gb_values, index=gb_months)
        .groupby(level=0)
        .mean()
    )

    # Satellite: keep only finite values and average in case of duplicates
    valid_sat = np.isfinite(sat_ground["x" + gas].values)

    sat_series = (
        pd.Series(
            sat_ground["x" + gas].values[valid_sat],
            index=sat_months[valid_sat],
        )
        .groupby(level=0)
        .mean()
    )

    # Keep only months present in both datasets
    common_months = gb_series.index.intersection(sat_series.index)

    gb_matched = gb_series.loc[common_months].to_numpy()
    sat_matched = sat_series.loc[common_months].to_numpy()

    valid = np.isfinite(gb_matched) & np.isfinite(sat_matched)

    return sat_matched[valid], gb_matched[valid]

if __name__ == "__main__":
    sat_data = get_sat_data(gas)
    files = sorted(data_path.glob(f"{gas}_*_event.nc"))
    print(len(files))

    for file in files[40:45]:
        gb = xr.open_dataset(file)

        gb["value"] = gb["value"].where(gb["value"] > 0, np.nan)
        gb = filter_qc(gb, filter_config, qc_var="qcflag")

        gb = set_time_at_start_of_month(gb)

        station_name = get_station_code(file)
        print(gb['value'].size)



        print(station_name)
        plot_matching_data(gb, sat_data, gas, station_name=station_name)
        print("scatter")
        scatter_plot(gb, sat_data, gas, station_name=station_name)
