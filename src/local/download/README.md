# Notes on downloading data

## Copernicus data: OBS4MIPs

We use the ecmwf API as it provides some advanced features. To use this API, set up a virtual env and :

```
python3 -m venv ~/venv_copernicus
source ~/venv_copernicus/bin/activate
pip install ecmwf-api-client ecmwf-datastores-client
```

TODO: automate in the MAKE file