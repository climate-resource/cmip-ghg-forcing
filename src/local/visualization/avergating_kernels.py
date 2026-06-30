"""
Plots for quick visualization of averaging kernels
"""

import os

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from PIL import Image

sat_default = 1.0e20
gas = "co2"
sat_gas = f"x{gas}"

if gas == "co2":
    uppercase_gas = "CO2"
elif gas == "ch4":
    uppercase_gas = "CH4"
else:
    raise ValueError("gas_not_supported")

home_path = "/home/anna_lanteri/"
esgf_path = "/data/data--processed/output-bundles/v1.0.0/data/processed/esgf-ready/"
plots_path = f"{home_path}/code/cmip-ghg-forcing/plots/"

sat_path = "/home/anna_lanteri/data/satellite_data/OBS4MIPs/"
sat_data = xr.open_dataset(
    f"{sat_path}/200301_202312-C3S-L3_X{uppercase_gas}-GHG_PRODUCTS-MERGED-MERGED-OBS4MIPS-MERGED-v4.6.nc"
)

var = 'vmr_profile_co2_apriori'

sat_data[var] = sat_data[var].where(sat_data[var] != sat_default, np.nan)

# Plot surface AK gif over time

data = sat_data[var][:,-1,:,:]

frames = []

for i in range(len(data["time"])):
    plt.figure(figsize=(10, 6))
    data[i, :, :].plot()
    plt.title(f"{sat_gas} VMR- Month {i + 1}")

    temp_file = f"temp_frame_{i}.png"
    plt.savefig(temp_file, format="png", bbox_inches="tight", dpi=100)
    plt.close()

    frames.append(Image.open(temp_file))

gif_path = f"{plots_path}/{sat_gas}_surface_vmr_all_months.gif"

frames[0].save(
    gif_path,
    save_all=True,
    append_images=frames[1:],
    duration=500,
    loop=0,
    optimize=True,
)

# Remove all temp files
for i in range(len(data["time"])):
    os.remove(f"temp_frame_{i}.png")



# make a gif of the kernels

data = sat_data[var].mean('lon')

frames = []

for i in range(len(data["time"])):
    plt.figure(figsize=(10, 6))
    data[i, :, :].plot()
    plt.title(f"{sat_gas} VMR- Month {i + 1}")

    temp_file = f"temp_frame_{i}.png"
    plt.savefig(temp_file, format="png", bbox_inches="tight", dpi=100)
    plt.close()

    frames.append(Image.open(temp_file))

gif_path = f"{plots_path}/{sat_gas}_VMR_all_months.gif"

frames[0].save(
    gif_path,
    save_all=True,
    append_images=frames[1:],
    duration=500,
    loop=0,
    optimize=True,
)

# Remove all temp files
for i in range(len(data["time"])):
    os.remove(f"temp_frame_{i}.png")
