"""
Makes a gif of global satellite data
"""

import os

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from PIL import Image

sat_default = 1.0e20

plots_path = "/home/anna_lanteri/code/cmip-ghg-forcing/plots/"

sat_path = "/home/anna_lanteri/data/satellite_data/OBS4MIPs/"
sat_data = xr.open_dataset(
    f"{sat_path}/200301_202312-C3S-L3_XCH4-GHG_PRODUCTS\
                           -MERGED-MERGED-OBS4MIPS-MERGED-v4.6.nc"
)
sat_data["xch4"] = sat_data["xch4"].where(sat_data["xch4"] != sat_default, np.nan)

data = sat_data["xch4"]

frames = []

for i in range(len(data["time"])):
    plt.figure(figsize=(10, 6))
    data[i, :, :].plot()
    plt.title(f"xch4 - Month {i + 1}")

    temp_file = f"temp_frame_{i}.png"
    plt.savefig(temp_file, format="png", bbox_inches="tight", dpi=100)
    plt.close()

    frames.append(Image.open(temp_file))

gif_path = plots_path + "xch4_all_months.gif"

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
