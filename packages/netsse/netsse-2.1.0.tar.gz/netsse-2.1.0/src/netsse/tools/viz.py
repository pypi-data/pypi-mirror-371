# -*- coding: utf-8 -*-
"""
**Data visualisation** functions for NetSSE.

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

*Last updated on 05-11-2024 by R.E.G. Mounet*

"""

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import cartopy.crs as ccrs
import numpy as np
from netsse.tools.misc_func import re_range

def plot_dirwavespec(spec, dirs, freqs, unit_dirs='deg', unit_freqs='Hz', levels=None,\
                     cmap='turbo', vmin=None, vmax=None, freq_max=None, show_dirlabels=True,\
                     show_freqlabels=True, ax=None):
    """Plots the input directional wave spectrum in a polar diagram.
    
    The plot shows the power spectral density (PSD) distribution over wave frequencies and 
    directions.

    Parameters
    ----------
    spec : array_like
        Directional wave spectrum to be plotted. This must be a 2-D array of shape either 
        `(Ndirs,Nfreqs)` or `(Nfreqs,Ndirs)`.
    dirs : array_like of shape (`Ndirs`,)
        Directions of the spectrum.
    freqs : array_like of shape (`Nfreqs`,)
        Frequencies of the spectrum.
    unit_dirs : {'deg','rad'}, optional
        Unit of the directions, either ``'deg'`` for degrees or ``'rad'`` for radians. 
        Default is ``'deg'``.
    unit_freqs : {'Hz','rad/s'}, optional
        Unit of the frequencies, either ``'Hz'`` for Hertz or ``'rad/s'`` for radians per second. 
        Default is ``'Hz'``.
    levels : array_like, optional
        Contour levels to use for the plot. If ``None``, levels are automatically determined 
        according to the formula below:

        :math:`vmin*(vmax/vmin)^{i/29}` for :math:`i=0,1,...,29`.
        Default is ``None``.
    cmap : str, optional
        Colormap to use for the plot. Default is ``'turbo'``. 
        
        .. note::
            Other colormap options include ``'viridis'``, ``'plasma'``, ``'inferno'``, ``'magma'``. 
            Visit the `Matplotlib documentation 
            <https://matplotlib.org/stable/tutorials/colors/colormaps.html>`_ for an overview of 
            the options.

    vmin : float, optional
        Minimum value for the colormap. Default is ``None``, which means to use the value 
        :math:`10^{-1/2}`.
    vmax : float, optional
        Maximum value for the colormap. Default is ``None``, which means to use the maximum value
        in ``spec``.

        .. warning::
            ``vmin`` and ``vmax`` are used to set the colormap limits. These options will override the lower and upper limits of ``levels``, if the latter option is used.

    freq_max : float, optional
        Maximum frequency to plot. Default is ``None``, which means to use the maximum frequency in 
        the input data.
    show_dirlabels : {True,False,'compass'}, optional
        Whether to show direction labels. 
        If ``True``, shows labels in degrees. If ``'compass'``, shows compass directions. 
        If ``False``, no labels are shown. Default is ``True``.
    show_freqlabels : {True,False,'all'}, optional
        Whether to show frequency labels. If ``True``, shows only the maximum frequency label. 
        If ``'all'``, shows all labels. If ``False``, no labels are shown. Default is ``True``.
    ax : matplotlib.axes, optional
        Axes object to plot on. If ``None``, a new figure and axes are created. Default is ``None``.

    Returns
    -------
    ax : matplotlib.axes._subplots.PolarAxesSubplot
        The axes object with the plot.

    Example
    -------
    >>> # Generate some example data
    >>> freqs = np.linspace(0.05, 0.5, 50)
    >>> dirs = np.linspace(0, 360, 36)
    >>> spec = np.random.rand(36, 50)
    >>> # Plot the directional wave spectrum
    >>> plot_dirwavespec(spec, dirs, freqs)
    """
    # Identify the dimensions of the spectra:
    Nfreqs = np.size(freqs)
    Ndirs = np.size(dirs)
    ax_freqs = np.where(np.array(spec.shape) == Nfreqs)[0][0]
    ax_dirs = np.where(np.array(spec.shape) == Ndirs)[0][0]
    spec_plot = np.transpose(spec,(ax_dirs,ax_freqs))

    # Headings in radians:
    if unit_dirs == 'deg':
        dirs_rad = np.radians(dirs)
    else:
        dirs_rad = dirs
    dirs_rad = re_range(dirs_rad.flatten(),0,unit='rad')

    # Ensure that the headings are cyclic:
    if np.round(dirs_rad[-1,],4)==np.round(dirs_rad[0,],4):
        dirs_rad[-1,] += 2*np.pi
    else:
        dirs_rad = np.append(dirs_rad,dirs_rad[0,]+2*np.pi)
        Ndirs += 1
        spec_plot = np.append(spec_plot,spec_plot[0,:].reshape(1,Nfreqs),axis=0)

    # Make a meshgrid in angles and frequencies:
    Headings, Freq = np.meshgrid(dirs_rad,freqs)

    # Select the levels for the contour plot:
    spec_plot[np.isnan(spec_plot)] = -1
    if vmin is None:
        min_val = 10**(-0.5)
    else:
        min_val = vmin
    if vmax is None:
        max_val = np.amax(spec_plot)
    else:
        max_val = vmax
    if levels is None:
        levels = 10**np.linspace(np.log10(min_val),np.log10(max_val),30)
    else:
        if vmin is not None:
            levels[0] = vmin
        if vmax is not None:
            levels[-1] = vmax

    norm = cm.colors.LogNorm()
    spec_plot = np.ma.masked_where(spec_plot <= 0,spec_plot)

    # Plot the 2-D wave spectrum:
    if ax is None:
        fig, ax = plt.subplots(subplot_kw={'projection':'polar'},figsize=(4,4))
    else:
        fig = ax.get_figure()
        rows,cols,start,_ = ax.get_subplotspec().get_geometry()
        ax.remove()
        ax = fig.add_subplot(rows,cols,start+1,projection='polar')
    ax.set_theta_direction(-1)
    ax.set_theta_zero_location("N")
    ax.contour(Headings,Freq,spec_plot.T,levels=levels,norm=norm,linewidths=1,cmap=cmap)

    # Set the labels and grid:
    ax.set_xticks(np.arange(np.pi/6,13*np.pi/6,np.pi/6))
    
    match show_dirlabels:
        case True:
            ax.set_xticklabels(['','',r'90$^\circ$','','',r'180$^\circ$','','',\
                                r'270$^\circ$','','',r'0$^\circ$'])
        case 'compass':
            ax.set_xticklabels(['','','E','','','S','','','W','','','N'])
        case False:
            ax.set_xticklabels(['']*12)

    if freq_max is None:
        freq_max = np.max(np.round(freqs,decimals=1))
    dfreq = 0.1*(unit_freqs=='Hz')+0.5*(unit_freqs=='rad/s')
    ax.set_ylim(0,freq_max)
    ax.set_yticks(np.arange(0,freq_max,dfreq)+dfreq)

    match show_freqlabels:
        case True:
            ax.set_yticklabels(['']*np.uint(np.round(freq_max/dfreq,0)-1)+\
                               ['%.1f [%s]'%(freq_max,unit_freqs)])
        case 'all':
            freq_ticklabels = ['%.1f'%(freq) for freq in np.arange(0,freq_max,dfreq)+dfreq]
            freq_ticklabels[-1] += ' [%s]'%(unit_freqs)
            ax.set_yticklabels(freq_ticklabels)
        case False:
            ax.set_yticklabels(['']*np.uint(np.round(freq_max/dfreq,0)))

    ax.grid(linestyle='--',color='black',linewidth=0.5)

    return ax


