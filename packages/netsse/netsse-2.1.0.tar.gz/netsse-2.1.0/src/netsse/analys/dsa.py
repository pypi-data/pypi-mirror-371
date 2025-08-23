# -*- coding: utf-8 -*-
"""
Functions for **transforming spectra** observed from advancing floating platforms.

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

*Last updated on 22-08-2025 by R.E.G. Mounet*

"""

import numpy as np
from netsse.tools.misc_func import re_range
from scipy.sparse import bsr_array, dia_array


def polynom_DSA(
    tau, om0m, weighting="uniform", nu23=(1 + 2 ** (1 / 2)) / 2, full_output=False
):
    r"""Computes the polynomial approximation of the Doppler Shift.

    .. note::
        This implementation uses the derivations presented in Mounet et al. (2025a,b).

    Parameters
    ----------
    tau : array_like of shape (Ntau,)
        Array of Doppler shift intensities.
    om0m : float
        Cut-off frequency of the DSA.
    weighting : {'uniform','tripvalpb','lowfreq'}, optional
        Weighting method to use:

        - 'uniform' :
            Equal weight is given to all frequencies in the range ``[0,om0m]`` in the cost
            function. This is the default option. It is introduced in Mounet et al. (2025a).
        - 'tripvalpb' :
            Same as ``'uniform'`` weighting, but the ``om0m`` is set to a value of
            :math:`(1+\sqrt{2})/(2\tau)` when :math:`\nu>\nu_{23}`. This ensures the DSA features
            an optimal accuracy in the range of frequencies where the triple-value problem occurs.
            This idea is introduced in Mounet et al. (2025b).
        - 'lowfreq' :
            A decreasing (affine) weighting function is applied in the range ``[0,om0m]``, such
            that low frequencies are given more importance in the cost function. This option is not
            recommended for general use.
    nu23 : float, optional
        Threshold value of ``nu`` for switching between the concave and convex forms of the
        approximation. Default is :math:`(1+\sqrt{2})/2`.
    full_output : bool, optional
        If True, the function returns ``nu``and ``kappa`` as additional outputs. Default is False.

    Returns
    -------
    rho_p : array_like of shape (Ntau,)
        Computed ``rho_p`` values.
    nu_p : array_like of shape (Ntau,)
        Computed ``nu_p`` values.
    nu : array_like of shape (Ntau,)
        Computed ``nu`` values.
    kappa : array_like of shape (Ntau,)
        Computed ``kappa`` values.

    See Also
    --------
    trans_2Dmat_DSA : Computes the matrices for applying the Doppler shift approximation (DSA).

    References
    ----------
    1. Mounet, R.E.G., Nielsen, U.D., and Takami, T. (2025a). "Doppler Shift Approximation in
       Seakeeping Problems: A New Formulation for Ships Advancing at Any Forward Speed." In:
       Proceedings of the 16th International Symposium on Practical Design of Ships and Other
       Floating Structures (PRADS 2025), Ann Arbor, MI, USA. (Accepted).
    2. Mounet, R.E.G., Nielsen, U.D., and Takami, T. (2025b). "Approximating the Doppler Shift in
       Sea-Wave Spectra Observed from an Advancing Floating Platform." Applied Mathematical
       Modelling. (Submitted).

    Example
    -------
    >>> rho_p, nu_p = polynom_DSA(tau, om0m, weighting='tripvalpb', full_output=False)
    """

    Ntau = np.shape(tau)[0]
    nu12 = 1 / 2
    nu = tau * om0m
    kappa = np.nanmin([np.ones((Ntau,)), 1 / nu], axis=0)

    match weighting:
        case "uniform":  # Used in the PRADS'25 paper (Mounet et al., 2025a)
            f1 = (
                1
                / 8
                * (
                    3 * nu * (-4 * kappa**5 + 10 * kappa**4 - 3)
                    + 15 * kappa**4
                    - 40 * kappa**3
                    + 41 / 2
                )
            )
            f2 = nu * (2 * kappa**5 - 1) - 5 / 2 * kappa**4 + 5 / 4
        case "tripvalpb":  # Used in the journal paper (Mounet et al., 2025b)
            Inu = np.nanmin(
                [np.ones(np.shape(tau)), (1 + np.sqrt(2)) / (2 * nu)], axis=0
            )
            f1 = 1 + (
                6 * nu * (Inu**4 - 2 * kappa**4) + 8 * (2 * kappa**3 - Inu**3)
            ) / (Inu**3 * (3 * Inu - 8))
            f2 = (4 * nu * (2 * kappa**5 - Inu**5) + 5 * (Inu**4 - 2 * kappa**4)) / (
                4 * Inu**5
            )
        case "lowfreq":  # Not recommended for general use
            f1 = (
                2
                / 5
                * (
                    nu * (10 * kappa**6 - 36 * kappa**5 + 30 * kappa**4 - 2)
                    + (-12 * kappa**5 + 45 * kappa**4 - 40 * kappa**3 + 6)
                )
            )
            f2 = nu * (-10 * kappa**6 + 12 * kappa**5 - 1) + (
                12 * kappa**5 - 15 * kappa**4 + 3 / 2
            )

    # Compute rho_p as a function of nu and kappa:
    rho_p = 0 * (nu <= nu12) + f1 * (nu > nu12) * (nu < nu23) + 1 * (nu >= nu23)

    # Compute nu_p as a function of nu and kappa:
    nu_p = (
        nu * (nu <= nu12) + (1 - f1) / 2 * (nu > nu12) * (nu < nu23) + f2 * (nu >= nu23)
    )

    if full_output:
        return rho_p, nu_p, nu, kappa
    return rho_p, nu_p


