# -*- coding: utf-8 -*-
"""
Functions to compute sea state parameters from **wave spectra**.

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

*Last updated on 11-07-2024 by R.E.G. Mounet*

"""

import numpy as np
from scipy.integrate import trapezoid
import matplotlib.pyplot as plt
from netsse.tools.misc_func import re_range

def spec1d_to_params(S,freq,unit_freq='rad/s',smooth_Tp=False):
    """Computes the main sea state parameters from a given 1-D wave spectrum.

    Parameters
    ----------
    S : array_like
        1-D wave spectrum. If ``S`` has more than one dimension, then one axis must
        have a length Nfreq.
    freq : array_like of shape (Nfreq,)
        Set of discretized frequencies.
    unit_freq : {'rad/s','Hz'}, optional
        Unit of the frequencies:
        
        - 'rad/s' :
            The variable ``freq`` denotes the circular frequencies in radians per second. 
        - 'Hz' :
            The 1-D wave spectrum is expressed as a function of frequency in Hertz.
    smooth_Tp : bool, default False
        Specify whether the output ``Tp`` value should be smoothened by fitting
        a polynomial of order 3 in the vicinity of the spectral peak and 
        estimating the peak period through the fitted polynomial.

    Returns
    -------
    m : array_like of shape (6,...,)
        Spectral moments :math:`[m_{-1},m_0,m_1,m_2,m_3,m_4]`.
    Hm0 : float, or array_like
        Spectral significant wave height [m].
    Tp : float, or array_like
        Peak wave period [s].
    Tm01 : float, or array_like
        Mean wave period [s].
    Tm02 : float, or array_like
        Zero up-crossing period [s].
    Tm24 : float, or array_like
        Mean crest period [s].
    TE : float, or array_like
        Mean energy period [s].
    Sm02 : float, or array_like
        Significant wave steepness [-].
    epsilon : float, or array_like
        Spectral bandwidth [-].
    Qp : float, or array_like
        Goda's peakedness parameter [-].

    See Also
    --------
    spec2d_to_params : Computes a set of overall parameters characterizing the sea 
        state from the 2-D wave spectrum.

    Example
    -------
    >>> m, Hm0, Tp, Tm01, Tm02, Tm24, TE, Sm02, epsilon, Qp =
    ...     spec1d_to_params(S,freq,unit_freq='rad/s',smooth_Tp=False)
    """
    if unit_freq=='rad/s':
        f = freq/(2*np.pi)
        Sf = S*2*np.pi
    elif unit_freq=='Hz':
        f = freq
        Sf = S        
    
    f = np.reshape(f,(-1,))
    Nf = len(f)
    nDim_Sf = np.ndim(Sf)
    
    if nDim_Sf>=1:
        for dim in range(1,nDim_Sf):
            f = np.expand_dims(f,dim)
        shape_spec = np.shape(S)
        freq_axis = np.where(np.array(shape_spec)==Nf)[0][0]
        Sf = np.moveaxis(Sf,freq_axis,0)
        shape_moments = np.shape(Sf)[1:]
        m = np.zeros((6,)+shape_moments)
    else:
        m = np.zeros((6,))
    
    ####
    ## Moments of the variance spectral density [m-1,m0,m1,m2,m3,m4]
    ####    
    
    m[0,] = trapezoid(f[1:,]**(-1)*Sf[1:,],f[1:,],axis=0)
    for i in range(1,6):
        m[i,] = trapezoid(f**(i-1)*Sf,f,axis=0)
    
    ####
    ## Sea state parameters, derived from the spectrum
    ####
    
    g = 9.81                          # Gravitational acceleration [m/s^2]
    Hm0 = 4*np.sqrt(m[1,])            # Spectral significant wave height [m]
    Tm02 = np.sqrt(m[1,]/m[3,])                # Zero up-crossing period [s]
    Tm01 = m[1,]/m[2,]                         # Mean wave period [s]
    Tm24 = np.sqrt(m[3,]/m[5,])                # Mean crest period [s]
    TE = m[0]/m[1]                             # Mean energy period [s]
    Sm02 = 2*np.pi/g*Hm0/Tm02**2               # Significant wave steepness [-]
    epsilon = np.sqrt(1-m[3,]**2/(m[1,]*m[5])) # Spectral bandwidth [-]
    
    ####
    ## Goda's peakedness parameter [-]
    ####
    
    Qp = 2/m[1,]**2*trapezoid(f*Sf**2,f,axis=0)
    
    ####
    ## Peak period [s]
    ####
            
    I = np.argmax(Sf,axis=0,keepdims=True)
    f = np.reshape(f,(-1,))
    
    if smooth_Tp==False:
        # Basic method:
        Tp = 1/np.squeeze(f[I,])
        
    elif smooth_Tp==True:    
        # More elaborate method: fit a polynomial of order 3 in the vicinity 
        # of the peak (increases the accuracy of Tp):
        I = np.squeeze(I)
        Tp = np.where((I<2)+(I>Nf-3),float('nan'),0)
        shape_Tp = np.shape(Tp)
        Sf_reshaped = np.squeeze(np.moveaxis(Sf,0,-1))

        for ii, I_val in enumerate(np.nditer(I)):
            indices_ii = np.unravel_index(ii, shape_Tp)
            if ~np.isnan(Tp[indices_ii]):
                x = f[I_val-2:I_val+3,]
                y = Sf_reshaped[indices_ii][I_val-2:I_val+3,]
                z = np.polyfit(x,y,3)
                x1 = np.linspace(f[I_val-2,],f[I_val+2,],100)
                p = np.poly1d(z)
                y1 = p(x1)
                I1 = np.argmax(y1)
                Tp[indices_ii] += 1/x1[I1,]
        
                # Plot of the polynomial fit, compared with the true values 
                # at the peak:
                # plt.figure()
                # plt.plot(x1,y1)
                # plt.plot(x,y,marker='+')
                # plt.show()
            
    return m,Hm0,Tp,Tm01,Tm02,Tm24,TE,Sm02,epsilon,Qp


