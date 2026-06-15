"""

Download ground based data from:

* NOAA 
* AGAGE (not yet)

"""

import logging
logging.basicConfig(level="INFO")

import os
from pathlib import Path
import requests

base_url = "https://gml.noaa.gov/aftp/data/greenhouse_gases/"

def download_ground_based_data(download_path, config):

    download_path = Path(download_path).expanduser().absolute()
    os.makedirs(download_path, exist_ok=True)
    print(f"Downloading to: {download_path!s}")


    gas = config['gas']
    folder = config['folder']
    sampling = config['sampling']

    url = f"{base_url}{gas}/{folder}/surface/{gas}_surface-{sampling}_ccgg_netCDF.zip"

    response = requests.get(url, timeout=10)
    print(f"Request URL: {url}")
    print(f"Response status code: {response.status_code}")
    response.raise_for_status()

    with open(download_path / f"noaa_{gas}_surface_{sampling}.zip", "wb") as f:
        f.write(response.content)

    logging.info(f"downloaded NOAA-zip ({gas}-{sampling}) to {download_path!s}")


if __name__ == "__main__":

    download_path = Path('~/data/ground_based_data/NOAA/')

    config = {
        'gas' : 'ch4',
        'folder' : 'in-situ',
        'sampling' : 'insitu'
    }

    download_ground_based_data(download_path, config)