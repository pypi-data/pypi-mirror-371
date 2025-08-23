# -*- coding: utf-8 -*-
"""
Functions to compute spectra in a **body-fixed** reference system.

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
from scipy.interpolate import interp1d
# from scipy.integrate import trapezoid, cumulative_trapezoid
# from scipy.linalg import block_diag
from netsse.tools.misc_func import *

def resp_spec_1d(f0,ws,TRF1,TRF2,fe,U,beta):
    """Computes a response cross-spectrum in both the absolute and encountered 
    frequency domains, in a case of long-crested seas.

    Parameters
    ----------
    f0 : array_like of shape (Nf0,1)
        Vector of absolute frequencies [Hz].
    ws : array_like of shape (Nf0,1) in 1-D
        1-D wave spectrum, as a function of (absolute) wave frequency ``f0`` [Hz].
    TRF1, TRF2 : array_like of shape (Nf0,1)
        Transfer functions of two response components, as a function of frequency
        ``f0`` [Hz].
    fe : array_like of shape (Nfe,1)
        Vector of encounter frequencies [Hz].
    U : float
        Ship speed [m/s].
    beta : float
        Ship heading, relative to the wave direction [deg].

    Returns
    -------
    RspecAbs: array_like of shape (Nf0,1)
        Response spectrum, as a function of absolute wave frequency ``f0`` [Hz].
    RspecEnc: array_like of shape (Nfe,1)
        Response spectrum, as a function of encountered frequency ``fe`` [Hz].

    See Also
    --------
    resp_spec_2d : Computes a response cross-spectrum in the encounter-frequency 
        domain, in case of short-crested sea.
    
    Example
    -------
    >>> RspecAbs, RspecEnc = resp_spec_1d(f0,ws,TRF1,TRF2,fe,U,beta)
    """
    g = 9.81 # Gravitational acceleration [m/s^2]

    df0 = f0[1]-f0[0]    # Step size in absolute frequencies [Hz]
    omega0 = 2*np.pi*f0  # Angular wave frequency [rad/s]
    Nf0 = len(f0)
    Nfe = len(fe)
    A = 2*np.pi*U/g*np.cos(np.radians(beta))
    
    # Response spectrum in the absolute frequency domain
    RspecAbs = np.reshape(TRF1*np.conj(TRF2)*ws,(-1,))
    if areSame_vec(TRF1,TRF2):
        RspecAbs = np.real(RspecAbs)
    
    # Compute the encounter domain response spectrum 
    if A == 0. or (beta >= 90 and beta <= 270):
        # Response spectrum in the encounter domain
        fe_resp = 1/(2*np.pi)*(omega0-omega0**2*U/g*np.cos(np.pi/180*beta))    
        RspecEnc = RspecAbs*(g/(g-2*omega0*U*np.cos(np.pi/180*beta)))
        
        # Interpolate the response spectrum at the user-specified range of 
        # encounter frequencies:
        f1 = interp1d(fe_resp,RspecEnc,bounds_error=False,fill_value=0.)
        RspecEnc = f1(fe)
                                
    else: # Following sea cases
        RspecEnc = np.zeros((Nfe))
        for j in range(Nfe):
            
            f03 = (1+np.sqrt(1+4*A*fe[j]))/(2*A)  # This wave freq. always exists
            df3de = 1/np.sqrt(1+4*A*fe[j])
            if (f03 > f0[0] and f03 < f0[Nf0-1]):
                m1_3 = np.int32((f03-f0[0])/df0)
                m2_3 = m1_3+1
                if m2_3 > Nf0-1:
                    continue                   
                b = df3de*(f03-f0[m1_3])/df0
                a = df3de*(f0[m2_3]-f03)/df0                    
                RspecEnc[j] += (ws[m1_3]*np.abs(TRF1[m1_3]*np.conj(TRF2[m1_3])))*b + \
                                (ws[m2_3]*np.abs(TRF1[m2_3]*np.conj(TRF2[m2_3])))*a
                                                
            if fe[j] < 1/(4*A):
                f01 = (1-np.sqrt(1-4*A*fe[j]))/(2*A) # 1st conditional wave freq.
                df1de = 1/np.sqrt(1-4*A*fe[j])
                f02 = (1+np.sqrt(1-4*A*fe[j]))/(2*A)  # 2nd conditional wave freq.
                df2de = df1de
                
                if (f01 > f0[0] and f01 < f0[Nf0-1]):
                    m1_1 = np.int32((f01-f0[0])/df0)
                    m2_1 = m1_1+1
                    if m2_1 > Nf0-1:
                        continue                    
                    b = df1de*(f01-f0[m1_1])/df0
                    a = df1de*(f0[m2_1]-f01)/df0
                    
                    RspecEnc[j] += (ws[m1_1]*np.abs(TRF1[m1_1]*np.conj(TRF2[m1_1])))*b + \
                                    (ws[m2_1]*np.abs(TRF1[m2_1]*np.conj(TRF2[m2_1])))*a
                
                if (f02>f0[0] and f02<f0[Nf0-1]):
                    m1_2 = np.int32((f02-f0[0])/df0)
                    m2_2 = m1_2+1
                    if m2_2 > Nf0-1:
                        continue                    
                    b = df2de*(f02-f0[m1_2])/df0
                    a = df2de*(f0[m2_2]-f02)/df0
                    
                    RspecEnc[j] += (ws[m1_2]*np.abs(TRF1[m1_2]*np.conj(TRF2[m1_2])))*b + \
                                    (ws[m2_2]*np.abs(TRF1[m2_2]*np.conj(TRF2[m2_2])))*a
        
    return RspecAbs, RspecEnc


def resp_spec_2d(freq0,mu,ws0,beta_TRF,TRF1,TRF2,freqE,U,psi,conv='from',unit_freq='rad/s'):
    """Computes a response cross-spectrum in the encounter-frequency domain, in a case of 
    short-crested seas.

    .. note::
        This is a Python implementation of the algorithm given in Nielsen et al. (2021).

    Parameters
    ----------
    freq0 : array_like of shape (Nf0,)
        Vector of absolute frequencies, in which the wave spectrum and the
        transfer functions are expressed.
    mu : array_like of shape (Nmu,)
        Vector of wave directions [deg], relative to North (in a NED-reference frame).
    ws0 : array_like of shape (Nf0,Nmu) in 2-D
        2-D wave spectrum, as a function of (absolute) wave frequency ``freq0`` and wave
        direction ``mu`` [rad].
    beta_TRF : array_like of shape (Nbeta,)
        Vector of relative wave headings [deg], in which the transfer functions
        are expressed.
    TRF1, TRF2 : array_like of shape (Nf0,Nbeta)
        Transfer function of the first and second response component, respectively, as a 
        function of frequency ``freq0`` and relative wave heading.
    freqE : array_like of shape (Nfe,)
        Vector of encounter frequencies for the output response spectrum.
    U : float
        Ship speed [m/s]
    psi : float
        Ship heading [deg], relative to North (in a NED-reference frame).
    conv: {'from','to'}, optional
        The convention that is used to express the direction ``mu`` of wave spectrum: 

        - 'from' :
            The naval architecture convention, indicating where the waves are COMING FROM.
        - 'to' :
            The oceanographic convention, indicating where the waves are GOING TO.
            The default is "from" direction.
    unit_freq : {'rad/s','Hz'}, optional
        Unit of the frequencies: 

        - 'rad/s' : 
            The variables ``freq0`` and ``freqE`` denote the angular frequencies in radians 
            per second.
        - 'Hz' : 
            The 2-D wave spectrum ``ws0`` is expressed as a function of frequency in Hertz.  
            The default is 'rad/s'.

    Returns
    -------        
    RspecEnc: array_like of shape (Nfe,)
        Response spectrum, as a function of encounter frequency ``freqE``.

    See Also
    --------
    resp_spec_1d : Computes a response cross-spectrum in both the absolute and encountered 
        frequency domains, in a case of long-crested seas.
        
    References
    ----------
    Nielsen, U. D., Mounet, R. E. G., & Brodtkorb, A. H. (2021). Tuning of 
    transfer functions for analysis of wave-ship interactions. Marine 
    Structures, 79, 103029. https://doi.org/10.1016/j.marstruc.2021.103029

    Example
    -------
    >>> RspecEnc =
    ...     resp_spec_2d(freq0,mu,ws0,beta_TRF,TRF1,TRF2,freqE,U,psi,'from','rad/s')
    """
    g = 9.81 # Gravitational acceleration [m/s^2]

    if unit_freq == 'rad/s':
        f0 = freq0/(2*np.pi)
        fe = freqE/(2*np.pi)
        ws = ws0*(2*np.pi)
    else:
        f0 = freq0
        fe = freqE
        ws = ws0

    df0 = f0[1]-f0[0]    # Step size in absolute frequencies [Hz]
    Nf0 = len(f0)
    Nfe = len(fe)
    Ndir = len(mu)    
    
    if mu[0,]%360==mu[-1,]%360:
        # The directions are actually wrapped around, so that mu[0,] = mu[-1,]
        # This is changed, to avoid counting directions twice!
        beta = mu[:-1,]-psi
        Ndir = Ndir-1
    else:
        beta = mu-psi
        
    if conv=='from':
        beta = re_range(180+beta)
    elif conv=='to':
        beta = re_range(beta)
    else:
        raise NameError('Invalid direction convention. Only accepts "from" or "to".')
    
    dbeta = 2*np.pi/Ndir
    A = 2*np.pi*U/g*np.cos(np.radians(beta))
    beta_TRF_new = re_range(beta_TRF)
    
    # To prepare the interpolation of the transfer functions at the directions
    # of the wave spectrum, make sure that the vector of directions at which 
    # the transfer functions are expressed is in a 'wrapped around' format, 
    # so that beta_TRF_new[0,] = beta_TRF_new[-1,] with a modulo 2*pi:    
    if beta_TRF_new[0,]%360 != beta_TRF_new[-1,]%360:
        beta_TRF_new = wrap(beta_TRF_new,axis=0,add=360)
        TRF1 = wrap(TRF1,axis=1)
        TRF2 = wrap(TRF2,axis=1)
    
    # Interpolate the transfer functions at the vector of wave directions:
    finterp_TRF1 = interp1d(beta_TRF_new,TRF1,kind='linear',axis=1)
    TRF1_interp = finterp_TRF1(beta)
    finterp_TRF2 = interp1d(beta_TRF_new,TRF2,kind='linear',axis=1)
    TRF2_interp = finterp_TRF2(beta)
    
    # Initialize the response spectrum:
    RspecEnc = np.zeros((Nfe,))
    
    for j in range(Nfe):
        fe_j = fe[j,]
        
        for k in range(Ndir): # Do not count the direction beta = 0 deg twice!
            beta_k = beta[k,]
            A_k = A[k,]

            if (beta_k >= 90 and beta_k <= 270): # Head sea cases
                
                f01 = (1-np.sqrt(1-4*A_k*fe_j))/(2*A_k)
                df1de = 1/np.sqrt(1-4*A_k*fe_j)
    
                if (f01 > f0[0,] and f01 < f0[Nf0-1,]):
                    # Only consider absolute (wave) frequencies for which 
                    # transfer functions are calculated/defined
                    m1 = np.int32((f01-f0[0,])/df0)
                    m2 = m1+1
                    if m2 > Nf0-1:
                        continue  
                    # 'a' and 'b' are the weights for interpolation to exact frequency
                    b = dbeta*df1de*(f01-f0[m1,])/df0
                    a = dbeta*df1de*(f0[m2,]-f01)/df0
                    RspecEnc[j,] += (ws[m1,k]*TRF1_interp[m1,k]*np.conj(TRF2_interp[m1,k]))*b + \
                                    (ws[m2,k]*TRF1_interp[m2,k]*np.conj(TRF2_interp[m2,k]))*a       
                                    
            else: # Following sea cases
                    
                f03 = (1+np.sqrt(1+4*A_k*fe_j))/(2*A_k)  # This wave freq. always exists
                df3de = 1/np.sqrt(1+4*A_k*fe_j)
                
                if (f03 > f0[0,] and f03 < f0[Nf0-1,]):
                    m1_3 = np.int32((f03-f0[0,])/df0)
                    m2_3 = m1_3+1
                    if m2_3 > Nf0-1:
                        continue                   
                    b = dbeta*df3de*(f03-f0[m1_3,])/df0
                    a = dbeta*df3de*(f0[m2_3,]-f03)/df0                    
                    RspecEnc[j,] += (ws[m1_3,k]*TRF1_interp[m1_3,k]*np.conj(TRF2_interp[m1_3,k]))*b + \
                                    (ws[m2_3,k]*TRF1_interp[m2_3,k]*np.conj(TRF2_interp[m2_3,k]))*a
                                                    
                if fe_j < 1/(4*A_k):                        
                    f01 = (1-np.sqrt(1-4*A_k*fe_j))/(2*A_k) # 1st conditional wave freq.
                    df1de = 1/np.sqrt(1-4*A_k*fe_j)
                    f02 = (1+np.sqrt(1-4*A_k*fe_j))/(2*A_k)  # 2nd conditional wave freq.
                    df2de = df1de
                    
                    if (f01 > f0[0,] and f01 < f0[Nf0-1,]):
                        m1_1 = np.int32((f01-f0[0,])/df0)
                        m2_1 = m1_1+1
                        if m2_1 > Nf0-1:
                            continue                    
                        b = dbeta*df1de*(f01-f0[m1_1])/df0
                        a = dbeta*df1de*(f0[m2_1]-f01)/df0
                        
                        RspecEnc[j,] += (ws[m1_1,k]*TRF1_interp[m1_1,k]*np.conj(TRF2_interp[m1_1,k]))*b + \
                                        (ws[m2_1,k]*TRF1_interp[m2_1,k]*np.conj(TRF2_interp[m2_1,k]))*a
                    
                    if (f02>f0[0,] and f02<f0[Nf0-1,]):
                        m1_2 = np.int32((f02-f0[0,])/df0)
                        m2_2 = m1_2+1
                        if m2_2 > Nf0-1:
                            continue                    
                        b = dbeta*df2de*(f02-f0[m1_2,])/df0
                        a = dbeta*df2de*(f0[m2_2,]-f02)/df0
                        
                        RspecEnc[j,] += (ws[m1_2,k]*TRF1_interp[m1_2,k]*np.conj(TRF2_interp[m1_2,k]))*b + \
                                        (ws[m2_2,k]*TRF1_interp[m2_2,k]*np.conj(TRF2_interp[m2_2,k]))*a
    
    if unit_freq == 'rad/s':
        RspecEnc = RspecEnc/(2*np.pi)

    return RspecEnc