def spec2d_to_params(S2D,freq,theta,unit_theta='deg',smooth_peak=False):
    """Computes a set of overall parameters characterizing the sea state from the 
    2-D wave spectrum.

    Parameters
    ----------
    S2D : array_like of shape (...,Nf,Ntheta,...)
        Directional wave spectrum [m^2.s/``unit_theta``], as a function of frequency 
        in Hertz and wave direction in specified unit (``unit_theta``).
    freq : array_like of shape (Nf,)
        Vector of (discretized) wave frequencies [Hz] (must include :math:`f =` 0 Hz).
    theta : array_like of shape (Ntheta,)
        Vector of wave headings [the unit is specified in ``unit_theta``].

        .. attention::
            ``theta`` must be in a wrapped format, i.e., corresponding to [0,360] deg.
    unit_theta : {'deg','rad'}, optional
        Unit of the wave directions. This applies for the expression of the wave 
        spectrum too. Can be ``'deg'`` (for degrees), or ``'rad'`` (for radians). 
        ``'deg'`` is the default.
    smooth_peak : bool, optional
        Specify whether the output ``Tp`` and ``theta_p`` values should be smoothened by 
        fitting a polynomial of order 3 in the vicinity of the spectral peak and 
        estimating the peak period and direction through the fitted polynomial.
        The default is ``False``.

    Returns
    -------
    m : array_like of shape (6,)
        Spectral moments :math:`[m_{-1},m_0,m_1,m_2,m_3,m_4]`.
    Hm0 : float, or array_like
        Spectral significant wave height [m].
    Tp : float, or array_like
        Peak wave period [s].
    Tm01 : float, or array_like
        Mean wave period [s].
    Tm02 : float, or array_like
        Zero up-crossing period [s].
    Tm24 : float, or array_like
        Mean crest period [s].
    TE : float, or array_like
        Mean energy period [s].
    Sm02 : float, or array_like
        Significant wave steepness [-].
    epsilon : float, or array_like
        Spectral bandwidth [-].
    Qp : float, or array_like
        Goda's peakedness parameter [-].
    theta_p : float, or array_like
        Peak wave direction [deg].
    theta_m : float, or array_like
        Mean overall wave direction [deg].
    sigma_m : float, or array_like
        Mean directional spreading [deg].

    See Also
    --------
    spec1d_to_params : Computes the main sea state parameters from a given 1-D 
        wave spectrum.

    Example
    -------
    >>> m, Hm0, Tp, Tm01, Tm02, Tm24, TE, Sm02, epsilon, Qp, theta_p, theta_m, sigma_m = 
    ...     spec2d_to_params(S2D,freq,theta,unit_theta='deg',smooth_Tp=False)
    """
    # Physical constants:
    g = 9.81 # Gravitational acceleration [m/s^2]
    
    # Dimensions:
    nDim_S2D = np.ndim(S2D)
    Nf = len(freq)
    Nmu = len(theta)
    shape_spec2D = np.array(np.shape(S2D))
    f_axis = np.where(shape_spec2D==Nf)[0][0]
    mu_axis = np.where(shape_spec2D==Nmu)[0][0]

    if nDim_S2D>=3:
        spec2D = np.moveaxis(S2D,[f_axis,mu_axis],[0,1])
        f = np.reshape(freq,(Nf,1)+tuple([1]*(nDim_S2D-2)))
        mu = np.reshape(theta,(1,Nmu)+tuple([1]*(nDim_S2D-2)))
        shape_moments = np.shape(spec2D)[2:]
        m = np.zeros((6,)+shape_moments)
    else:
        spec2D = S2D
        f = np.reshape(freq,(Nf,1))
        mu = np.reshape(theta,(1,Nmu))
        shape_moments = []
        m = np.zeros((6,))        

    # Units:
    if unit_theta == 'deg':
        theta_deg = theta
        # theta_rad = theta*np.pi/180
        mu_rad = mu*np.pi/180
        spec2D *= 180/np.pi
    elif unit_theta == 'rad':
        theta_deg = theta*180/np.pi
        # theta_rad = theta
        mu_rad = mu
        
    Sf = np.expand_dims(trapezoid(spec2D,mu_rad,axis=1),1)

    # Moments of the variance spectral density [m-1,m0,m1,m2,m3,m4]:
    m[0,] = np.squeeze(trapezoid(f**(-1)*Sf,f,axis=0))
    for i in range(1,6):
        m[i,] = np.squeeze(trapezoid(f**(i-1)*Sf,f,axis=0))

    # Directional spreading function
    D = spec2D/Sf
    D[np.isnan(D)] = 0

    # Fourier coefficients (frequency-dependent):
    a1 = trapezoid(D*np.cos(mu_rad),mu_rad,axis=1)
    b1 = trapezoid(D*np.sin(mu_rad),mu_rad,axis=1)
    #print(a1); print(b1)
    
    # Sea state parameters, derived from the spectrum:
    Hm0 = 4*np.sqrt(m[1,])            # Spectral significant wave height [m]
    Tm02 = np.sqrt(m[1,]/m[3,])                # Zero up-crossing period [s]
    Tm01 = m[1,]/m[2,]                         # Mean wave period [s]
    Tm24 = np.sqrt(m[3,]/m[5,])                # Mean crest period [s]
    TE = m[0]/m[1]                             # Mean energy period [s]
    Sm02 = 2*np.pi/g*Hm0/Tm02**2               # Significant wave steepness [-]
    epsilon = np.sqrt(1-m[3,]**2/(m[1,]*m[5])) # Spectral bandwidth [-]

    # Goda's peakedness parameter [-]:    
    Qp = 2/m[1,]**2*np.squeeze(trapezoid(f*Sf**2,f,axis=0))
    
    # Peak period [s] and peak direction [deg]:
    I = np.argmax(Sf,axis=0,keepdims=True)
    J = np.argmax(spec2D,axis=1,keepdims=True)
    K = np.take_along_axis(J,I,axis=0)
    # Important note: The peak direction is defined here as the direction of 
    # maximum PSD in the 2-D wave spectrum at the peak frequency (computed 
    # from the 1-D spectrum)
    
    if smooth_peak==False:
        # Basic method:
        Tp = 1/np.squeeze(freq[I,])
        theta_p = np.squeeze(theta_deg[K,])
        
    elif smooth_peak==True:    
        # More elaborate method: fit a polynomial of order 3 in the vicinity 
        # of the peak (increases the accuracy of Tp and theta_p):
        theta_deg_wrap = np.concatenate((theta_deg[-3:-1,]-360,theta_deg,theta_deg[1:3,]+360),axis=0)
        K = np.squeeze(K+2)
        shape_thetap = np.shape(K)
        theta_p = np.zeros(shape_thetap)
        Stheta = np.take_along_axis(spec2D,I,axis=0)
        Stheta_wrap = np.squeeze(np.moveaxis(np.concatenate((Stheta[:,-3:-1],Stheta,Stheta[:,1:3]),axis=1),1,-1))

        I = np.squeeze(I)
        Tp = np.where((I<2)+(I>Nf-3),float('nan'),0)
        shape_Tp = np.shape(Tp)
        Sf_reshaped = np.squeeze(np.moveaxis(Sf,0,-1))

        for ii, I_val in enumerate(np.nditer(I)):
            indices_ii = np.unravel_index(ii, shape_Tp)
            if ~np.isnan(Tp[indices_ii]):
                x = freq[I_val-2:I_val+3,]
                y = Sf_reshaped[indices_ii][I_val-2:I_val+3,]
                z = np.polyfit(x,y,3)
                x1 = np.linspace(freq[I_val-2,],freq[I_val+2,],100)
                p = np.poly1d(z)
                y1 = p(x1)
                I1 = np.argmax(y1)
                Tp[indices_ii] += 1/x1[I1,]
        
                # Plot of the polynomial fit, compared with the true values 
                # at the peak:
                # plt.figure()
                # plt.plot(x1,y1)
                # plt.plot(x,y,marker='+')
                # plt.show()
        
        for kk, K_val in enumerate(np.nditer(K)):
            indices_kk = np.unravel_index(kk, shape_thetap)
            x = theta_deg_wrap[K_val-2:K_val+3,]
            y = Stheta_wrap[indices_kk][K_val-2:K_val+3,]
            z = np.polyfit(x,y,3)
            x1 = np.linspace(theta_deg_wrap[K_val-2,],theta_deg_wrap[K_val+2,],100)
            p = np.poly1d(z)
            y1 = p(x1)
            K1 = np.argmax(y1)
            theta_p[indices_kk] += x1[K1,]

            # Plot of the polynomial fit, compared with the true values 
            # at the peak:
            # plt.figure()
            # plt.plot(x1,y1)
            # plt.plot(x,y,marker='+')
            # plt.show()

    theta_p = re_range(theta_p)
    
    # Frequency-dependent mean wave direction [deg] and directional spreading 
    # factor [rad]:
    # theta1 = np.arctan2(b1,a1)*180/np.pi
    # s = np.sqrt(a1**2+b1**2)/(1-np.sqrt(a1**2+b1**2))
    
    # Mean overall wave direction [deg]:
    d = trapezoid(trapezoid(spec2D*np.sin(mu_rad),f,axis=0),mu_rad[0,],axis=0)
    c = trapezoid(trapezoid(spec2D*np.cos(mu_rad),f,axis=0),mu_rad[0,],axis=0)
    theta_m = np.reshape(re_range(np.reshape(np.arctan2(d,c)*180/np.pi,(-1,))),
                         shape_moments)
    
    # First-order spreading coefficient [rad] (as per Saulnier et al. 2012)
    sigma1 = np.expand_dims(np.sqrt(2*(1-np.sqrt(a1**2+b1**2))),1)
    
    # Mean directional spreading [deg]:
    d_s = trapezoid(trapezoid(spec2D*np.sin(sigma1),f,axis=0),mu_rad[0,],axis=0)
    c_s = trapezoid(trapezoid(spec2D*np.cos(sigma1),f,axis=0),mu_rad[0,],axis=0)
    sigma_m = np.arctan2(d_s,c_s)*180/np.pi
    
    return m,Hm0,Tp,Tm01,Tm02,Tm24,TE,Sm02,epsilon,Qp,theta_p,theta_m,sigma_m


