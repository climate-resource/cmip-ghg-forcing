"""
Plots for quick visualization of L3 data from OBS4MIP
"""

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

sat_default = 1.e+20

home_path = '/home/anna_lanteri/'
esgf_path = '/data/data--processed/output-bundles/v1.0.0/data/processed/esgf-ready/'
path_interp = f"{home_path}{esgf_path}/input4MIPs/CMIP7/CMIP/CR/CR-CMIP-1-0-0/atmos/mon/ch4/gnz/v20250228/"  # noqa: E501
plots_path = f"{home_path}/code/cmip-ghg-forcing/plots/"

sat_path = '/home/anna_lanteri/data/satellite_data/OBS4MIPs/'
sat_data = xr.open_dataset(f"{sat_path}/200301_202312-C3S-L3_XCH4-GHG_PRODUCTS-MERGED-MERGED-OBS4MIPS-MERGED-v4.6.nc")  # noqa: E501
sat_data['xch4'] = sat_data['xch4'].where(sat_data['xch4'] != sat_default, np.nan)
sat_data['xch4_stderr'] = sat_data['xch4_stderr'].where(
                                    sat_data['xch4_stderr'] != sat_default, np.nan
                                    )

sat_data['xch4'].mean('lon').plot()
plt.title('xch4 zonal averaged')
plt.savefig(f"{plots_path}xch4_zonal.png", format="png", bbox_inches="tight")
plt.close()

sat_data['xch4_stderr'].mean('lon').plot()
plt.title('xch4 stderr ')
plt.savefig(f"{plots_path}xch4_std.png", format="png", bbox_inches="tight")
plt.close()
