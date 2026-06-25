"""
Plotting trends for CH4 for all ground based observation stations from NOAA

"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

data_path = Path(
    "/home/anna_lanteri/data/ground_based_data/NOAA/ch4_surface-insitu_ccgg_netCDF/"
)
plots_path = "/home/anna_lanteri/code/cmip-ghg-forcing/plots/"

# Mauna Loa, Hawaii, 01/1987
# Mauna Kea, Hawaii, 12/2022
# American Samoa, 04/2025
# Utqiaġvik, Alaska, 04/1987


def plot_trends(files, title, save_file):
    """Plot trends of NOAA ground based obs"""
    colors = ["blue", "orange", "green", "red"]
    for file, color in zip(files, colors):
        ds = xr.open_dataset(file)
        ds["value"] = ds["value"].where(ds["value"] >= 0, np.nan)
        plt.plot(ds["time"], ds["value"], label=file.stem)

        plt.fill_between(
            ds["time"],
            ds["value"] - ds["value_std_dev"],
            ds["value"] + ds["value_std_dev"],
            alpha=0.2,
            color=color,
        )

    plt.legend()

    plt.title(title)
    plt.savefig(f"{plots_path}{save_file}.png", format="png")


files = sorted(data_path.glob("ch4_*_MonthlyData.nc"))

plot_trends(files, title="Ground based obs", save_file="NOAA_gb_trends")