def spread_dist_to_spec2d(Sf,D,theta):
    """Converts the given 1-D wave spectrum and directional spreading function
    into a 2-D wave spectrum.
    
    Parameters
    ----------
    Sf : array_like of shape (...,Nf,...)
        One-sided variance spectrum of the waves, as a function of 
        frequency.
    D : array_like of shape (...,Nf,Ntheta,...)
        Directional spreading function.
    theta : array_like of shape (Ntheta,)
        Vector of wave headings (with arbitrary unit).

    Returns
    -------
    S2D : array_like of shape (...,Nf,Ntheta,...)
        Directional wave spectrum, as a function of frequency 
        and wave direction (with arbitrary units).

    See Also
    --------
    spec2d_to_spread_dist : Converts the given 2-D wave spectrum 
        into a directional spreading function and a 1-D wave spectrum.
        
    Example
    -------
    >>> S2D = spread_dist_to_spec2d(Sf,D,theta)
    """    
    # Dimensions:
    Nmu = len(theta)
    shape_spec2D = np.array(np.shape(D))
    mu_axis = np.where(shape_spec2D==Nmu)[0][0]

    # Directional wave spectrum:
    D[np.isnan(D)] = 0
    S2D = np.expand_dims(Sf,mu_axis)*D
    
    return S2D


