# -*- coding: utf-8 -*-
"""
**Miscellaneous functions** for NetSSE.

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

*Last updated on 12-07-2024 by R.E.G. Mounet*

"""

import string
import random
import numpy as np
from scipy.interpolate import interp1d
from geopy import distance

def wrap(U,axis=1,add=0):
    """Wraps an array around one of its dimensions.

    Parameters
    ----------
    U : array_like of shape (n,m) or (n,)
        Input array to be wrapped around.
    axis : {1,0}, optional
        If ``U`` is a 2d-array, the axis of ``U`` along which to wrap.
        The default is ``1``.
    add : float or array_like, default 0
        Term that is added to the repeated part of ``U`` before
        concatenation. 

    Returns
    -------
    U_wrap : array_like
        Extended array, where the first column (respectively, row)
        of ``U`` has been repeated by concatenation at the end of ``U``.

        .. note::

            - If ``U`` is a 2d-array, then the output array has a shape of
              ``(n+1*(axis==0),m+1*(axis==1))``.
            - If ``U`` is a 1d-array, then the output array has a shape of
              ``(n+1,)``. The first element of ``U`` has been repeated at the
              end.

    See Also
    --------
    pad : Adds zeros to an array along one of its dimensions.

    Example
    -------
    >>> U_wrap = wrap(U,axis=1,add=0)
    """
    N = np.shape(U)
    if len(N)==1:
        U_wrap = np.concatenate([U,np.reshape(U[0]+add,1)])
    else:            
        n,m = np.shape(U)
        if axis == 1:
            U_wrap = np.concatenate([U,np.reshape(U[:,0]+add,[n,1])],axis=axis)
        elif axis == 0:
            U_wrap = np.concatenate([U,np.reshape(U[0,:]+add,[1,m])],axis=axis)
    return U_wrap


def pad(U,axis=1,add=0):
    """Adds zeros to an array along one of its dimensions.
    
    Parameters
    ----------
    U : array_like of shape (n,m) or (n,)
        Input array to be padded with zeros at the beginning.
    axis : {1,0}, optional
        If ``U`` is a 2d-array, the axis of ``U`` along which to pad. 
        The default is ``1``.
    add : float or array_like, default 0
        Term that is added to the concatenated zeros.    
    
    Returns
    -------
    U_pad : array_like
        Extended array, where ``U`` has been padded with a first column 
        (respectively, row) of zeros (plus an optional added term).

        .. note::

            - If ``U`` is a 2d-array, then the output array ``U_pad`` has a 
              new shape of ``(n+1*(axis==0),m+1*(axis==1))``.
            - If ``U`` is a 1d-array, then the output array ``U_pad`` has a 
              new shape of ``(n+1,)``. A zero element has been added at the 
              beginning.

    See Also
    --------
    wrap : Wraps an array around one of its dimensions.
    
    Example
    -------
    >>> U_wrap = pad(U,axis=1,add=0) 
    """
    N = np.shape(U)
    if len(N)==1:
        U_wrap = np.concatenate([np.reshape(0,1),U])
    else:            
        n,m = np.shape(U)
        if axis == 1:
            U_wrap = np.concatenate([np.zeros([n,1])+add,U],axis=axis)
        elif axis == 0:
            U_wrap = np.concatenate([np.zeros([1,m])+add,U],axis=axis)
    return U_wrap


def re_range(theta,start=0,unit='deg'):
    r"""Converts angles to a new range (of extent 360 degrees).

    Parameters
    ----------
    theta : array_like
        Array of angles to be rearranged.
    start : float, default 0
        Lower boundary of the range that should contain the new values of
        ``theta``. The upper boundary will be set automatically to 
        ``start + 360`` degrees.
    unit : {'deg','rad'}, optional
        Specifies the unit of ``theta`` and ``start`` as ``'rad'`` or 
        ``'deg'``. The default is ``'deg'``.

    Returns
    -------
    theta_rerange : array_like
        Array of angles where the elements of ``theta`` have been converted
        to the new range ``[start, start+360)`` degrees.

    See Also
    --------
    ang_diff : Calculates the signed difference between two angles.

    Example
    -------
    >>> theta_rerange = re_range(theta,start=0,unit='deg')
    """
    N = np.size(theta)
    angles = np.reshape(np.array(theta),(-1,))
    theta_rerange = []    
    
    if unit=='rad':
        for t in angles:
            t_new = t
            while not (t_new>=start and t_new<start+2*np.pi):
                t_new = (2*np.pi+t_new)*(t_new<start)+\
                            t_new*(t_new>=start and t_new<start+2*np.pi)+\
                                (t_new-2*np.pi)*(t_new>=start+2*np.pi)
            theta_rerange.append(t_new)            
    
    elif unit=='deg':
        for t in angles:
            t_new = t
            while not (t_new>=start and t_new<start+360):
                t_new = (360+t_new)*(t_new<start)+\
                            t_new*(t_new>=start and t_new<start+360)+\
                                (t_new-360)*(t_new>=start+360)
            theta_rerange.append(t_new)
            
    if N<2:
        theta_rerange = theta_rerange[0]
    else:
        theta_rerange = np.array(theta_rerange).reshape(np.shape(theta))
    
    return theta_rerange