def plot_bathymetry(depths, shp_dict, ax, cmap='Blues_r'):
    """Plots the bathymetry map for a given area.
    
    The function plots the bathymetry map for a given area using the shapefiles contained in the 
    dictionary `shp_dict`. The shapefiles are sorted by depth, from the surface to the bottom.

    Parameters
    ----------
    depths : list
        List of the depths in the shapefiles for the specified area.
    shp_dict : dict
        Dictionary containing the shapefiles.
    ax : matplotlib.axes
        Axes object to plot on.
    cmap : str, optional
        Colormap to use for the plot. Default is ``'Blues_r'``. 
        
        .. note::
            Other colormap options include ``'plasma'``, ``'inferno'``, ``'magma'``, ``'viridis'``. 
            Visit the `Matplotlib documentation 
            <https://matplotlib.org/stable/tutorials/colors/colormaps.html>`_ for an overview of 
            the options.
    
    Returns
    -------
    ax : matplotlib.axes._subplots.AxesSubplot
        The axes object with the plot.
    colormap : matplotlib.colors.ListedColormap
        The colormap used for the plot.

    See Also
    --------
    netsse.model.bathymetry.load_bathymetry : Retrieve and read bathymetry shapefiles.

    Example
    -------
    .. code-block:: python

        import matplotlib.pyplot as plt
        import cartopy.crs as ccrs
        import cartopy.feature as cfeature
        from netsse.model.bathymetry import load_bathymetry
        from netsse.tools.viz import plot_bathymetry

        depths, shp_dict = load_bathymetry(lonmin=-5, lonmax=15, latmin=35, latmax=45)
        fig, ax = plt.subplots(subplot_kw={'projection':ccrs.Mercator(central_longitude=5,min_latitude=35,max_latitude=45)},figsize=(6,6))
        ax.set_extent([-5, 15, 35, 45], crs=ccrs.PlateCarree())
        ax, colormap = plot_bathymetry(depths, shp_dict, ax)
        ax.add_feature(cfeature.LAND,edgecolor='black',facecolor='gainsboro',alpha=0.5)
    """

    # Construct a discrete colormap with colors corresponding to each depth
    depths_int = depths.astype(int)
    N = len(depths)
    nudge = 0.01  # shift bin edge slightly to include data
    boundaries = [min(depths_int)] + sorted(depths_int+nudge)  # low to high
    norm = matplotlib.colors.BoundaryNorm(boundaries, N)
    colormap = matplotlib.colormaps[cmap].resampled(N)
    colors_depths = colormap(norm(depths_int))

    # Iterate and plot bathymetry feature for each depth level
    for i, depth in enumerate(depths):
        ax.add_geometries(shp_dict[depth].geometries(),
                                crs=ccrs.PlateCarree(),
                                color=colors_depths[i])
    
    # Convert vector bathymetries to raster (saves a lot of disk space) while leaving labels as vectors:
    #ax.set_rasterized(True)

    return ax, colormap