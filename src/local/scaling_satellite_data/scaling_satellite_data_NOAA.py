"""
Linear fit for scaling factor
"""

import numpy as np
import xarray as xr

sat_default = 1.0e20

plots_path = "/home/anna_lanteri/code/cmip-ghg-forcing/plots/"
data_path = "/home/anna_lanteri/data/"
ground_path = f"{data_path}ground_based_data/NOAA/ch4_surface-insitu_ccgg_netCDF/"
sat_path = f"{data_path}/satellite_data/OBS4MIPs/"
output_file = f"{data_path}/scaled/OBS4MIPs_to_MLO_basic_fit.nc"

sat_data = xr.open_dataset(
    f"{sat_path}/200301_202312-C3S-L3_XCH4-GHG_PRODUCTS-MERGED-MERGED-OBS4MIPS-MERGED-v4.6.nc"
)
sat_data["xch4"] = sat_data["xch4"].where(sat_data["xch4"] != sat_default, np.nan)

# Using scaling from one NOAA station for testing purposes
sat_data["xch4"] = sat_data["xch4"] * 1.022

sat_data.attrs["Scaling"] = [
    "Fit: linear",
    "Data: NOAA MLO ground based observations",
]

sat_data.to_netcdf(output_file)