def trans_2Dmat_DSA(
    freq_in,
    beta,
    U,
    freq_out=None,
    unit_freq="rad/s",
    unit_beta="deg",
    conv="from",
    max_freq=None,
    nu23=(1 + 2 ** (1 / 2)) / 2,
    transform="abs2enc",
    weighting="uniform",
    highfreq_matching=True,
):
    r"""Computes the transformation matrices for applying the Doppler shift approximation (DSA) at the given forward speed and for the given frequency and direction discretizations.

    .. note::
        This implementation uses the derivations presented in Mounet et al. (2025a,b).

    Parameters
    ----------
    freq_in : array_like of shape (NfreqIN,)
        Input frequencies.
    beta : array_like of shape (Nbeta,)
        Relative wave heading angles.
    U : float
        Forward speed of the observer [m/s].
    freq_out : array_like of shape (NfreqOUT), optional
        Output frequencies. If None, it is set to freq_in.
    unit_freq : {'rad/s','Hz'}, optional
        Unit of the frequencies:

        - 'rad/s' :
            The variables ``freq_in`` and ``freq_out`` denote the angular frequencies in radians
            per second. The default is 'rad/s'.
        - 'Hz' :
            Frequencies are in Hertz.
    unit_beta : {'deg','rad'}, optional
        Unit of the relative wave heading angles ``beta`` ('deg' or 'rad'). Default is 'deg'.
    conv : {'from','to'}, optional
        The convention that is used to express the direction ``beta`` of wave spectrum:

        - 'from' :
            The naval architecture convention, indicating where the waves are COMING FROM.
        - 'to' :
            The oceanographic convention, indicating where the waves are GOING TO.
            The default is "from" direction.
    max_freq : float, optional
        Cut-off frequency. If None, it is set to the maximum of ``freq_in``.
    nu23 : float, optional
        Threshold parameter for the DSA. Default is :math:`(1+\sqrt{2})/2`.
    transform : str, optional
        Type of transformation ('abs2enc' or 'enc2abs'). Default is 'abs2enc'.
    weighting : {'uniform','tripvalpb','lowfreq'}, optional
        Weighting method to use:

        - 'uniform' :
            Equal weight is given to all frequencies in the range [0,om0m] in the cost function.
            This is the default option. It is introduced in Mounet et al. (2025a).
        - 'tripvalpb' :
            Same as ``'uniform'`` weighting, but the ``om0m`` is set to a value of
            :math:`(1+\sqrt{2})/(2\tau)` when :math:`\nu>\nu_{23}`. This ensures the DSA features
            an optimal accuracy in the range of frequencies where the triple-value problem occurs.
            This idea is introduced in Mounet et al. (2025b).
        - 'lowfreq' :
            A decreasing (affine) weighting function is applied to frequencies in the range
            [0,om0m], such that low frequencies are given more importance in the cost function.
            This option is not recommended for general use.
    highfreq_matching : bool, optional
        If ``True``, the convex form of the DSA is overriden to become exact beyond the point where
        the DSA and the exact Doppler shift intersect each other in Region III of the mapping.
        If ``False``, the DSA is kept unchanged otherwise. Default is True.

    Returns
    -------
    Omega_in_fromout : ndarray of shape (NfreqOUT,Nbeta)
        Approximated input frequencies as a function of the target frequencies and wave directions.
    C : ndarray of shape (NfreqOUT*Nbeta,NfreqIN*Nbeta)
        Linear interpolation matrix.
    D_wave : ndarray of shape (NfreqOUT*Nbeta,NfreqOUT*Nbeta)
        2D-to-2D transformation matrix for wave spectra.
    S : ndarray of shape (NfreqOUT,NfreqOUT*Nbeta)
        2D-to-1D summation matrix.

    See Also
    --------
    polynom_DSA : Computes the polynomial approximation of the Doppler Shift.

    References
    ----------
    1. Mounet, R.E.G., Nielsen, U.D., and Takami, T. (2025a). "Doppler Shift Approximation in
       Seakeeping Problems: A New Formulation for Ships Advancing at Any Forward Speed." In:
       Proceedings of the 16th International Symposium on Practical Design of Ships and Other
       Floating Structures (PRADS 2025), Ann Arbor, MI, USA. (Accepted).
    2. Mounet, R.E.G., Nielsen, U.D., and Takami, T. (2025b). "Approximating the Doppler Shift in
       Sea-Wave Spectra Observed from an Advancing Floating Platform." Applied Mathematical
       Modelling. (Submitted).

    Example
    -------
    >>> _, C, D, S = trans_2Dmat_DSA(
    ...     freq_in, beta, U, freq_out, unit_freq='Hz', unit_beta='deg', conv='from', max_freq=0.3,
    ...     nu23=2, transform='abs2enc', weighting="uniform", highfreq_matching=True)
    """

    g = 9.818  # Gravitational acceleration [m/s^2]

    # Define the absolute and encountered wave frequencies:
    if freq_out is None:
        freq_out = freq_in
    match unit_freq:
        case "rad/s":
            omega_in = freq_in
            omega_out = freq_out

            # Define the cut-off wave frequency:
            if max_freq is not None:
                omega_m = max_freq

        case "Hz":
            omega_in = 2 * np.pi * freq_in
            omega_out = 2 * np.pi * freq_out
            if max_freq is not None:
                omega_m = 2 * np.pi * max_freq

    if max_freq is None:
        omega_m = np.amax(omega_in)

    # Define the normalized frequencies:
    Omega_in = omega_in / omega_m
    Omega_out = omega_out / omega_m

    # Define the wave heading angles:
    match unit_beta:
        case "deg":
            beta_rad = np.radians(beta)
        case "rad":
            beta_rad = beta

    # Account for the direction convention:
    if conv == "from":
        beta_rad = re_range(beta_rad, unit="rad")
    elif conv == "to":
        beta_rad = re_range(beta_rad - np.pi, unit="rad")
    else:
        raise NameError('Invalid direction convention. Only accepts "from" or "to".')

    # Reshape the vector of absolute frequencies and relative wave headings:
    Omega_in = np.reshape(Omega_in, (-1, 1))
    Omega_out = np.reshape(Omega_out, (-1, 1))
    beta_rad = np.reshape(beta_rad, (1, -1))

    # Avoid counting twice the same direction:
    if beta_rad[0, 0] % (2 * np.pi) == beta_rad[0, -1] % (2 * np.pi):
        beta_rad = beta_rad[:, :-1]
        print("Warning: The direction vector has duplicates!")

    NOmega_in = np.shape(Omega_in)[0]
    NOmega_out = np.shape(Omega_out)[0]
    Nbeta = np.shape(beta_rad)[1]

    dOmega_in = Omega_in[1, 0] - Omega_in[0, 0]  # even spacing required in omega_in!
    dbeta = beta[1,] - beta[0,]  # even spacing required in beta!

    # Variables of the Doppler shift approximation:
    tau = U / g * np.cos(beta_rad)
    nu = tau * omega_m
    kappa = np.nanmin([np.ones(np.shape(tau)), 1 / nu], axis=0)

    match weighting:
        case "uniform":  # Used in the PRADS'25 paper (Mounet et al., 2025a).
            A1 = (
                1
                / 8
                * (
                    3 * nu * (-4 * kappa**5 + 10 * kappa**4 - 3)
                    + 15 * kappa**4
                    - 40 * kappa**3
                    + 41 / 2
                )
            )
            A2 = nu * (2 * kappa**5 - 1) - 5 / 2 * kappa**4 + 5 / 4
        case "tripvalpb":  # Used in the journal paper (Mounet et al., 2025b).
            Inu = np.nanmin(
                [np.ones(np.shape(tau)), (1 + np.sqrt(2)) / (2 * nu)], axis=0
            )
            A1 = 1 + (
                6 * nu * (Inu**4 - 2 * kappa**4) + 8 * (2 * kappa**3 - Inu**3)
            ) / (Inu**3 * (3 * Inu - 8))
            A2 = (4 * nu * (2 * kappa**5 - Inu**5) + 5 * (Inu**4 - 2 * kappa**4)) / (
                4 * Inu**5
            )
        case "lowfreq":  # Not recommended for general use.
            A1 = (
                2
                / 5
                * (
                    2 * nu * (5 * kappa**6 - 18 * kappa**5 + 15 * kappa**4 - 1)
                    + (-12 * kappa**5 + 45 * kappa**4 - 40 * kappa**3 + 6)
                )
            )
            A2 = nu * (-10 * kappa**6 + 12 * kappa**5 - 1) + (
                12 * kappa**5 - 15 * kappa**4 + 3 / 2
            )

    # Compute rho_p as a function of nu and kappa:
    nu12 = 1 / 2
    rho_p = 0 * (nu <= nu12) + A1 * (nu > nu12) * (nu < nu23) + 1 * (nu >= nu23)
    nu_p = (
        nu * (nu <= nu12) + (1 - A1) / 2 * (nu > nu12) * (nu < nu23) + A2 * (nu >= nu23)
    )

    # Compute the Doppler shift approximation:
    match transform:
        case "abs2enc":
            Omega_in_fromout = np.abs(
                1
                / (2 * nu_p)
                * ((1 - rho_p) - ((1 - rho_p) ** 2 - 4 * Omega_out * nu_p) ** (1 / 2))
            )

            # Avoid nan values:
            Omega_in_fromout[np.isnan(Omega_in_fromout)] = 0
            Omega_in_fromout[(Omega_in_fromout >= 1) * (nu > nu12) * (nu < nu23)] = 0

            # Compute matrix E:
            E = 1 / ((1 - rho_p) - 2 * nu_p * Omega_in_fromout)

            # Special handling for the cases beta=90° and beta=270°:
            i_beta_90 = np.argmin(np.abs(beta_rad - np.pi / 2))
            i_beta_270 = np.argmin(np.abs(beta_rad - 3 * np.pi / 2))
            if np.abs(beta_rad[0, i_beta_90] - np.pi / 2) < 1e-3:
                Omega_in_fromout[:, i_beta_90] = Omega_out[:, 0]
                E[:, i_beta_90] = 1
            if np.abs(beta_rad[0, i_beta_270] - 3 * np.pi / 2) < 1e-3:
                Omega_in_fromout[:, i_beta_270] = Omega_out[:, 0]
                E[:, i_beta_270] = 1

            # Special handling for the cases outside the range of the triple-value problem (TVP):
            if highfreq_matching:
                Omega0_lims = np.ones(np.shape(nu)) * np.inf
                index_above_nu23 = np.where(nu > nu23)[1]
                Omega0_lims[:, index_above_nu23] = 1 / (
                    nu[0, index_above_nu23] + nu_p[0, index_above_nu23]
                )
                index_outside_TVP = np.where(Omega_in_fromout > Omega0_lims)
                Omega_in_fromout_regIII = (1 + np.sqrt(1 + 4 * nu * Omega_out)) / (
                    2 * nu
                )
                Omega_in_fromout[index_outside_TVP] = Omega_in_fromout_regIII[
                    index_outside_TVP
                ]
                E[index_outside_TVP] = np.abs(
                    1
                    / (
                        -1
                        + 2
                        * nu[0, index_outside_TVP[1]]
                        * Omega_in_fromout[index_outside_TVP]
                    )
                )

        case "enc2abs":
            # Compute matrix E:
            E = (1 - rho_p) - 2 * nu_p * Omega_out

            # Compute the encounter frequency by the DSA:
            Omega_in_fromout = (1 - rho_p) * Omega_out - nu_p * Omega_out**2
            Omega_in_fromout[np.isnan(Omega_in_fromout)] = 0
            Omega_in_fromout[E < 0] = 0
            E[E < 0] = 0

            # Special handling for the cases beta=90° and beta=270°:
            i_beta_90 = np.argmin(np.abs(beta_rad - np.pi / 2))
            i_beta_270 = np.argmin(np.abs(beta_rad - 3 * np.pi / 2))
            if np.abs(beta_rad[0, i_beta_90] - np.pi / 2) < 1e-3:
                Omega_in_fromout[:, i_beta_90] = Omega_out[:, 0]
                E[:, i_beta_90] = 1
            if np.abs(beta_rad[0, i_beta_270] - 3 * np.pi / 2) < 1e-3:
                Omega_in_fromout[:, i_beta_270] = Omega_out[:, 0]
                E[:, i_beta_270] = 1

            # Special handling for the cases outside the range of the triple-value problem (TVP):
            if highfreq_matching:
                Omegae_lims = np.ones(np.shape(nu)) * np.inf
                index_above_nu23 = np.where(nu > nu23)[1]
                Omegae_lims[:, index_above_nu23] = (
                    -nu_p[0, index_above_nu23]
                    / (nu[0, index_above_nu23] + nu_p[0, index_above_nu23]) ** 2
                )
                index_outside_TVP = np.where(Omega_in_fromout - Omegae_lims > 0)
                Omega_in_fromout_regIII = -Omega_out + nu * Omega_out**2
                Omega_in_fromout[index_outside_TVP] = Omega_in_fromout_regIII[
                    index_outside_TVP
                ]
                E[index_outside_TVP] = (
                    -1
                    + 2
                    * nu[0, index_outside_TVP[1]]
                    * Omega_out[index_outside_TVP[0], 0]
                )

    # Build matrix C:
    N1 = np.int64(np.floor(Omega_in_fromout / dOmega_in))
    N2 = N1 + 1
    A = np.zeros((NOmega_out, Nbeta), dtype=np.float32)
    B = np.zeros((NOmega_out, Nbeta), dtype=np.float32)
    A[N2 < NOmega_in] = (
        1
        / dOmega_in
        * (Omega_in[N2[N2 < NOmega_in], 0] - Omega_in_fromout[N2 < NOmega_in])
    )
    B[N2 < NOmega_in] = (
        1
        / dOmega_in
        * (Omega_in_fromout[N2 < NOmega_in] - Omega_in[N1[N2 < NOmega_in], 0])
    )
    N1[N2 >= NOmega_in] = 0
    N2[N2 >= NOmega_in] = 0

    rows, cols, data = [], [], []
    for k in range(NOmega_out):
        for p in range(Nbeta):
            rows.append(k * Nbeta + p)
            cols.append(N1[k, p] * Nbeta + p)
            data.append(B[k, p])
            rows.append(k * Nbeta + p)
            cols.append(N2[k, p] * Nbeta + p)
            data.append(A[k, p])
    C = bsr_array((data, (rows, cols)), shape=(NOmega_out * Nbeta, NOmega_in * Nbeta))

    # Build matrices D_wave:
    D_wave = dia_array(
        (np.reshape(E, (-1,)), np.array([0])),
        shape=(NOmega_out * Nbeta, NOmega_out * Nbeta),
    )

    # Build sparse block diagonal array S
    data = np.tile(dbeta, NOmega_out * Nbeta)
    rows = np.repeat(np.arange(NOmega_out), Nbeta)
    cols = np.arange(NOmega_out * Nbeta)
    S = bsr_array((data, (rows, cols)), shape=(NOmega_out, NOmega_out * Nbeta))

    return Omega_in_fromout, C, D_wave, S
