"""
Plotting trends for CH4 for all ground based observation stations from NOAA

"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

gas = "co2"

data_path = Path(
    f"/home/anna_lanteri/data/ground_based_data/NOAA/{gas}_surface-insitu_ccgg_netCDF/"
)
plots_path = "/home/anna_lanteri/code/cmip-ghg-forcing/plots/"

# Mauna Loa, Hawaii, 01/1987
# Mauna Kea, Hawaii, 12/2022
# American Samoa, 04/2025
# Utqiaġvik, Alaska, 04/1987

def plot_trends(files, title, save_file):
    """Plot trends of NOAA ground based obs"""
    fig, ax = plt.subplots()

    for file in files:
        ds = xr.open_dataset(file)
        ds["value"] = ds["value"].where(ds["value"] >= 0, np.nan)

        # Plot the line and get its color
        line, = ax.plot(ds["time"], ds["value"], label=file.stem)
        color = line.get_color()

        # Use the same color for the uncertainty band
        ax.fill_between(
            ds["time"],
            ds["value"] - ds["value_std_dev"],
            ds["value"] + ds["value_std_dev"],
            color=color,
            alpha=0.2,
        )

    ax.legend()
    ax.set_title(title)

    fig.savefig(f"{plots_path}{save_file}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


files = sorted(data_path.glob(f"{gas}_*_MonthlyData.nc"))
print(len(files))

plot_trends(files, title="Ground based obs", save_file="NOAA_gb_trends")
