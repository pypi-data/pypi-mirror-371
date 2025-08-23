# -*- coding: utf-8 -*-
"""
Retrieve and process **bathymetry** information.

.. dropdown:: Copyright (C) 2023-2025 Technical University of Denmark, R.E.G. Mounet
    :color: primary
    :icon: law

    *This code is part of the NetSSE software.*

    NetSSE is free software: you can redistribute it and/or modify it under 
    the terms of the GNU General Public License as published by the Free 
    Software Foundation, either version 3 of the License, or (at your 
    option) any later version.

    NetSSE is distributed in the hope that it will be useful, but WITHOUT 
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or 
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License 
    for more details.

    You should have received a copy of the GNU General Public License along 
    with this program.  If not, see https://www.gnu.org/licenses/.

    To credit the author, users are encouraged to use below reference:

    .. code-block:: text

        Mounet, R. E. G., & Nielsen, U. D. NetSSE: An open-source Python package 
        for network-based sea state estimation from ships, buoys, and other 
        observation platforms (version 2.1). Technical University of Denmark, 
        GitLab. August 2025. https://doi.org/10.11583/DTU.26379811.

*Last updated on 25-03-2025 by R.E.G. Mounet*

"""

from glob import glob
import io
import zipfile
import requests
import cartopy.io.shapereader as shpreader
import numpy as np

def load_bathymetry(lonmin,lonmax,latmin,latmax,zip_file_url=None):
    """Retrieve, read, and process a zip file from Natural Earth containing bathymetry shapefiles.
    
    The function reads the shapefiles contained in the zip file using the `cartopy.io.shapereader` module. The shapefiles are sorted by depth, from the surface to the bottom. The function returns a dictionary containing the shapefiles and a list of the depths in the shapefiles. 
    
    Parameters
    ----------
    lonmin : float
        Minimum longitude of the area of interest in degrees East.
    lonmax : float
        Maximum longitude of the area of interest in degrees East.
    latmin : float
        Minimum latitude of the area of interest in degrees North.
    latmax : float
        Maximum latitude of the area of interest in degrees North.
    zip_file_url : str, optional
        URL of the zip file containing the shapefiles. By default, the function accesses the bathymetry data from Natural Earth through the Amazon Web Services (https://registry.opendata.aws/naturalearth).
    
    Returns
    -------
    depths : list
        List of the depths in the shapefiles for the specified area.
    shp_dict : dict
        Dictionary containing the shapefiles.

    See Also
    --------
    netsse.tools.viz.plot_bathymetry : Plot the bathymetry map.
    
    References
    ----------
    1. North American Cartographic Information Society. "AWS Marketplace: Natural Earth". Amazon
       Sustainability Data Initiative, https://registry.opendata.aws/naturalearth (accessed on 25-03-2025).
    2. Natural Earth (2009-2025). Free vector and raster map data. 
       https://www.naturalearthdata.com/ (accessed on 25-03-2025).
    3. Met Office (2010-2015). Cartopy: a cartographic Python library with a Matplotlib interface.  
       Exeter, Devon, UK. https://scitools.org.uk/cartopy (accessed on 25-03-2025).

    Example
    -------
    >>> depths, shp_dict = load_bathymetry(lonmin=0, lonmax=10, latmin=50, latmax=60)
    """

    # Default URL for Natural Earth bathymetry data
    if zip_file_url is None:
        zip_file_url = 'https://naturalearth.s3.amazonaws.com/'+\
                       '10m_physical/ne_10m_bathymetry_all.zip'

    # Download and extract shapefiles
    r = requests.get(zip_file_url)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall("ne_10m_bathymetry_all/")

    # Read shapefiles, sorted by depth
    shp_dict = {}
    files = glob('ne_10m_bathymetry_all/*.shp')
    assert len(files) > 0
    files.sort()
    depths = []
    for f in files:
        depth = '-' + f.split('_')[-1].split('.')[0]  # depth from file name
        depths.append(depth)
        bbox = (lonmin, latmin, lonmax, latmax)  # (x0, y0, x1, y1)
        nei = shpreader.Reader(f, bbox=bbox)
        shp_dict[depth] = nei
    depths = np.array(depths)[::-1]  # sort from surface to bottom

    return depths, shp_dict