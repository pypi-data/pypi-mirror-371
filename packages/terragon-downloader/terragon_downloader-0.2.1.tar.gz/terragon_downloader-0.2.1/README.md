# Terragon
<p align="center">
    <a href="https://github.com/drnhhl/terragon"><img src="https://github.com/drnhhl/terragon/raw/main/docs/_static/logo.png" style="width: 200px" ></a>
</p>
<p align="center">
    <em>Terragon - Earth(Poly)gon. Create EO Minicubes from Polygons and simplify EO Data downloading.</em>
</p>
<p align="center">
    <a href='https://terragon.readthedocs.io/en/latest/?badge=latest'>
        <img src='https://img.shields.io/badge/Readthedocs-%23000000.svg?style=for-the-badge&logo=readthedocs&logoColor=white' alt='Documentation' />
    </a>
    <a href="https://github.com/drnhhl/terragon" target="_blank">
        <img src="https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white" alt="GitHub">
    </a>
</p>
<p align="center">
    <a href='https://pypi.python.org/pypi/terragon-downloader'>
        <img src='https://img.shields.io/pypi/v/terragon-downloader.svg' alt='PyPI' />
    </a>
    <a href="https://opensource.org/licenses/MIT" target="_blank">
        <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License">
    </a>
</p>

You want to download Earth Observation data but don't want to spend hours just for accessing all different APIs? Then this is for you!

We currently support these data providers:
- [Planetary Computer (pc)](https://planetarycomputer.microsoft.com/catalog)
- [Google Earth Engine (gee)](https://developers.google.com/earth-engine/datasets)
- [Copernicus Data Space Ecosystem (cdse)](https://dataspace.copernicus.eu/explore-data/data-collections) (not all collections supported)
- [Alaska Satellite Facility (asf)](https://asf.alaska.edu/how-to/data-basics/datasets-available-from-asf-sar-daac/) (not all collections supported)

## Usage
### Installation
Install the package via PyPi:
```python
pip install terragon-downloader
```
Optional with the dependency you want to use:
```python
pip install terragon-downloader[pc]
```
### Downloading EO data
```python
import terragon
import geopandas as gpd
from shapely.geometry import Polygon

# example polygon
gdf = gpd.GeoDataFrame(geometry=[Polygon(
            [(446993, 3383569),
            (446993, 3371569),
            (434993, 3371569),
            (434993, 3383569),
            (446993, 3383569)])],
            crs='EPSG:32616' # the dataset will receive the crs from the dataframe
            )

# initialize backend/data source (here planetary computer)
tg = terragon.init('pc')

# download data
da = tg.create(shp=gdf, # polygon in geopandas format (minicube will receive the same CRS)
               collection="sentinel-2-l2a", # name of the collection
               start_date="2021-01-01", # start date of tiles
               end_date="2021-01-05", # end date of tiles
               bands=["B02", "B03", "B04"], # bands to retrieve
               resolution=20, # pixel size in meter
               )
```
Other data backends work with the same principle, check out the [Demos](https://github.com/drnhhl/terragon/tree/main/docs/demo_files).

## Limitations
Be aware that depending on the collection the data is not mosaicked.

## Contribute
You found a bug or a data source is missing? We encourage you to raise an issue or provide a PR.

We are looking for contributors to add more collections to CDSE. Please get in touch if you are interested.

## License
This work is licensed under the MIT license.

## Citation
If you use this work, please consider citing the following paper: Coming soon.

## Acknowledgement
This work is inspired by [cubo](https://github.com/ESDS-Leipzig/cubo)