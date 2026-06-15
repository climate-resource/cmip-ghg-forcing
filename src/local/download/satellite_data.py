"""

Download satellite data from:

* OBS4MIPs

"""

import os
from pathlib import Path

import logging
logging.basicConfig(level="INFO")

from ecmwf.datastores import Client
client = Client()


def download_satellite_data(download_path:Path , gas: str):
    download_path = Path(download_path).expanduser().absolute()
    print(f"Downloading to: {download_path!s}")

    os.makedirs(download_path, exist_ok=True)

    request = {
        "processing_level": ["level_3"],
        "variable": f"x{gas}",
        "sensor_and_algorithm": "merged_obs4mips",
        "version": ["4_6"],
    }

    if not client.check_authentication():
        raise ValueError("authentification failed")


    target = download_path / f"obs4mips_x{gas}.zip"
    dataset = "satellite-methane"
    client.retrieve(dataset, request, target=str(target))

    return logging.info(f"downloaded OBS4MIPs {gas} data to {target!s}")


if __name__ == "__main__":


    download_path = Path('~/data/satellite_data/OBS4MIPs/')
    gas = 'ch4'


    download_satellite_data(download_path, gas)