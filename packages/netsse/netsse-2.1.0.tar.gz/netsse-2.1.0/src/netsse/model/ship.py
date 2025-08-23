# -*- coding: utf-8 -*-
"""
Closed-form expressions of the linear wave-to-motion transfer functions
for a box-shaped uniformly-loaded **monohull ship**.

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
# import warnings


def heaveCF(om0, beta_deg, U, L, B0, T, C_B=1):
    """Computes the heave transfer function amplitude, using the closed-form
    expressions presented in Jensen et al. (2004).

    Parameters
    ----------
    om0 : array_like of shape (Nom0,)
        Vector of absolute wave frequencies [rad/s].
    beta_deg : array_like of shape (Nbeta,)
        Vector of heading angles [deg].
    U : float
        Vessel forward speed [m/s].
    L : float
        Length of the ship [m].
    B0 : float
        Breadth of the ship [m].
    T : float
        Draft of the ship [m].
    C_B : float, default 1
        Block coefficient of the ship [-].

    Returns
    -------
    heave : numpy.ndarray of shape (Nom0,Nbeta)
        Coefficients of the heave transfer function amplitude [m/m].

    See Also
    --------
    pitchCF, rollCF : Computes the pitch/roll transfer function amplitude
        using closed-form expressions.

    References
    ----------
    Jensen, J. J., Mansour, A. E., & Olsen, A. S. (2004). Estimation of ship
    motions using closed-form expressions. Ocean Engineering, 31(1), 61–85.
    https://doi.org/10.1016/S0029-8018(03)00108-2

    Example
    -------
    >>> heave = heaveCF(om0,beta_deg,U,L,B0,T,C_B=1)
    """
    # warnings.filterwarnings("ignore", category=RuntimeWarning)

    # Physical quantities:
    g = 9.81  # Gravitational acceleration [m/s^2]

    beta = np.array(beta_deg * np.pi / 180).reshape((-1, 1))
    Fn = U / np.sqrt(g * L)
    k = np.square(om0) / g
    k[np.where(k < 1e-9)] = 1e-9
    B = B0 * C_B  # correction of the breadth B0 for shape effect of the hull geometry

    heave = np.zeros((len(om0), len(beta)))

    for i, beta_i in enumerate(beta):
        alpha = 1 - Fn * np.sqrt(k * L) * np.cos(beta_i)
        ome = om0 - k * U * np.cos(beta_i)
        A = 2 * np.sin(np.square(ome) * B / (2 * g)) * np.exp(-np.square(ome) * T / g)
        ke = np.abs(k * np.cos(beta_i))
        f = np.sqrt((1 - k * T) ** 2 + (A**2 / (k * B * alpha**3)) ** 2)
        kappa = np.exp(-k * T)

        F = kappa * f * 2 / (ke * L) * np.sin(ke * L / 2)
        eta = 1 / np.sqrt(
            (1 - 2 * k * T * alpha**2) ** 2 + (A**2 / (k * B * alpha**2)) ** 2
        )
        heave[:, i] = np.reshape(eta * np.abs(F), (-1,))

    # warnings.filterwarnings("default", category=RuntimeWarning)

    return heave


def pitchCF(om0, beta_deg, U, L, B0, T, C_B=1):
    """Computes the pitch transfer function amplitude, using the closed-form
    expressions presented in Jensen et al. (2004).

    Parameters
    ----------
    om0 : array_like of shape (Nom0,)
        Vector of absolute wave frequency [rad/s].
    beta_deg : array_like of shape (Nbeta,)
        Vector of heading angle [deg].
    U : float
        Vessel forward speed [m/s].
    L : float
        Length of the ship [m].
    B0 : float
        Breadth of the ship [m].
    T : float
        Draft of the ship [m].
    C_B : float, default 1
        Block coefficient of the ship [-].

    Returns
    -------
    pitch : numpy.ndarray of shape (Nom0,Nbeta)
        Coefficients of the pitch transfer function amplitude [rad/m].

    See Also
    --------
    heaveCF, rollCF : Computes the heave/roll transfer function amplitude using
        closed-form expressions.

    References
    ----------
    Jensen, J. J., Mansour, A. E., & Olsen, A. S. (2004). Estimation of ship
    motions using closed-form expressions. Ocean Engineering, 31(1), 61–85.
    https://doi.org/10.1016/S0029-8018(03)00108-2

    Example
    -------
    >>> pitch = pitchCF(om0,beta_deg,U,L,B0,T,C_B=1)
    """
    # warnings.filterwarnings("ignore", category=RuntimeWarning)

    # Physical quantities:
    g = 9.81  # Gravitational acceleration [m/s^2]

    beta = np.array(beta_deg * np.pi / 180).reshape((-1, 1))
    Fn = U / np.sqrt(g * L)
    k = np.square(om0) / g
    k[np.where(k < 1e-9)] = 1e-9
    B = B0 * C_B  # correction of the breadth B0 for shape effect of the hull geometry

    pitch = np.zeros((len(om0), len(beta)))

    for i, beta_i in enumerate(beta):
        # In case beta==90 deg or 270 deg, the amplitude of pitch is taken as
        # 10% of the amplitude at beta==100 deg (would be zero otherwise):
        # if (beta_i+np.pi/2)%np.pi == 0.:
        #     beta_i += np.pi/180
        #     eta = 1.0
        # else:
        #     eta = 1.0
        alpha = 1 - Fn * np.sqrt(k * L) * np.cos(beta_i)
        ome = om0 - k * U * np.cos(beta_i)
        A = 2 * np.sin(np.square(ome) * B / (2 * g)) * np.exp(-np.square(ome) * T / g)
        ke = np.abs(k * np.cos(beta_i))
        f = np.sqrt((1 - k * T) ** 2 + (A**2 / (k * B * alpha**3)) ** 2)
        kappa = np.exp(-k * T)

        G = (
            kappa
            * f
            * 24
            / ((ke * L) ** 2 * L)
            * (np.sin(ke * L / 2) - ke * L / 2 * np.cos(ke * L / 2))
        )
        eta = 1 / np.sqrt(
            (1 - 2 * k * T * alpha**2) ** 2 + (A**2 / (k * B * alpha**2)) ** 2
        )

        pitch[:, i] = np.reshape(eta * np.abs(G), (-1,))

    # warnings.filterwarnings("default", category=RuntimeWarning)

    return pitch


def rollCF(om0, beta_deg, U, L, B0, T, C_B, C_WP, GM_T, kappa, mu, T_N=0):
    """Computes the roll transfer function amplitude, using the closed-form
    expressions presented in Jensen et al. (2004).

    Parameters
    ----------
    om0 : array_like of shape (Nom0,)
        Vector of absolute wave frequencies [rad/s].
    beta_deg : array_like of shape (Nbeta,)
        Vector of heading angles [deg].
    U : float
        Vessel forward speed [m/s].
    L : float
        Length of the ship [m].
    B0 : float
        Breadth of the ship [m].
    T : float
        Draft of the ship [m].
    C_B : float
        Block coefficient of the ship [-].
    C_WP : float
        Waterplane area coefficient of the ship [-].
    GM_T : float
        Transverse metacentric height [m].
    kappa : float
        Custom parameter (chosen between 0 and ``C_WP``) representing the ratio
        between the length of the aft beam and the whole ship length in the
        simplified ship model for roll.
    mu : float, default 0
        Ratio between added viscous damping and critical damping.
    T_N : float, optional
        Roll natural period [s].

        .. note::
            If not specified as input, ``T_N`` is calculated using empirical
            formulas from ADA147598.

    Returns
    -------
    roll : numpy.ndarray of shape (Nom0,Nbeta)
        Coefficients of the roll transfer function amplitude [rad/m].

    See Also
    --------
    heaveCF, pitchCF : Computes the heave/pitch transfer function amplitude using
        closed-form expressions.

    References
    ----------
    1. Jensen, J. J., Mansour, A. E., & Olsen, A. S. (2004). Estimation of ship
       motions using closed-form expressions. Ocean Engineering, 31(1), 61–85.
       https://doi.org/10.1016/S0029-8018(03)00108-2
    2. ADA147598, 1973. Code of Safety for Fishermen and Fishing Vessels.
       Part B. Safety and Health Requirements for the Construction and Equipment
       of Fishing Vessels. Inter-Governmental Maritime Consultative Organization,
       London, England.

    Example
    -------
    >>> roll = rollCF(om0,beta_deg,U,L,B0,T,C_B,C_WP,GM_T,kappa,mu,T_N=0)
    """
    # warnings.filterwarnings("ignore", category=RuntimeWarning)

    # Physical quantities:
    g = 9.81  # Gravitational acceleration [m/s^2]
    rho = 1025  # Density of seawater [kg/m^3]

    roll = np.zeros((len(om0), len(beta_deg)))

    if om0[0,] == 0.0:
        om0 = om0[1:,]
        start_om = int(1)
    else:
        start_om = int(0)

    beta = np.radians(beta_deg)
    k = om0**2 / g
    k[np.where(k < 1e-100)] = 1e-100

    delta = np.amax((C_WP - kappa, 0))
    gamma = np.amax((kappa / (1 - delta), 1 / 6))
    B1 = gamma * B0

    # The ship draught T should be less than B0 and B1, and should not be
    # lower than B0/6 and B1/6:
    T = np.amax((np.amin((T, B0, B1)), B0 / 6, B1 / 6))
    Delta = L * B0 * T * C_B * rho  # Displacement [kg]

    # Roll natural period [s]:
    if T_N == 0:
        # Select the factor for the rolling period (found in IMO A.685(17)
        # resolution and ADA147598):
        if L < 45:
            f = 0.4
        else:
            f = 0.373 + 0.023 * (B0 / T) - 0.043 * (L / 100)
        T_N = 2 * f * B0 / np.sqrt(GM_T)

    C44 = g * Delta * GM_T  # Restoring moment coefficient
    B44_crit = C44 * T_N / np.pi  # Critical roll damping

    A0 = C_B * B0 * T / (delta + gamma * (1 - delta))
    A1 = gamma * A0

    if (B0 / T >= 3) & (B0 / T <= 6):
        aBT0 = 0.256 * B0 / T - 0.286
        bBT0 = -0.11 * B0 / T - 2.55
        dBT0 = 0.033 * B0 / T - 1.419
    elif (B0 / T >= 0.99) & (B0 / T < 3):
        aBT0 = -3.94 * B0 / T + 13.69
        bBT0 = -2.12 * B0 / T - 1.89
        dBT0 = 1.16 * B0 / T - 7.97

    if (B1 / T >= 3) & (B1 / T <= 6):
        aBT1 = 0.256 * B1 / T - 0.286
        bBT1 = -0.11 * B1 / T - 2.55
        dBT1 = 0.033 * B1 / T - 1.419
    elif (B1 / T >= 0.99) & (B1 / T < 3):
        aBT1 = -3.94 * B1 / T + 13.69
        bBT1 = -2.12 * B1 / T - 1.89
        dBT1 = 1.16 * B1 / T - 7.97

    for i, beta_i in enumerate(beta):
        ome = np.abs(om0 - k * U * np.cos(beta_i))
        ome[np.where(ome < 1e-100)] = 1e-100
        ke = np.abs(k * np.cos(beta_i))
        ke[np.where(ke < 1e-100)] = 1e-100

        b44_0 = (
            rho
            * A0
            * B0**2
            * np.sqrt(2 * g / B0)
            * aBT0
            * np.exp(bBT0 * ome ** (-1.3))
            * ome**dBT0
        )
        b44_0[np.where(b44_0 < 1e-100)] = 1e-100
        b44_1 = (
            rho
            * A1
            * B1**2
            * np.sqrt(2 * g / B1)
            * aBT1
            * np.exp(bBT1 * ome ** (-1.3))
            * ome**dBT1
        )
        kappa = np.sqrt(1 + (b44_1 - b44_0) / b44_0)
        B44_invisc = (
            L * b44_0 * (delta + kappa**2 * (1 - delta))
        )  # Roll hydrodynamic damping
        B44_tot = B44_invisc + mu * B44_crit

        # Amplitude of the roll excitation moment:
        M_abs = (
            np.abs(np.sin(beta_i))
            * np.sqrt(rho * g**2 / ome)
            * 2
            / ke
            * np.sqrt(b44_0)
            * np.sqrt(
                np.sin(0.5 * delta * L * ke) ** 2
                + kappa**2 * np.sin(0.5 * (1 - delta) * L * ke) ** 2
                + 2
                * kappa
                * np.sin(0.5 * delta * L * ke)
                * np.sin(0.5 * (1 - delta) * L * ke)
                * np.cos(0.5 * L * ke)
            )
        )

        roll[start_om:, i] = M_abs / np.sqrt(
            (-(ome**2) * (T_N / (2 * np.pi)) ** 2 + 1) ** 2 * C44**2
            + ome**2 * B44_tot**2
        )

    # warnings.filterwarnings("default", category=RuntimeWarning)

    return roll
