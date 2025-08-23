# -*- coding: utf-8 -*-
"""
Functions to **process wave buoy** motion signals into directional wave 
spectra.

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
from netsse.tools.misc_func import *

def cross_spec2Fourier_coef(Gf):
    """Computes the Fourier coefficients from the cross-spectra of a 
    heave-East-North wave buoy, as per Benoit et al. (1997).

    Parameters
    ----------
    Gf : array_like of shape (3,3,Nf)
        Cross-spectra (Heave-East-North), as a function of frequency in Hertz.

    Returns
    -------
    Sf : array_like of shape (Nf,)
        One-sided variance spectrum of the waves [m^2.s], as a function of 
        frequency in Hertz.
    a1, a2, b1, b2 : array_like of shape (Nf,)
        Frequency-dependent Fourier coefficients of the directional wave 
        spectrum.

    See Also
    --------
    Shannon_MEMII_Newton : Reconstructs the directional spreading function 
        based on the first four Fourier coefficients of a directional wave spectrum.
          
    References
    ----------
    Benoit, M., Frigaard, P., & Schäffer, H. A. (1997). *Analysing Multidirectional 
    Wave Spectra: A tentative classification of available methods*. Proceedings of 
    the 27th IAHR Congress, San Francisco, CA, USA (pp. 131–158). Canadian 
    Government Publishing.

    Example
    -------
    >>> Sf, a1, a2, b1, b2 = cross_spec2Fourier_coef(Gf)
    """
    C, Q = np.zeros(np.shape(Gf)), np.zeros(np.shape(Gf))
    
    for m in range(3):
        for n in range(3):
            C[m,n,:] = np.real(Gf[m,n,:]) # coïncident spectral density function, co-spectrum
            Q[m,n,:] = np.imag(Gf[m,n,:]) # quadrature spectral density function, quad-spectrum
    
    Sf = np.squeeze(C[0,0,:]).reshape((-1,1))      # 1-D wave spectrum [m^2.s]
    
    # Fourier coefficients, as a function of frequency in Hertz:
    a1 = -Q[0,1,:]/np.sqrt(C[0,0,:]*(C[1,1,:]+C[2,2,:]))
    b1 = -Q[0,2,:]/np.sqrt(C[0,0,:]*(C[1,1,:]+C[2,2,:]))
    a2 = (C[1,1,:]-C[2,2,:])/(C[1,1,:]+C[2,2,:])
    b2 = 2*C[1,2,:]/(C[1,1,:]+C[2,2,:])
    
    # Test:
    # b1 = -Q[0,1,:]/np.sqrt(C[0,0,:]*(C[1,1,:]+C[2,2,:]))
    # a1 = -Q[0,2,:]/np.sqrt(C[0,0,:]*(C[1,1,:]+C[2,2,:]))
    # a2 = (C[1,1,:]-C[2,2,:])/(C[1,1,:]+C[2,2,:])
    # b2 = 2*C[1,2,:]/(C[1,1,:]+C[2,2,:])
    
    # /!\ Important note: with the current definition of the Fourier coefficients,
    #     the associated 2D wave spectra will show where the energy is GOING TO 
    #     (direction of propagation of the wave components), and NOT where the 
    #     energy comes from.
    
    return Sf, a1, a2, b1, b2


def Shannon_MEMII_Newton(a1,a2,b1,b2,freq,theta,maxiter,tol_error,miniter=50,approx=False):
    """Reconstructs the directional spreading function based on the first four Fourier 
    coefficients of a directional wave spectrum.
    
    The function implements the Maximum Entropy Principle (Hashimoto, 1997), either via 
    running the Newton local linearisation method or following the approximation method
    by Kim et al. (1994).
    
    Parameters
    ----------
    a1, a2, b1, b2 : array_like of shape (Nf,)
        First four Fourier coefficients of the directional wave spectrum.
    freq : array_like of shape (Nf,)
        Vector of (discretized) wave frequencies [Hz].
    theta : array_like of shape (Ntheta,)
        Vector of wave headings [deg].
    maxiter : int
        Maximum number of iterations.
    tol_error : float
        Tolerance in the relative error.
    miniter : int, default 50
        Minimum number of iterations.
    approx : bool, default False
        Boolean which indicates whether the approximation method should be 
        used for finding the Lagrangian multipliers.

    Returns
    -------
    D : array_like of shape (Nf,Ntheta)
        Directional spreading function.
    flag : array_like of shape (Nf,)
        Boolean flag indicating unconverged frequencies 
        (``flag = 0`` for unconverged)
    L1, L2, L3, L4 : array_like of shape (Nf,)
        Optimized Lagrange multipliers.

    See Also
    --------
    cross_spec2Fourier_coef : Computes the Fourier coefficients from the cross-spectra 
        of a heave-East-North wave buoy.
    netsse.analys.emep.emep : Extended Maximum Entropy Principle (EMEP) method for 
        reconstructing the directional spreading function based on the cross-power 
        spectra of measured wave-induced responses.
    
    References
    ----------
    1. Benoit, M., Frigaard, P., & Schäffer, H. A. (1997). *Analysing Multidirectional
       Wave Spectra: A tentative classification of available methods*. Proceedings of 
       the 27th IAHR Congress, San Francisco, CA, USA (pp. 131–158). 
       Canadian Government Publishing.
    2. Hashimoto, N. (1997). *Analysis of the Directional Wave Spectrum from Field 
       Data*. Advances in coastal and ocean engineering. 3:103-44.
    3. Kim, T., Lin, L.-H., & Wang, H. (1994). *Application of Maximum Entropy Method 
       to the Real Sea Data*. In Coastal Engineering (pp. 340–355).
    
    Example
    -------
    >>> D, flag, L1, L2, L3, L4 =
    ...     Shannon_MEMII_Newton(a1,a2,b1,b2,freq,theta,maxiter,tol_error,miniter=50,False)
    """
    Nf = len(freq); Ntheta = len(theta)
    theta_rad = theta*np.pi/180
    D = np.zeros((Nf,Ntheta))
    flag = np.zeros((Nf,))
    L1, L2, L3, L4 = np.zeros((Nf,maxiter)),np.zeros((Nf,maxiter)),\
                        np.zeros((Nf,maxiter)),np.zeros((Nf,maxiter))
    
    # Changing the Fourier coefficients symbols for ease:
    B_all = np.array([a1,b1,a2,b2])
    A = np.array([np.cos(theta_rad),np.sin(theta_rad),\
                  np.cos(2*theta_rad),np.sin(2*theta_rad)]) # A values

    # Make calculations frequency per frequency
    for a in range(Nf):
        # Fourier coefficients for current frequency:
        B = B_all[:,a]

        # Initialisation:
        # Approximate solutions to the Lagrange multipliers (Kim et al. 1995):
        L1[a,0] = 2*B[0]*B[2]+2*B[1]*B[3]-2*B[0]*(1+np.sum(B**2))
        L2[a,0] = 2*B[0]*B[3]-2*B[1]*B[2]-2*B[1]*(1+np.sum(B**2))
        L3[a,0] = B[0]**2-B[1]**2-2*B[2]*(1+np.sum(B**2))
        L4[a,0] = 2*B[0]*B[1]-2*B[3]*(1+np.sum(B**2))
        b = 0
        
        if not approx: 
            # Apply Newton's technique of local linearization and iteration
            # (Hashimoto 1997):
            for b in range(maxiter-1): # Iteration loop
                L = np.array([L1[a,b],L2[a,b],L3[a,b],L4[a,b]]).reshape((4,1))
                A_bar = np.zeros((4,4)); B_bar = np.zeros((4,))
                for ii in range(4):
                    for jj in range(4):
                        A_bar[ii,jj] = trapezoid((A[ii,:]-B[ii,])*A[jj,:]*np.exp(-np.sum(L*A,axis=0)),theta_rad)
                        B_bar[ii,] = trapezoid((A[ii,:]-B[ii,])*np.exp(-np.sum(L*A,axis=0)),theta_rad)
                
                # Solving linear system of equations to get the error:
                e = np.reshape(np.linalg.inv(A_bar).dot(B_bar),(4,1))
                # Next value of Lagrange multipliers for next iteration:
                [L1[a,b+1],L2[a,b+1],L3[a,b+1],L4[a,b+1]] = L+e
                
                # Break loop if converged early:
                if b > miniter:
                    rel_err1 = np.abs(L1[a,b+1]-L1[a,b])/L1[a,b]
                    rel_err2 = np.abs(L2[a,b+1]-L2[a,b])/L2[a,b]
                    rel_err3 = np.abs(L3[a,b+1]-L3[a,b])/L3[a,b]
                    rel_err4 = np.abs(L4[a,b+1]-L4[a,b])/L4[a,b]
                    
                    # Check convergence for the particular frequency:
                    if (rel_err1 < tol_error and rel_err2 < tol_error and \
                        rel_err3 < tol_error and rel_err4 < tol_error):
                        flag[a,] = 1
                        b += 1
                        break

        # Extract the optimal values of the Lagrangian multipliers:
        L1_star = L1[a,b]
        L2_star = L2[a,b]
        L3_star = L3[a,b]
        L4_star = L4[a,b]
        L = np.array([L1_star,L2_star,L3_star,L4_star]).reshape((4,1))
        
        # Calculate L0
        L0 = np.log(trapezoid(np.exp(-np.sum(L*A,axis=0)),theta_rad))
   
        # Compute the directional spreading function D:
        D[a,:] = np.exp(-L0-np.sum(L*A,axis=0))
    
    return D, flag, L1, L2, L3, L4


def Fourier2spread_dist_params(a1,b1,a2,b2):
    """Infers the parameters of the directional spreading distribution function 
    from the Fourier coefficients, as per Kuik et al. (1988).
    
    Parameters
    ----------
    a1, b1, a2, b2 : array_like of shape (Nf,)
        First four Fourier coefficients of the directional wave spectrum.

    Returns
    -------
    alpha : array_like of shape (Nf,)
        Wave direction [rad].
    sigma : array_like of shape (Nf,)
        Directional spread [rad].
    gamma : array_like of shape (Nf,)
        Skewness of the directional distribution [-].
    delta : array_like of shape (Nf,)
        Kurtosis of the directional distribution [-].

    See Also
    --------
    spread_dist_params2Fourier : Infers the Fourier coefficients from the 
        parameters of the directional spreading distribution function.
        
    References
    ----------
    Kuik, A. J., van Vledder, G. P., & Holthuijsen, L. H. (1988). *A Method for 
    the Routine Analysis of Pitch-and-Roll Buoy Wave Data*. Journal of Physical 
    Oceanography, 18(7), 1020–1034.

    Example
    -------
    >>> [alpha, sigma, gamma, delta] = Fourier2spread_dist_params(a1,b1,a2,b2)
    """
    alpha = np.atan2(b1,a1)
    m1 = np.sqrt(a1**2+b1**2)
    m2 = a2*np.cos(2*alpha)+b2*np.sin(2*alpha)
    n2 = b2*np.cos(2*alpha)-a2*np.sin(2*alpha)
    sigma = np.sqrt(2*(1-m1))
    gamma = -n2/((1-m2)/2)**(3/2)
    delta = (6-8*m1+2*m2)/(2*(1-m1))**2
        
    return alpha, sigma, gamma, delta 


def spread_dist_params2Fourier(alpha, sigma, gamma, delta, unit='rad'):
    """Infers the Fourier coefficients from the parameters of the directional
    spreading distribution function, as per Kuik et al. (1988).
    
    Parameters
    ----------
    alpha : array_like of shape (Nf,)
        Wave direction [rad, or deg].
    sigma : array_like of shape (Nf,)
        Directional spread [rad, or deg].
    gamma : array_like of shape (Nf,)
        Skewness of the directional distribution [-].
    delta : array_like of shape (Nf,)
        Kurtosis of the directional distribution [-].
    unit : {'rad','deg'}, optional
        Unit of the wave direction and directional spread: ``'deg'`` or ``'rad'``
        (default).

    Returns
    -------
    a1, b1, a2, b2 : array_like of shape (Nf,)
        First four Fourier coefficients of the directional wave spectrum.

    See Also
    --------
    Fourier2spread_dist_params : Infers the parameters of the directional 
        spreading distribution function from the Fourier coefficients.
    Shannon_MEMII_Newton : Reconstructs the directional spreading function 
        based on the first four Fourier coefficients of a directional wave spectrum.

    References
    ----------
    Kuik, A. J., van Vledder, G. P., & Holthuijsen, L. H. (1988). *A Method for 
    the Routine Analysis of Pitch-and-Roll Buoy Wave Data*. Journal of Physical 
    Oceanography, 18(7), 1020–1034.

    Example
    -------
    >>> [a1,b1,a2,b2] = spread_dist_params2Fourier(alpha,sigma,gamma,delta,unit)
    """
    if unit=='deg':
        alpha = np.radians(alpha)
        sigma = np.radians(sigma)
        
    m1 = np.abs(1-sigma**2/2)
    
    a1 = np.sign(np.cos(alpha))*m1*(1+np.tan(alpha)**2)**(-1/2)
    b1 = a1*np.tan(alpha)
    
    m2 = 4*m1+2*delta*(1-m1)**2-3
    n2 = -gamma*((1-m2)/2)**(3/2)
    
    a2 = m2*np.cos(2*alpha)-n2*np.sin(2*alpha)
    b2 = m2*np.sin(2*alpha)+n2*np.cos(2*alpha)
    
    return a1, b1, a2, b2