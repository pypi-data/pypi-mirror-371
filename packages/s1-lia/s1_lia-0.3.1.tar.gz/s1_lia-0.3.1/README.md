# s1_lia

**s1_lia** is a Python package for searching, downloading, and merging Sentinel-1 local incidence angle (LIA) files. It simplifies access to static OPERA RTC products by handling AOI validation, ASF search, reliable downloading, and data merging by relative orbit.

<img src="https://github.com/ZachHoppinen/s1_lia/blob/main/title-img.png" width="800">

---

## Features

- Validate and normalize Areas of Interest (AOI) from WKT, GeoJSON, Shapely, or GeoPandas objects.
- Search ASF for static OPERA Sentinel-1 RTC products overlapping the AOI.
- Download local incidence angle GeoTIFF files robustly with retry support.
- Merge downloaded files by relative orbit into combined GeoTIFFs.
- Generates human-readable file name stems based on AOI centroid and optional reverse geocoding.

---

## Installation

Install via pip:

```bash
pip install s1_lia
```

## Usage

Simple aoi designation, data search and download (packaged into `get_opera_lia`), and plotting to check results.

See documentation of `get_opera_lia` for all optional arguments including to select only a certain relative orbit and setting file names.

```python
import s1_lia

# Define AOI as WKT polygon string
aoi_wkt = 'POLYGON((-107.5 37.6,-107.5 38.0,-108.0 38.0,-108.0 37.6,-107.5 37.6))'

# Define directory to store downloaded and merged files
data_dir = "./data"

# Run full workflow: search, download, merge
merged_files = s1_lia.get_opera_lia(aoi_wkt, data_dir)

print("Merged incidence angle files:")
for f in merged_files:
    print(f)

import xarray as xr
import shapely
import matplotlib.pyplot as plt
xr.open_dataarray(merged_files[0]).rio.reproject('EPSG:4326').plot()
x, y = shapely.from_wkt(aoi_wkt).exterior.xy
plt.gca().plot(x,y, color = 'k', linewidth = 4)
```

## Functions
`find_static_opera_files(aoi, relative_orbit=None, ...)`: Search ASF for matching OPERA products.

`download_results(results, data_directory, ...)`: Download local incidence angle files.

`merge_lia_by_relative_orbit(downloaded_files, output_directory, name_stem)`: Merge downloaded files by relative orbit.

`generate_name_stem(aoi, use_place_name=True)`: Generate descriptive filename stem based on AOI centroid.

`get_opera_lia(...)`: Runs full workflow combining above steps.

## Development
To install in development mode:

```bash
git clone https://github.com/zachhoppinen/s1_lia.git
cd s1_lia
pip install -e .
```

Run tests

```bash
pytest tests/
```

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments
Built on top of the ASF Search Python API.

Uses Shapely, GeoPandas, xarray, and rioxarray.

Data from:
https://www.earthdata.nasa.gov/data/catalog/asf-opera-l2-cslc-s1-v1-1
https://d2pn8kiwq2w21t.cloudfront.net/documents/ProductSpec_RTC-S1.pdf

Please use citation:

NASA/JPL/OPERA. (2023). <i>OPERA Co-registered Single Look Complex from Sentinel-1 validated product (Version 1)</i> [Data set]. NASA Alaska Satellite Facility Distributed Active Archive Center. https://doi.org/10.5067/SNWG/OPERA_L2_CSLC-S1_V1 Date Accessed: 2025-08-08

Inspiration from: 
https://github.com/egagli/generate_sentinel1_local_incidence_angle_maps

## Contact
For questions or feedback, open an issue or contact Zach Hoppinen @ zmhoppinen@alaska.edu

## To bump version and trigger pypi upload

```bash
bump2version patch # or minor major
git push origin vx.x.x # TODO this should not be needed.
```