def spec2d_to_spread_dist(S2D,theta):
    """Converts the given 2-D wave spectrum into a directional spreading function
    and a 1-D wave spectrum.
    
    Parameters
    ----------
    S2D : array_like of shape (...,Nf,Ntheta,...)
        Directional wave spectrum, as a function of frequency and wave 
        direction (with arbitrary units).
    theta : array_like of shape (Ntheta,)
        Vector of wave headings (with arbitrary unit).

    Returns
    -------
    Sf : array_like of shape (...,Nf,...)
        One-sided variance spectrum of the waves, as a function of frequency.
    D : array_like of shape (...,Nf,Ntheta,...)
        Directional spreading function.

    See Also
    --------
    spread_dist_to_spec2d : Converts the given 1-D wave spectrum and directional
        spreading function into a 2-D wave spectrum.

    Example
    -------
    >>> Sf, D = spec2d_to_spread_dist(S2D,theta)
    """
    # Dimensions:
    Ntheta = len(theta)
    shape_spec2D = np.array(np.shape(S2D))
    theta_axis = np.where(shape_spec2D==Ntheta)[0][0]

    # 1-D wave spectrum:
    Sf = np.expand_dims(trapezoid(S2D,theta,axis=theta_axis),theta_axis)

    # Directional spreading function
    D = S2D/Sf
    D[np.isnan(D)] = 0
    
    Sf = np.squeeze(Sf)

    return Sf, D