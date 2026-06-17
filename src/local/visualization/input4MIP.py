import xarray as xr
import matplotlib.pyplot as plt
import numpy as np


home_path = "/home/anna_lanteri/"
plots_path = f"{home_path}/code/cmip-ghg-forcing/plots/"
path_input4mip = f"{home_path}/data/data--processed/output-bundles/v1.0.0/data/processed/esgf-ready/input4MIPs/CMIP7/CMIP/CR/CR-CMIP-1-0-0/"
path_base_zonal_ch4 = f"{path_input4mip}/atmos/mon/ch4/gnz/v20250228/"
path_zonal_ch4 = f"{path_base_zonal_ch4}/ch4_input4MIPs_GHGConcentrations_CMIP_CR-CMIP-1-0-0_gnz_175001-202212.nc"

zonal_ch4 = xr.open_dataset(path_zonal_ch4)

zonal_ch4['ch4'].plot()
plt.title('Zonal Ch4 from input4MIP')
plt.savefig(plots_path + "zonal_ch4_input4MIP.png", format="png", bbox_inches="tight")
plt.close() 

# Zooming in on the time where we have OBS4MIPs data
subset_zonal_ch4 = zonal_ch4['ch4'].sel(time=slice('2003-01-01', '2023-12-31')) / 1e9
subset_zonal_ch4.plot()
plt.title('Zonal Ch4 from input4MIP, from 2003')
plt.savefig(plots_path + "zonal_ch4_input4MIP_from2003.png", format="png", bbox_inches="tight")
plt.close() 
