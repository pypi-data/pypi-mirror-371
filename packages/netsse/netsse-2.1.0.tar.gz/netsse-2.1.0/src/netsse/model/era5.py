# -*- coding: utf-8 -*-
"""
Retrieve and process sea state information from the **ERA5 dataset**.

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

*Last updated on 26-02-2025 by R.E.G. Mounet*

"""

import sys
from pathlib import Path
import cdsapi
import pandas as pd
import numpy as np


def retrieve_dirwavespec(index_month=0, folder_output="../Output/"):
    """Retrieve directional wave spectrum data from the ERA5 dataset (Hersbach et al., 2020, 2023).

    The function retrieves data from the ERA5 dataset for a specific period of time and geographical area. The latter must be specified in a dedicated `'ERA5_request.csv' <https://gitlab.gbar.dtu.dk/regmo/NetSSE/-/blob/wip/docs/examples/ERA5_request.csv>`_ file at the location path given in ``folder_output`` informing the spatial and temporal coverage of the data to be retrieved. The content of the file must follow the example below (including the header line!):

    .. code-block:: text

      ,Year,Month,Day_start,Day_end,NrDays,Longitude_min,Longitude_max,Latitude_min,Latitude_max
      0,2007,9,12,25,30,-55.0,-5.0,46.0,50.0
      1,2007,10,12,26,31,-55.0,-5.0,45.0,50.0


    There can be as many lines as needed in the ERA5 request file, each line corresponding to a single retrieval request of data located all within the same month. The function retrieves the directional wave spectrum data for the request line having the index ``index_month`` in the file. The default value for ``index_month`` is ``0``, which means to submit the first request in the request file.

    The data is retrieved for the month and year specified in the `'Month'` and `'Year'` columns of the request file; e.g., September 2007 in the first request contained in the above example). The retrieval period covers from the start day at 00:00 to the end day at 23:00; e.g., from 12 September 2007 at 00:00 to 25 September 2007 at 23:00 in the first request contained in the above example.

    Longitudes are specified in degrees East and latitudes in degrees North. The data is retrieved for the geographical area defined by the minimum and maximum longitudes and latitudes; e.g., from 46.0 to 50.0 degrees North and from -55.0 to -5.0 degrees East in the first request contained in the above example. The spatial resolution is fixed to 0.5 degrees in both latitude and longitude.

    The data is retrieved using the Copernicus Climate Data Store (CDS) API. The user must have a valid CDS API key to access the data. The downloaded data is stored in a NetCDF file at the location path specified in the variable ``folder_output``. The default value for ``folder_output`` is ``'../Output/'``.

    References
    ----------
    1. Hersbach, H., Bell, B., Berrisford, P., Hirahara, S., Horányi, A., Muñoz-Sabater, J., Nicolas,
       J., Peubey, C., Radu, R., Schepers, D., Simmons, A., Soci, C., Abdalla, S., Abellan, X.,
       Balsamo, G., Bechtold, P., Biavati, G., Bidlot, J., Bonavita, M., De Chiara, G., Dahlgren, P.,
       Dee, D., Diamantakis, M., Dragani, R., Flemming, J., Forbes, R., Fuentes, M., Geer, A.,
       Haimberger, L., Healy, S., Hogan, R. J., Hólm, E., Janisková, M., Keeley, S., Laloyaux, P.,
       Lopez, P., Lupu, C., Radnoti, G., de Rosnay, P., Rozum, I., Vamborg, F., Villaume, S., and
       Thépaut, J. N. The ERA5 global reanalysis. Quarterly Journal of the Royal Meteorological
       Society 146, 730 (2020), 1999–2049, DOI: 10.1002/qj.3803.
    2. Hersbach, H., Bell, B., Berrisford, P., Biavati, G., Horányi, A., Muñoz Sabater, J., Nicolas,
       J., Peubey, C., Radu, R., Rozum, I., Schepers, D., Simmons, A., Soci, C., Dee, D., Thépaut,
       J-N. (2023): ERA5 hourly data on single levels from 1940 to present. Copernicus Climate Change
       Service (C3S) Climate Data Store (CDS), DOI: 10.24381/cds.adbb2d47  (Accessed on 26-02-2025).

    Example
    -------
    To retrieve the directional wave spectrum data for the month with index 1 in the file `'ERA5_request.csv'` stored in the folder `'../Output/'`, run:

    >>> retrieve_dirwavespec(index_month=1,folder_output='../Output/')
    >>> # Output:
    >>> # Retrieving ERA5 data for the month with index 1...
    >>> # Selected dates: 2007-10-12/to/2007-10-26
    >>> # Selected area: 50.0/-55.0/45.0/-5.0
    >>> # The downloaded file is stored at '../Output/ERA5_2D_spectra_2007-10.nc'.
    """
    try:
        c = cdsapi.Client()
    except Exception:
        sys.exit(
            "The CDS API client could not be initiated. Please check your CDS API key."
        )

    # Import the spatial boundaries for the specific month:
    input_file = Path(folder_output + "ERA5_request.csv")
    if not input_file.is_file():
        sys.exit(
            'The file "ERA5_request.csv" is missing from the folder "%s".'
            % folder_output
        )

    # Build the date and area strings:
    df_selec_areas = pd.read_csv(input_file)
    selec_month = df_selec_areas.loc[index_month]
    year = int(selec_month.loc["Year"])
    month = int(selec_month.loc["Month"])
    day_start, day_end, minlon_month, maxlon_month, minlat_month, maxlat_month = (
        np.int32(
            selec_month.loc[
                [
                    "Day_start",
                    "Day_end",
                    "Longitude_min",
                    "Longitude_max",
                    "Latitude_min",
                    "Latitude_max",
                ]
            ]
        )
    )
    date_str = "%04.0f-%02.0f-%02.0f/to/%04.0f-%02.0f-%02.0f" % (
        year,
        month,
        day_start,
        year,
        month,
        day_end,
    )
    area_str = "%s/%s/%s/%s" % (maxlat_month, minlon_month, minlat_month, maxlon_month)

    # Define the output file:
    filename_output = folder_output + "ERA5_2D_spectra_%04.0f-%02.0f.nc" % (year, month)

    print("Retrieving ERA5 data for the month with index %s..." % index_month)
    print("Selected dates: ", date_str)
    print("Selected area: ", area_str)

    # Retrieve the directional wave spectrum data:
    c.retrieve(
        "reanalysis-era5-complete",
        {
            "class": "ea",
            "date": date_str,
            "direction": "1/2/3/4/5/6/7/8/9/10/11/12/13/14/15/16/17/18/19/20/21/22/23/24",
            "area": area_str,
            "grid": "0.5/0.5",
            "expver": "1",
            "frequency": "1/2/3/4/5/6/7/8/9/10/11/12/13/14/15/16/17/18/19/20/21/22/23/24/25/26/27/28/29/30",
            "param": "251.140",
            "stream": "wave",
            "time": "00/to/23/by/1",
            "type": "an",
            "format": "netcdf",
        },
        filename_output,
    )

    print("The downloaded file is stored at %s." % filename_output)


if __name__ == "__main__":
    index_month = int(sys.argv[1])
    retrieve_dirwavespec(index_month=index_month)
