# -*- coding: utf-8 -*-
"""
Python implementation of the **EMEP** algorithm, used for analyzing
directional wave spectra from field data.

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
from scipy.integrate import trapezoid
import itertools


def norm_resp(Rxy_ReIm, TRF, S1D, f, mn=None, ReIm=None, Na=None, axy=None):
    """Normalizes the response spectra and transfer functions for application of the EMEP method.

    .. note::
        The normalization factors are found in Bendat & Piersol (2010).

    Parameters
    ----------
    Rxy_ReIm : array_like of shape (Nfreq,Nxy)
        Response spectra as a function of frequency ``f``, considering `Nxy` pairs of responses.
    TRF : Multidimensional array of shape (Nresp,Ntheta,Nfreq)
        Transfer functions for `Nresp` different responses, as functions of wave direction and frequency ``f``.
    S1D : array_like of shape (Nfreq,)
        1-D wave spectrum, as a function of frequency ``f``.
    f : array_like of shape (Nfreq,)
        Vector of wave frequencies.
    mn : array_like of shape (Nxy,2), optional
        Definition of the considered responses in ``Rxy_ReIm``. Elements in ``mn`` correspond to the indices of the pairs of
        responses along the first dimension of ``TRF``, i.e., from 0 to `Nresp`-1.
        Default is ``None``; in that case, the response pairs are ordered in the following order (illustrated for `Nresp = 3`):

        ``Rxy_ReIm = [Re(R00),Re(R11),Re(R22),Re(R01),Re(R02),Re(R12),Im(R01),Im(R02),Im(R12)]``

        ``mn = [[0, 0], [1, 1], [2, 2], [0, 1], [0, 2], [1, 2], [0, 1], [0, 2], [1, 2]]``
    ReIm : array_like of shape (Nxy,) or (Nxy,1), optional
        Vector indicating whether the real part (``'R'``) or imaginary part (``'I'``) of the response cross-spectrum is considered
        in ``Rxy_ReIm``.
        Default is ``None``; in that case, the real and imaginary parts of the response pairs are ordered in the order
        shown above, thus:

        ``ReIm = ['R', 'R', 'R', 'R', 'R', 'R', 'I', 'I', 'I']``
    Na : str, or array_like of shape (Nxy,), optional
        Number of the ensembled average for computation of the response spectra variance. Default is ``None``, for which case ``Na = 1``.
    axy : array_like of shape (Nxy,), optional
        Additional weights (must be positive). Any weight greater than zero increases the importance given to a corresponding pair of
        responses in the EMEP method. Default is ``None``, for which case the weights are set to zero.

    Returns
    -------
    Rxy_ReIm_n : array_like of shape (Nfreq,Nxy)
        Normalized version of the response spectra.
    Hn : array_like of shape (Ntheta,Nfreq,Nxy)
        Normalized version of the real and imaginary parts of the product of the transfer functions for pairs of responses.
        The real and imaginary parts for the pairs of responses are output in the same order as ``Rxy_ReIm``.

    See Also
    --------
    emep : Extended Maximum Entropy Principle (EMEP) method for reconstructing the directional spreading
        function based on the cross-power spectra of measured wave-induced responses.

    References
    ----------
    Bendat, J. S., & Piersol, A. G. (2010). Random Data: Analysis and Measurement Procedures. In Measurement Science and
    Technology (Vol. 11, Issue 12). Wiley. https://doi.org/10.1002/9781118032428

    Example
    -------
    >>> Rxy_ReIm_n, Hn = norm_resp(Rxy_ReIm,TRF,S1D,f,mn=None,ReIm=None,Na=None,axy=None)
    """
    Nxy = np.shape(Rxy_ReIm)[1]  # Number of considered response pairs
    Nfreq = np.shape(f)[0]  # Number of wave frequencies
    Ntheta = np.shape(TRF)[1]  # Number of wave directions

    Wmn = np.ones((Nfreq, Nxy))  # Weighting factor to normalise responses
    Swave = np.reshape(S1D, (Nfreq, 1))  # Point wave spectrum
    Hn = np.zeros((Ntheta, Nfreq, Nxy))  # Normalised transfer function products

    ## Optional arguments:
    Nresp = int(np.sqrt(Nxy))  # Number of considered responses

    if mn is None:  # Indicate the indices of considered response pairs
        mn = np.array(
            [[ix, ix] for ix in range(Nresp)]
            + [list(x) for x in itertools.combinations(range(Nresp), 2)] * 2
        )

    if ReIm is None:  # Indicates whether the real or the imaginary part is considered
        ReIm = np.array(["R"] * 2 * Nresp + ["I"] * Nresp).reshape((-1, 1))
    else:
        ReIm = np.reshape(ReIm, (-1, 1))

    if Na is None:  # Number of the ensembled average
        Na = np.ones((Nxy,))
    elif np.size(Na) == 1:
        Na = Na * np.ones((Nxy,))

    if axy is None:  # Additional weights
        axy = np.zeros((Nxy,))
    else:
        axy = np.abs(axy)

    ## Compute the weighting factors Wmn:
    for ixy in range(Nxy):
        mn_ixy = mn[ixy]
        index_xx_Re = np.where(
            np.all((mn == [mn_ixy[0], mn_ixy[0]]) * (ReIm == "R"), axis=1)
        )[0][0]
        index_yy_Re = np.where(
            np.all((mn == [mn_ixy[1], mn_ixy[1]]) * (ReIm == "R"), axis=1)
        )[0][0]

        if ReIm[ixy] == "R":  # Case 1: real part
            # Find the response index for the imaginary part for the corresponding pair:
            index_xy_Im = np.where(np.all((mn == mn_ixy) * (ReIm == "I"), axis=1))[0]
            if np.any(index_xy_Im):
                Rxy_Im = Rxy_ReIm[:, index_xy_Im[0]]
            else:
                Rxy_Im = np.zeros((Nfreq,))
            index_xy_Re = ixy

            # Weigthing factor value:
            Wmn[:, ixy] = np.sqrt(
                (
                    Rxy_ReIm[:, index_xx_Re] * Rxy_ReIm[:, index_yy_Re]
                    + np.square(Rxy_ReIm[:, index_xy_Re])
                    - np.square(Rxy_Im)
                )
                / (2 * (Na[ixy] + axy[ixy]))
            )

        elif ReIm[ixy] == "I":  # Case 2: imaginary part
            # Find the response index for the real part for the corresponding pair:
            index_xy_Re = np.where(np.all((mn == mn_ixy) * (ReIm == "R"), axis=1))[0]
            if np.any(index_xy_Re):
                Rxy_Re = Rxy_ReIm[:, index_xy_Re[0]]
            else:
                Rxy_Re = np.zeros((Nfreq,))
            index_xy_Im = ixy

            # Weigthing factor value:
            Wmn[:, ixy] = np.sqrt(
                (
                    Rxy_ReIm[:, index_xx_Re] * Rxy_ReIm[:, index_yy_Re]
                    - np.square(Rxy_Re)
                    + np.square(Rxy_ReIm[:, index_xy_Im])
                )
                / (2 * (Na[ixy] + axy[ixy]))
            )

    ## Normalise the response spectra:
    Rxy_ReIm_n = Rxy_ReIm / (Swave * Wmn)

    ## Normalise the transfer functions:
    for ixy in range(Nxy):
        mn_ixy = mn[ixy]
        if ReIm[ixy] == "R":
            Hn[:, :, ixy] = np.real(
                TRF[mn_ixy[0], :, :] * np.conj(TRF[mn_ixy[1], :, :])
            ) / np.expand_dims(Wmn[:, ixy], 0)
        if ReIm[ixy] == "I":
            Hn[:, :, ixy] = np.imag(
                TRF[mn_ixy[0], :, :] * np.conj(TRF[mn_ixy[1], :, :])
            ) / np.expand_dims(Wmn[:, ixy], 0)

    return Rxy_ReIm_n, Hn


def norm_DSF(D, theta):
    """Normalizes the directional spreading function.

    The function ensures that the output has a unit integral
    over wave directions.

    Parameters
    ----------
    D : array_like of shape (nt,nf)
        Directional spreading function.
    theta : array_like of shape (nt,)
        Vector of wave directions.

    Returns
    -------
    Dn : array_like of shape (nt,nf)
        Normalized spreading function.

    Example
    -------
    >>> Dn = norm_DSF(D, theta)
    """
    Dn = D

    # Repair corrupted values:
    ind = np.where((Dn < 0) + np.isnan(Dn))
    if np.any(ind):
        Dn[ind] = 0

    _, iy = np.where(Dn == np.inf)

    if np.any(iy):
        for iz in iy:
            ind0 = Dn[:, iz] < np.inf
            Dn[ind0, iz] = 0
            Dn[~ind0, iz] = 1

    # Normalize so that int D(theta, f) dtheta = 1 for each f
    Sf2 = np.trapezoid(Dn, theta, axis=0)

    k = np.where((Sf2 > np.sqrt(np.finfo(float).eps)) * (Sf2 < np.inf))[0]

    if np.any(k):
        Dn[:, k] = Dn[:, k] / Sf2[k]

    return Dn


def emep(Sxyn, Hn, theta, fi, k, opt=None):
    r"""Applies the Extended Maximum Entropy Principle (EMEP) method to reconstruct the directional
    spreading function based on the cross-power spectra of measured wave-induced responses.

    .. note::
        This implementation is based on the functions EMEP in the DIWASP toolbox and EMEM in the
        WAFO toolbox.

    Parameters
    ----------
    Sxyn : ndarray of shape (nf,m*m), where nf is the number of frequencies and m is the number of sensors
        Real and imaginary parts of the normalised cross-power spectral density:

        ``Sxyn(f,i) = Re(Smn(f)/(Szeta(f)*Wmn(f)))`` or the imaginary (``Im(.)``) counterpart.

    Hn : ndarray of shape (nt,nf,m*m), where nt is the number of theta values
        Matrix of the real and imaginary parts of the normalised RAO products, in the same
        order of response pairs as for ``Sxyn``:

        ``Hn(theta,f,i) = Re(Phi_m(theta,f)*conj(Phi_n(theta,f))/Wmn(f))``
        or the imaginary (``Im(.)``) counterpart.

    theta : ndarray of shape (nt,)
        Vector of wave headings.

        .. warning::
            The wave heading *must be* in a wrapped format, corresponding to [0,360] deg.
            For ship responses, those headings must be the *relative* wave headings.

    fi : ndarray of shape (nf,)
        Frequency vector.
    k : array_like
        List of indices corresponding to frequencies where the wave power spectral density
        is substantially greater than zero.
    opt : dict, optional
        Optional parameters controlling the EMEM calculation. Available options are:

        - 'errortol' : float, default 0.0005
            Error tolerance for convergence.
        - 'maxiter' : int, default 25
            Maximum number of iterations for the Newton-Raphson method.
        - 'relax' : float, default 1
            Relaxation parameter for controlling step shape in optimization.
        - 'maxcoef' : float, default 10000
            Maximum value for coefficients to prevent divergence.
        - 'coefabstol' : float, default 0.01
            Coefficient absolute tolerance for convergence.
        - 'minmodelorder' : int, default 1
            Minimum model order for AIC evaluation.
        - 'maxmodelorder' : int, default M/2 + 1
            Maximum model order for AIC evaluation.
        - 'diradjust' : float, default 0
            Deviation term to adjust the wave directions to other direction conventions.

            .. warning::
                For ship responses, a value of :math:`-\pi/2` was necessary to use:
                ``opt = {'diradjust': numpy.pi/2}``.

        - 'message' : {0,1}
            Display messages during the calculation.

    Returns
    -------
    D : ndarray
        Estimated directional spreading distribution matrix of shape (nt, nf).

    See Also
    --------
    norm_resp : Normalizes the response spectra and transfer functions.
    norm_DSF : Normalizes the directional spreading function.
    netsse.analys.buoy.Shannon_MEMII_Newton : Reconstructs the directional spreading function based
        on the first four Fourier coefficients of a directional wave spectrum.

    References
    ----------
    1. Hashimoto, N. (1997). "Analysis of the directional wave spectra from field data."
       Advances in Coastal and Ocean Engineering, Vol.3., pp.103-143.
    2. DIWASP, a directional wave spectra toolbox for MATLAB: User Manual.
       Research Report WP-1601-DJ (V1.1), Centre for Water Research, University of Western Australia.
    3. Brodtkorb, P.A., Johannesson, P., Lindgren, G., Rychlik, I., Rydén, J. and Sö, E. (2000).
       "WAFO - a Matlab toolbox for analysis of random waves and loads", Proc. 10th Int. Offshore and
       Polar Eng. Conf., Seattle, USA, Vol III, pp. 343-350.

    Example
    -------
    >>> D = emep(Sxyn, Hn, theta, fi, k, opt=None)
    """
    nt, nf, mm = Hn.shape

    H = np.zeros((mm, nt, nf))
    phi = np.zeros((mm, nf))

    # Eliminate meaningless equations such as those determined from the zero co-spectrum
    # and zero quadrature-spectrum.

    M = 0  # M is the number of independent equations

    dtheta = theta[1,] - theta[0,]
    tol = np.sqrt(np.finfo(float).eps)  # threshold defining zero for transfer functions

    for ii in range(mm):
        Htemp = Hn[:, :, ii]

        if np.any(np.any(np.abs(np.diff(Htemp, axis=0)) > tol * dtheta)):
            M += 1
            phi[M - 1, :] = Sxyn[:, ii]
            H[M - 1, :, :] = Htemp

        # for iy in range(ix, m):
        # Htemp = Gwt[ix, :, :] * np.conj(Gwt[iy, :, :])

        # if np.any(np.any(np.abs(np.diff(np.real(Htemp), axis=0)) > tol*dtheta)):
        #     M += 1
        #     phi[M-1, :] = np.real(Sxyn[ix, iy, :])
        #     H[M-1, :, :] = np.real(Htemp)

        # if np.any(np.any(np.abs(np.diff(np.imag(Htemp), axis=0)) > tol*dtheta)):
        #     M += 1
        #     phi[M-1, :] = np.imag(Sxyn[ix, iy, :])
        #     H[M-1, :, :] = np.imag(Htemp)

    # Note: H and Phi here are normalized as described in Hashimoto, N. (1997)
    H = H[:M, :, :]
    phi = phi[:M, :]

    if opt is None:
        opt = {}

    # Default values of the parameters controlling the calculations:
    errorTol = 0.0005  # Error tolerance for convergence
    maxIter = 25  # Maximum number of iterations
    Li = 1  # Relaxation parameter
    maxCoef = 10000  # Maximum value for coefficients
    coefAbsTol = 0.01  # Coefficient absolute tolerance
    coefAbsTol2 = 500  # See below*
    minModelOrder = 1  # Minimum model order for AIC evaluation
    maxModelOrder = M // 2 + 1  # Maximum model order for AIC evaluation
    AICTol = 0.1  # AIC tolerance
    dirAdjust = 0  # Directional deviation for adjustment
    display = 0
    # * 'coefAbsTol2' is a threshold value used to check whether the change in coefficients
    # during the Newton-Raphson iteration is within acceptable bounds.

    if "errortol" in opt:
        errorTol = opt["errortol"]
    if "maxiter" in opt:
        maxIter = opt["maxiter"]
    if "relax" in opt:
        Li = opt["relax"]
    if "maxcoef" in opt:
        maxCoef = opt["maxcoef"]
    if "coefabstol" in opt:
        coefAbsTol = opt["coefabstol"]
    if "minmodelorder" in opt:
        minModelOrder = opt["minmodelorder"]
    if "maxmodelorder" in opt:
        maxModelOrder = opt["maxmodelorder"]
    if "diradjust" in opt:
        dirAdjust = opt["diradjust"]
    if "message" in opt:
        display = opt["message"]

    if display > 0:
        print("Number of independent equations: ", M)

    cosn = np.cos(np.outer(np.arange(1, maxModelOrder + 1), theta + dirAdjust))
    sinn = np.sin(np.outer(np.arange(1, maxModelOrder + 1), theta + dirAdjust))
    cosnt = np.transpose(np.tile(cosn, (M, 1, 1)), (2, 0, 1))
    sinnt = np.transpose(np.tile(sinn, (M, 1, 1)), (2, 0, 1))

    AIC = np.zeros((maxModelOrder,))
    XY = np.zeros(
        (2 * maxModelOrder, M)
    )  # Matrix to store the negative Jacobian in the iteration
    coef = np.zeros((2 * maxModelOrder,))
    deltaCoef = np.zeros((2 * maxModelOrder,))
    Nbest = 0  # Best model order

    D = np.ones((nt, nf)) / (2 * np.pi)  # initialize DS

    for ff in k:
        Hj = H[:, :, ff].T  # H has shape (1:M,1:nt,1:nf)
        Phij = np.tile(phi[:, ff], (nt, 1))

        stop = 0

        localMinModelOrder = max(minModelOrder, int(np.ceil(Nbest / 2)))
        N = localMinModelOrder - 1

        coefOld = np.zeros((2 * N,))

        while not stop:
            N += 1

            coef[: 2 * N] = np.zeros((2 * N,))
            deltaCoef[: 2 * N] = np.zeros((2 * N,))

            count = 0
            lambda_ = Li
            modelFound = 0

            exponent = np.dot(coef[0:N], cosn[0:N, :]) + np.dot(
                coef[N : 2 * N], sinn[0:N, :]
            )
            a0 = -np.max(exponent)
            Fn = np.exp(a0 + exponent)
            Dn = np.tile(
                Fn.reshape((-1, 1)) / (trapezoid(Fn) * dtheta), (1, M)
            )  # Fn(theta|f)/norm(Fn)=Dn(theta|f)
            PhiHD = (Phij - Hj) * Dn
            Z = trapezoid(PhiHD, axis=0) * dtheta  # Z has shape (M,)
            error1 = np.max(np.abs(Z))

            while not (stop or modelFound):
                count += 1

                for ix in range(N):
                    XY[ix, :] = (
                        Z * trapezoid(Dn * cosnt[:, :, ix], axis=0)
                        - trapezoid(PhiHD * cosnt[:, :, ix], axis=0)
                    ) * dtheta
                    XY[N + ix, :] = (
                        Z * trapezoid(Dn * sinnt[:, :, ix], axis=0)
                        - trapezoid(PhiHD * sinnt[:, :, ix], axis=0)
                    ) * dtheta

                deltaCoefOld = deltaCoef[0 : 2 * N]

                # Perform the least-square method for sum((Z - deltacoef.T @ XY)**2):
                deltaCoef[0 : 2 * N] = np.linalg.lstsq(
                    XY[0 : 2 * N, :].T, Z, rcond=None
                )[0]
                coef[0 : 2 * N] = coef[0 : 2 * N] + lambda_ * deltaCoef[0 : 2 * N]

                if maxCoef < np.inf:
                    k0 = np.where(np.abs(coef[0 : 2 * N]) > maxCoef)[0]
                    if len(k0) > 0:
                        deltaCoef[k0] = (
                            np.sign(deltaCoef[k0]) * maxCoef
                            - (coef[k0] - lambda_ * deltaCoef[k0])
                        ) / lambda_
                        coef[k0] = np.sign(coef[k0]) * maxCoef

                exponent = np.dot(coef[0:N], cosn[0:N, :]) + np.dot(
                    coef[N : 2 * N], sinn[0:N, :]
                )
                a0 = -np.max(exponent)  # Trick in order to avoid infinities
                Fn = np.exp(a0 + exponent)
                Dn = np.tile(Fn.reshape((-1, 1)) / (trapezoid(Fn) * dtheta), (1, M))
                PhiHD = (Phij - Hj) * Dn
                Z = trapezoid(PhiHD, axis=0) * dtheta
                error2 = error1
                error1 = np.max(np.abs(Z))

                if np.all(np.abs(deltaCoef[0 : 2 * N]) < coefAbsTol) or (
                    error1 <= errorTol
                ):
                    modelFound = 1
                    if display > 0:
                        print("Model found.")

                elif count > maxIter or (
                    (error2 < error1)
                    and (
                        np.any(np.abs(deltaCoef[: 2 * N] - deltaCoefOld) > coefAbsTol2)
                    )
                ):
                    if lambda_ > Li * 2 ** (-4):
                        lambda_ = lambda_ * 0.5

                        if display > 0:
                            print(
                                "Coefficient divergence detected. Relaxing to lamdba_= %.3f"
                                % lambda_
                            )

                        count = 0
                        deltaCoef[0 : 2 * N] = 0
                        coef[: 2 * N] = np.zeros(
                            (2 * N,)
                        )  # np.concatenate((coefOld[:(N-1)],np.array([0]),coefOld[(N-1):2*(N-1)],np.array([0])))
                        Dn = np.tile(1 / (2 * np.pi), (nt, M))
                        PhiHD = (Phij - Hj) * Dn
                        Z = trapezoid(PhiHD, axis=0) * dtheta
                        error2 = np.inf
                        error1 = np.max(np.abs(Z))
                    else:
                        stop = 1
                        if display > 0:
                            print("Model not found.")

                if 0:  # modelFound
                    Np = 4
                    # subplot(Np,1,1), semilogy(abs(Z)+eps,'*'),hline(errorTol), title('error')
                    # subplot(Np,1,2),plot(deltaCoef(1:2*N),'g*'), title('deltaCoef')
                    # subplot(Np,1,3), plot(coef(1:2*N),'r*'), title('coef')
                    # subplot(Np,1,4), plot(theta,Dn)
                    # drawnow,
                    # disp('Hit any key'),pause

            AIC[N - 1] = M * (np.log(2 * np.pi * np.var(Z)) + 1) + 4 * N + 2

            if N > localMinModelOrder:
                stop = stop or (AIC[N - 1] + AICTol > AIC[N - 2])

            if np.isnan(AIC[N - 1]):
                stop = 1

            if stop:
                if N > localMinModelOrder:
                    Nbest = N - 1
                    coef[0 : 2 * Nbest] = coefOld
                else:
                    Nbest = 1
                    coef[0 : 2 * Nbest] = np.zeros((2 * Nbest,))
            else:
                Nbest = N
                stop = N >= maxModelOrder
                coefOld = coef[0 : 2 * N]

        if display > 0:
            print(
                f"f = {fi[ff]} \t \t Model order = {Nbest} \t \t error = {np.max(np.abs(Z))}"
            )

        exponent = np.dot(coef[0:Nbest], cosn[0:Nbest, :]) + np.dot(
            coef[Nbest : 2 * Nbest], sinn[0:Nbest, :]
        )
        a0 = -np.max(exponent)  # Trick in order to avoid infinities
        D[:, ff] = np.exp(a0 + exponent)

    D = norm_DSF(D, theta)

    if np.all(np.abs(D.flatten() - D[0, 0]) < np.sqrt(np.finfo(float).eps)):
        print("No main direction found. Check the estimated spectrum!")

    return D
