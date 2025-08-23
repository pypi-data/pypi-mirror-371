# -*- coding: utf-8 -*-
"""
Relevant functions for **environmental conditions**.

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

import numpy as np
from math import gamma
from scipy.integrate import trapezoid

def JONSWAP_DNV(Tp,Hs,omega,gamma='standard',h=0):
    """Computes the JONSWAP spectrum corresponding to the input sea state 
    parameters.

    The JONSWAP spectrum is formulated as a modification of
    a Pierson-Moskowitz spectrum for a developing sea state in a fetch
    limited situation.

    Parameters
    ----------    
    Tp : float
        Peak period [s].
    Hs : float
        Significant wave height [m].
    omega : array_like of shape (Nfreq,)
        Vector of angular frequencies [rad/s].
    gamma : {'standard','DNV',float}, optional
        Peak shape parameter [-]. The value can be user-provided as a float. 
        Alternatively, if ``'standard'`` is input, then ``gamma`` will take the 
        standard value of 3.3., while a value ``'DNV'`` as input leads to 
        following the procedure 3.5.5.5 described in DNV-RP-C205.

        .. tip::
            Use ``gamma = 1`` to output a standard Pierson-Moskowitz spectrum.
    h : float, default 0
        Water depth [m]. If ``h`` is specified as input argument, then the output
        JONSWAP spectrum is corrected to account for finite water depth, becoming
        a standard TMA spectrum as per Bouws et al. (1985).

    Returns
    -------
    S_J : array_like of shape (Nfreq,)
        Standard wave spectrum [m^2.s/rad].
    
    References
    ----------
    1. DNV-RP-C205, "Environmental Conditions and Environmental Loads, 
       April 2007.
    2. Bouws, E., Gunther, H., Rosenthal, W., & Vincent, C. L. (1985). 
       *Similarity of the wind wave spectrum in finite depth water. 1. Spectral form*. 
       Journal of Geophysical Research-Oceans, 90(NC1), 975–986. 
       https://doi.org/10.1029/JC090iC01p00975

    See Also
    --------
    lin_disprel : A fast and accurate approximation of the linear wave dispersion 
        relationship in finite water depth.

    Example
    -------
    >>> S_J = JONSWAP_DNV(Tp,Hs,omega,gamma='standard',h=0) 
    """
    g = 9.81
    omega_p = 2*np.pi/Tp # angular spectral peak frequency [rad/s]
    omega = np.array(omega)
    
    # Pierson-Moskowitz spectrum:
    S_PM = (5/16*Hs**2*omega_p**4)*omega**(-5)*np.exp(-5/4*(omega/omega_p)**(-4))
    
    # JONSWAP spectrum:
    crit = Tp/np.sqrt(Hs)
    
    if gamma == 'standard':
        gamma = 3.3    
    elif gamma == 'DNV':
        if crit<=3.6:
            gamma = 5
            print('JONSWAP spectrum should be used with caution for the given (Tp,Hs)')
        elif crit>=5:
            gamma = 1
            print('JONSWAP spectrum should be used with caution for the given (Tp,Hs)')
        else:
            gamma = np.exp(5.75-1.15*crit)
    
    print('JONSWAP spectrum with gamma =',gamma)
    
    A_gamma = 1-0.287*np.log(gamma);
    sigma_a = 0.07; sigma_b = 0.09
    sigma = sigma_a*np.ones(np.shape(omega))  #spectral width parameter [n.d.]
    sigma[np.where(omega>omega_p)] = sigma_b
    S_J = A_gamma*S_PM*gamma**(np.exp(-0.5*((omega-omega_p)/(sigma*omega_p))**2))
    
    if h > 0: #case of finite water depth
        k0 = lin_disprel(omega,h)
        phi = np.cosh(h*k0)**2/(np.sinh(h*k0)**2+h/g*omega**2)
        S_J = S_J*phi # Finite water depth TMA spectrum

    return S_J


def lin_disprel(omega,h):
    """Computes the wavenumbers from wave angular frequencies in finite water depth.

    This function implements a fast and accurate approximation of the linear wave 
    dispersion relationship in finite water depth.

    Parameters
    ----------
    omega : array_like or float
        Wave angular frequencies [rad/s].
    h : float
        Mean water depth [m]

    Returns
    -------
    k : array_like or float
        Wavenumbers [1/m]

    Example
    -------
    >>> k = lin_disprel(omega,h)
    """
    g = 9.81
    T = 2*np.pi/omega
    omega_bar = (4*np.pi**2*h)/(g*T**2)
    f = 1 + np.sum(np.array([0.666,0.445,-0.105,0.272]).reshape((1,4))*\
                   np.reshape(omega_bar,(-1,1))**(np.arange(1,5).reshape((1,4))),axis=1)
    lamb = np.sqrt(g*h)*T*np.sqrt(f/(1+omega_bar*f))
    k = 2*np.pi/lamb

    return k


def wavespec1dto2d(S1d,theta,theta0,s):
    """Transforms a 1-D wave spectrum into a 2-D wave spectrum.

    A cosine-2s function is used for the directional spreading distribution.

    Parameters
    ----------
    S1d : array_like of shape (Nfreq,)
        1-D wave spectrum.
    theta : array_like of shape (Ntheta,)
        Vector of wave headings [deg] at which the 2-D spectrum must be computed.
    theta0 : float
        Mean wave direction [deg].
    s : float
        Spreading parameter [-], related to the exponent of the cosine function.

    Returns
    -------
    S2d : array_like of shape (Nfreq,Ntheta)
        2-D wave spectrum, as a function of both the frequency and the wave 
        heading [deg].
    D_theta : array_like of shape (1,Ntheta)
        Directional spreading function, as a function of the wave heading [deg].
        
    References
    ----------
    Naess, Arvid, and Torgeir Moan. 2010. Stochastic Dynamics of 
    Marine Structures. Stochastic Dynamics of Marine Structures. Vol. 
    9780521881555. Cambridge University Press. 
    https://doi.org/10.1017/CBO9781139021364.

    Example
    -------
    >>> S2d = wavespec1dto2d(S1d,theta,theta0,s)
    """
    C = 2**(2*s-1)/np.pi*(gamma(s+1))**2/gamma(2*s+1) # Normalizing constant
    D_theta = np.reshape(C*np.cos(np.radians(theta-theta0)/2)**(2*s),(1,-1))
    
    S2d = np.reshape(S1d,(-1,1))*np.ones((len(S1d),len(theta)))
    S2d = D_theta*S2d
       
    return S2d, D_theta