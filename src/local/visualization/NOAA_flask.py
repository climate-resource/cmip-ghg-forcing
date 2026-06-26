"""
Plotting trends for CH4 for all ground based observation stations from NOAA

"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

gas = "ch4"
method = "flask"

data_path = Path(
    f"/home/anna_lanteri/data/ground_based_data/NOAA/{gas}_surface-{method}_ccgg_netCDF/"
)

plots_path = "/home/anna_lanteri/code/cmip-ghg-forcing/plots/"


def plot_trends(files, title, save_file):
    """Plot trends of NOAA ground based obs"""
    fig, ax = plt.subplots()

    for file in files:
        ds = xr.open_dataset(file)
        ds["value"] = ds["value"].where(ds["value"] >= 0, np.nan)
        ds = filter_qc(ds, filter_config, qc_var="qcflag")


        # Plot the line and get its color
        line, = ax.plot(ds["time"], ds["value"], label=file.stem)
        color = line.get_color()

        # Use the same color for the uncertainty band
        ax.fill_between(
            ds["time"],
            ds["value"] - ds["value_unc"],
            ds["value"] + ds["value_unc"],
            color=color,
            alpha=0.2,
        )
        print('one down')

    #ax.legend()
    ax.set_title(title)

    fig.savefig(f"{plots_path}{save_file}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)



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

files = sorted(data_path.glob(f"{gas}_*_event.nc"))

plot_trends(files, title="Ground based obs, selecting TFF", save_file="NOAA_flask_trends_TFF")