def ang_diff(alpha, beta, unit='deg'):
    """Calculates the signed difference between two angles. 
    
    Parameters
    ----------
    alpha, beta : float or array_like
        Input angle as a scalar value or as an array of angles.
    unit : {'deg','rad'}, optional
        Specifies the unit of the angles as ``'rad'`` or 
        ``'deg'``. The default is ``'deg'``.

    Returns
    -------
    delta : float or array_like
        The output difference between alpha and beta in the range [-180,180] 
        degrees.

        .. note::
            This function subtracts ``alpha`` from ``beta``, i.e., 
            computes the signed difference ``beta-alpha``, taking into account
            the circularity at 360 degrees. 

    See Also
    --------
    re_range : Converts angles to a new range of values.
    ang_mean : Calculates the mean angle from an array of angular data.
    ang_std : Calculates the circular standard deviation for an array of 
        angular data.

    Example
    -------
    >>> delta = ang_diff(alpha, beta, unit='deg')
    """
    if unit=='deg':
        a = np.radians(alpha)
        b = np.radians(beta)
    elif unit=='rad':
        a = alpha
        b = beta
        
    delta = np.arctan2(np.sin(b-a),np.cos(b-a))
    if unit=='deg':
        delta = np.degrees(delta)
    return delta


def ang_mean(angles, unit='deg'):
    """Calculates the mean angle from an array of angular data.
    
    This function properly handles the circularity of angles at 360 
    degrees.

    Parameters
    ----------
    angles : array_like
        Array of angles.
    unit : {'deg','rad'}, optional
        Specifies the unit of the angles as ``'rad'`` or 
        ``'deg'``. The default is ``'deg'``.
    
    Returns
    -------
    mean_a : float
        Mean angle in the range [-180,180) degrees.

    See Also
    --------
    ang_diff : Calculates the signed difference between two angles.
    ang_std : Calculates the circular standard deviation of an array 
        of angular data.

    Example
    -------
    >>> mean_angle = ang_mean(angles, unit='deg')
    """
    if unit=='deg':
        a = np.radians(angles)
    elif unit=='rad':
        a = angles
    
    sin_a = np.sin(a)
    cos_a = np.cos(a)
    mean_a = np.arctan2(np.mean(sin_a),np.mean(cos_a))
    
    if unit=='deg':
        mean_a = np.degrees(mean_a)
    
    return mean_a


def ang_std(angles, unit='deg'):
    """Calculates the circular standard deviation of an array of 
    angular data.
    
    This function properly handles the circularity of angles at 360 
    degrees. The standard "two-pass" computation is implemented.        

    Parameters
    ----------
    angles : array_like
        Array of angles.
    unit : {'deg','rad'}, optional
        Specifies the unit of the angles as ``'rad'`` or 
        ``'deg'``. The default is ``'deg'``.
    
    Returns
    -------
    std_a : float
        Circular standard deviation.

    See Also
    --------
    ang_diff : Calculates the signed difference between two angles.
    ang_mean : Calculates the mean angle from an array of angular 
        data.

    Example
    -------
    >>> std_angle = ang_std(angles, unit='deg')
    """
    if unit=='deg':
        a = np.radians(angles)
    elif unit=='rad':
        a = angles
        
    mean_a = ang_mean(a,unit='rad')
    diff_a = ang_diff(mean_a,a,unit='rad')
    std_a = np.sqrt(np.mean(np.square(diff_a))-np.square(np.mean(diff_a)))
    
    if unit=='deg':
        std_a = np.degrees(std_a)
    
    return std_a


def areSame_vec(a,b):
    """Checks whether two vectors are identical, element-wise.
    
    Parameters
    ----------
    a, b : 1d-array
        Input vector.

    Returns
    -------
     : bool
        ``False`` for ``a!=b``, ``True`` for ``a=b``.

    .. note::
        If ``a`` and ``b`` do `not` have the same shape, then 
        ``False`` is returned. 
        
    See Also
    --------
    areSame_mat : Checks whether two matrices are identical, 
        element-wise.

    Example
    -------
    >>> areSame_vec(a,b)
    """
    n_a = len(a)
    n_b = len(b)
    
    if n_a != n_b:
        return False

    for i in range(n_a):
            if (a[i] != b[i]):
                return False

    return True


