"""
Plots for quick visualization of L3 data from OBS4MIP
"""

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

sat_default = 1.0e20
gas = 'co2'
sat_gas = f"x{gas}"

if gas == 'co2':
    uppercase_gas = "CO2"
elif gas == 'ch4':
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


sat_data[sat_gas] = sat_data[sat_gas].where(sat_data[sat_gas] != sat_default, np.nan)
sat_data[f"{sat_gas}_stderr"] = sat_data[f"{sat_gas}_stderr"].where(
    sat_data[f"{sat_gas}_stderr"] != sat_default, np.nan
)

sat_data[sat_gas].mean("lon").plot()
plt.title(f"{sat_gas} zonal averaged")
plt.savefig(f"{plots_path}{sat_gas}_zonal.png", format="png", bbox_inches="tight")
plt.close()

sat_data[f"{sat_gas}_stderr"].mean("lon").plot()
plt.title(f"{sat_gas} stderr ")
plt.savefig(f"{plots_path}{sat_gas}_std.png", format="png", bbox_inches="tight")
plt.close()