def areSame_mat(A,B):
    """Checks whether two matrices are identical, element-wise.

    Parameters
    ----------
    A, B : 2d-array
        Input matrix.
        
    Returns
    ------- 
     : bool 
        ``False`` for ``A!=B``, ``True`` for ``A=B``. 

    .. note::
        If ``A`` and ``B`` do `not` have the same shape, then 
        ``False`` is returned.

    See Also
    --------
    areSame_vec : Checks whether two vectors are identical, 
        element-wise.
    
    Example
    -------
    >>> areSame_mat(A,B)
    """
    # print(np.shape(A))
    nr_A, nc_A = np.shape(A)
    nr_B, nc_B = np.shape(B)
    
    if nr_A != nr_B or nc_A != nc_B:
        return False

    for i in range(nr_A):
        for j in range(nr_B):
            if (A[i][j] != B[i][j]):
                return False

    return True


def weighted_std(a,w,axis=None,ddof=1):
    """Computes the weighted standard deviation of some data.
    
    The weighted standard deviation is a measure of the spread of a 
    distribution of the array elements from the mean, where some of the 
    elements are more significant than others. The weighted standard deviation
    is calculated based on the weighted mean and it attaches more importance to 
    data that have more weight than to data with less weight 
    (National Institute of Standards and Technology, 1996).

    Parameters
    ----------
    a : array_like
        Variable for which the weighted std. must be computed.
    w : array_like
        Array of weights. All elements must be positive.
        The array ``w`` must broadcastable with the array ``a``.
    axis : None or int, optional
        Axis or axes along which the standard deviation is computed. 
        The default is to compute the weighted standard deviation of the
        flattened array.
    ddof : int, default 0
        Delta Degrees of Freedom. The divisor used in the calculations is 
        ``(N_nz - ddof)/N_nz``, where ``N_nz`` represents the number of
        non-zero weights.

    Returns
    -------
    std : array_like
        Weighted standard deviation of the data.

    See Also
    --------
    weighted_quantile : Computes the `q`-th quantiles of weighted data.

    References
    ----------
    National Institute of Standards and Technology, 1996. Formula for the 
    weighted standard deviation. Available at: 
    https://www.itl.nist.gov/div898/software/dataplot/refman2/ch2/weightsd.pdf
    (Consulted on 06-08-2023).

    Example
    -------
    >>> std = weighted_std(a,w,axis=None,ddof=1)
    """
    
    # Weighted mean of the samples:
    a_avg = np.average(a,weights=np.squeeze(w),axis=axis)
    
    # Squared deviations from the mean:
    x = np.square(np.abs(np.subtract(a,a_avg)))
    
    # Compute numerator:
    num = np.sum(np.multiply(w,x),axis=axis)
    
    # Number of non-zero weights
    N_nz = len(np.flatnonzero(w))
    
    # Compute denominator:
    denom = (N_nz-ddof)/N_nz*np.sum(w)
    std = np.sqrt(np.divide(num,denom))
    
    return std


def weighted_quantile(x,q,w,a=0.5,b=0.5,axis=-1):
    """Computes the `q`-th quantiles of weighted data.
    
    The quantiles are computed along one of the axes of the input array 
    ``x``.

    Parameters
    ----------
    x : array_like
        Input data array for which the quantiles must be computed.
    q : 1d-array of shape (Nq,)
        Sequence of quantiles to compute, which must be between 0 and 1.
    w : array_like
        Array of weights. The arrays ``x`` and ``w`` must be broadcastable. 
    a,b : floats, default 0.5
        User-defined constant used in the computation of the quantiles. 
        The default is 0.5 to minimize biases (Rogers, 2003).
    axis : integer, default -1
        Axis of ``x`` along which the ``q``-quantiles are computed. 

    Returns
    -------
    v : array_like
        Values of the ``q``-quantiles computed along the specified ``axis`` 
        of the input array ``x`` with weights ``w``.

    See Also
    --------
    weighted_std : Computes the weighted standard deviation of some 
        data.

    References
    ----------
    Rogers, J.W., 2003. Estimating the variance of percentiles using replicate 
    weights, in: Proc. of the Joint Statistical Meetings, Survey Research
    Methods Section, American Statistical Association. pp. 3525–3532. 
    URL: http://www.asasrms.org/Proceedings/y2003/Files/JSM2003-000742.pdf

    Example
    -------
    >>> v = weighted_quantile(x, q, w, a=0.5, b=0.5, axis=-1)
    """
    N = np.shape(x)[axis]
    Nq = len(q)
    index_sorted = np.argsort(x,axis=axis)
    x_k = np.take_along_axis(x,index_sorted,axis=axis)
    w_k = np.take_along_axis(w,index_sorted,axis=axis)
    
    # Re-arrange the arrays to facilitate the linear interpolation:
    w_k_new = np.reshape(np.moveaxis(w_k,axis,0),(N,-1))
    x_k_new = np.moveaxis(x_k,axis,0)
    v_shape = (Nq,)+np.shape(x_k_new)[1:]
    x_k_new = np.reshape(x_k_new,(N,-1))
    M = np.shape(x_k_new)[1]

    S_k = np.cumsum(w_k_new,axis=0)
    S_N = S_k[-1:,:]
    p_k_new = (S_k-a*w_k_new)/(S_N+(1-a-b)*w_k_new)
    
    # Linear interpolation at the requested quantiles q:
    v_new = np.zeros((Nq,M))
    for i in range(M):
        f_v = interp1d(p_k_new[:,i],x_k_new[:,i],kind='linear',axis=0,\
                       assume_sorted=True)
        v_new[:,i] = f_v(q)
    v = np.reshape(v_new,v_shape)
    v = np.moveaxis(v,0,axis)
    
    return v


def find_nearest_gridpoint(lat_wps,lon_wps,lat_grid,lon_grid,interv=0.01):  
    """Finds the nearest neighbours to a series of waypoints within a grid 
    of points.

    .. note::
        The grid points do `not` need to be uniformly spaced in any direction.
        The grid can also have been rotated of any angle about the 
        vertical direction (e.g., to be aligned with some shoreline).

    For a given waypoint at ``(lat_wp,lon_wp)``, the nearest-neighbour 
    candidates are first selected within the gridpoints that fall in the 
    geographical area delimited by ``lat_wp*[1-interv,1+interv]`` in latitude 
    and ``lon_wp*[1-interv,1+interv]`` in longitude. Then, the distance between
    the waypoint and the nearest-neighbour candidates is computed. The output 
    neighbour is found as the candidate that minimises this distance.

    Parameters
    ----------
    lat_wps : float, or 1d-array of shape (Nwp,)
        Vector of waypoint latitudes [deg].
    lon_wps : float, or 1d-array of shape (Nwp,)
        Vector of waypoint longitudes [deg].
    lat_grid : 2d-array
        Matrix defining the latitudes of the grid points [deg].
    lon_grid : 2d-array
        Matrix defining the longitudes of the grid points [deg].
    interv : float, default 0.01
        Half-width [-] of the interval band fraction in latitude and longitude, 
        used for screening the potential nearest-neighbour candidates.

    Returns
    -------
    index_nearest : numpy.array of shape (Nwp,2)
        The coordinates in `(latitude,longitude)` of the nearest gridpoints
        to the waypoints [deg].
    dist_nearest : numpy.array of shape (Nwp,)
        The distance between the nearest gridpoints and the waypoints [km].

    Example
    -------
    >>> index_nearest, dist_nearest = 
    ...     find_nearest_gridpoint(lat_wps, lon_wps, lat_grid, lon_grid, interv=0.01)
    """
    
    lat_wps = np.reshape(lat_wps,(-1,))
    lon_wps = np.reshape(lon_wps,(-1,))
    
    Nwp = np.size(lat_wps)
    dist_nearest = np.zeros((Nwp,))
    index_nearest = np.zeros((Nwp,2))
    
    for i_wp in range(Nwp):
        
        lat_wp = lat_wps[i_wp,]
        lon_wp = lon_wps[i_wp,]
        
        lat_interv = np.abs(lat_wp)*interv
        lon_interv = np.abs(lon_wp)*interv
        
        indices_near = np.where((lat_grid > lat_wp-lat_interv)*(lat_grid < lat_wp+lat_interv)*\
                       (lon_grid > lon_wp-lon_interv)*(lon_grid < lon_wp+lon_interv))
        
        Nnear = len(indices_near[0])
        dist2grid = np.zeros((Nnear,))
        
        
        for i_index in range(Nnear):
            index = (indices_near[0][i_index,],indices_near[1][i_index,])
            
            dist2grid[i_index,] = distance.distance((lat_wp,lon_wp),\
                                  (lat_grid[index],lon_grid[index])).km
                
        i_mindist = np.argmin(dist2grid)
        dist_nearest[i_wp,] = dist2grid[i_mindist,]
        index_nearest[i_wp,:] = [indices_near[0][i_mindist,],\
                                 indices_near[1][i_mindist,]]
        
    return index_nearest, dist_nearest


def id_generator(size=6,chars=string.ascii_uppercase+string.digits):
    """
    Randomly generates a cryptographically secure string of a given size.

    Parameters
    ----------
    size : int, default 6
        String size
    chars : str, default 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        List of allowed characters

    Returns
    -------
    str
        Output random string

    Example
    -------
    >>> id_generator(size=6, chars=string.ascii_uppercase+string.digits)
    """
    return ''.join(random.choice(chars) for _ in range(size))