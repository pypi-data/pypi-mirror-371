# -*- coding: utf-8 -*-
"""
Python implementation of various algorithms for sea state estimation 
using the **wave-buoy analogy** (WBA), i.e. using the wave-induced 
responses of ships considered as sailing wave buoys (SAWB).

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

import numpy as np
from scipy.integrate import trapezoid
from netsse.tools.misc_func import weighted_std

def specres(Rxy, TRF, freq, beta, opt=None):
    '''Computes an estimate of the sea state using the spectral-residual method
    from Brodtkorb et al. (2017) and Nielsen et al. (2018).

    The heave, roll, and pitch response cross-spectra are used as input.
    Using the motion transfer functions of the vessel, the wave spectrum is estimated 
    through iteration.
    
    .. warning::
        Long-crested wave conditions are assumed in this sea state estimation method.
        
    .. note::
        This Python code is based on a MATLAB/Simulink implementation by 
        Astrid H. Brodtkorb.
    
    Parameters
    ----------
    Rxy : array_like of shape (Nfreq,6)
        The complex-valued response spectra, given as in:
        ``Rxy = [heaveheave, rollroll, pitchpitch, heaveroll, heavepitch, rollpitch]``.
    TRF : array_like of shape (Nfreq,3*Nbeta)
        The transfer functions of the ship, in heave, roll, and pitch, concatenated 
        along the second axis as in:
        ``TRF = [heave_TF,roll_TF,pitch_TF]``

        .. note::
            The phase of the complex transfer functions is not important in this 
            implementation, and the amplitude alone can be provided without this affecting 
            the estimation results.
    freq : array_like of shape (Nfreq,) 
        The frequencies of the response spectra and the transfer functions (should 
        match).
    beta : array_like of shape (Nbeta,)
        The discretized heading angles [deg] at which the transfer functions
        are known.

        .. tip::
            For a port-starboard symmetric ship, directions from 0 deg to 180
            deg only can be considered to lower the computational cost.
    opt: dict, optional
        Optional parameters controlling the SSE calculation. Available options are:

        - 'maxiter' : int, or array_like of shape (6,)
            Maximum number of iterations (default: 50).
        - 'tolCoef' : float, or array_like of shape (6,)
            Tolerance coefficient (default: 0.1).
        - 'gainFact' : float, or array_like of shape (6,)
            Gain factor, as a fraction of the maximum gain value (default: 0.5).
        - 'weights' : float, or array_like of shape (6,)
            Weights given to each response in the calculation of the final spectrum estimate 
            (default: equal weight for each response, i.e. wij = 1/6).
        
        .. note::
            `array_like` entries of the dictionary can be input for a response-specific option. 
            In such case, the array elements must be provided in the same order as for the response 
            spectra.

    Returns
    -------
    S_wave : array_like of shape (Nfreq,) 
        The estimated 1-D wave spectrum.
    beta_est : float 
        The estimated relative wave heading [degrees].
    num_it : array_like of shape (6,) 
        The average number of iterations used per heading angle, for the individual 
        response pairs organised as:
        ``num_it = [it3, it4, it5, it34, it35, it45]``.

    References
    ----------
    1. Brodtkorb, A. H., Nielsen, U. D., & Sørensen, A. J. (2018). Online wave estimation 
       using vessel motion measurements. IFAC-PapersOnLine, 51(29), 244–249. 
       https://doi.org/10.1016/j.ifacol.2018.09.510 
    2. Brodtkorb, A. H., Nielsen, U. D., & Sørensen, A. J. (2018). Sea state estimation using 
       vessel response in dynamic positioning. Applied Ocean Research, 70, 76–86. 
       https://doi.org/10.1016/j.apor.2017.09.005 
    3. Nielsen, U. D., Brodtkorb, A. H., & Sørensen, A. J. (2018). A brute-force spectral approach 
       for wave estimation using measured vessel motions. Marine Structures, 60, 101–121. 
       https://doi.org/10.1016/j.marstruc.2018.03.011 
    4. Brodtkorb, A. H., & Nielsen, U. D. (2023). Automatic sea state estimation with online trust 
       measure based on ship response measurements. Control Engineering Practice, 130. 
       https://doi.org/10.1016/j.conengprac.2022.105375 

    Example
    -------
    >>> S_wave, beta_est, num_it = specres(Rxy, TRF, freq, beta, opt=None)
    '''
    ######
    #### Deciphering inputs
    ######
    
    beta_rad = np.radians(beta)
    Nbeta = np.shape(beta_rad)[0] #//2+1
    
    # Transfer functions:
    heave_TF = TRF[:,0:Nbeta]
    roll_TF = TRF[:,Nbeta:2*Nbeta]
    pitch_TF = TRF[:,2*Nbeta:3*Nbeta]
    
    # Using response cross-spectra amplitudes for iteration:
    heaveheave = np.abs(Rxy[:,0])
    rollroll = np.abs(Rxy[:,1])
    pitchpitch = np.abs(Rxy[:,2])
    heaveroll = np.abs(Rxy[:,3])
    heavepitch = np.abs(Rxy[:,4])
    rollpitch = np.abs(Rxy[:,5])
    # and imaginary part of response cross-spectra:
    I_heaveroll = np.imag(Rxy[:,3])
    I_heavepitch = np.imag(Rxy[:,4])
    

    ######
    #### Computing the upper bound on the gains hij
    ######

    max_heaveheave = np.amax(np.abs(np.square(heave_TF)))
    max_rollroll = np.amax(np.abs(np.square(roll_TF)))
    max_pitchpitch = np.amax(np.abs(np.square(pitch_TF)))
    max_heaveroll = np.amax(np.abs(heave_TF*roll_TF))
    max_heavepitch = np.amax(np.abs(heave_TF*pitch_TF))
    max_rollpitch = np.amax(np.abs(roll_TF*pitch_TF))
    max_h33 = 2/max_heaveheave
    max_h44 = 2/max_rollroll
    max_h55 = 2/max_pitchpitch
    max_h34 = 2/max_heaveroll
    max_h35 = 2/max_heavepitch
    max_h45 = 2/max_rollpitch


    ######
    #### Options
    ######

    maxiter = 50*np.ones((6,))
    tolcoef = 0.1*np.ones((6,))
    gainfact = 0.5*np.ones((6,))
    wij = 1/6*np.ones((6,))

    if opt==None:
        opt = []

    if 'maxiter' in opt:
        maxiter = opt['maxiter']
        if np.size(maxiter) == 1:
            maxiter = maxiter*np.ones((6,))

    if 'tolCoef' in opt:
        tolcoef = opt['tolCoef']
        if np.size(tolcoef) == 1:
            tolcoef = tolcoef*np.ones((6,))

    if 'gainFact' in opt:
        gainfact = opt['gainFact']
        if np.size(gainfact) == 1:
            gainfact = gainfact*np.ones((6,))

    if 'weights' in opt:
        wij = opt['weights']
        if np.size(wij) == 1:
            wij = wij*np.ones((6,))
        wij = wij/np.sum(wij)    


    ######
    #### Calculate tolerances
    ######

    e_33 = tolcoef[0]*np.max(heaveheave)
    e_44 = tolcoef[1]*np.max(rollroll)
    e_55 = tolcoef[2]*np.max(pitchpitch)
    e_34 = tolcoef[3]*np.max(heaveroll)
    e_35 = tolcoef[4]*np.max(heavepitch)
    e_45 = tolcoef[5]*np.max(rollpitch)
    

    ######
    #### Calculate the iteration gains
    ######

    h_33 = gainfact[0]*max_h33 # hij[0]
    h_44 = gainfact[0]*max_h44 # hij[1]
    h_55 = gainfact[0]*max_h55 # hij[2]
    h_34 = gainfact[0]*max_h34 # hij[3]
    h_35 = gainfact[0]*max_h35 # hij[4]
    h_45 = gainfact[0]*max_h45 # hij[5]
    

    ######
    #### Iteration procedure
    ##   Iterate to find estimates of the wave spectrum
    ####
    
    # Initialize
    Nfreq = np.shape(freq)[0]
    S_33_hat = np.zeros((Nfreq,Nbeta))
    R_33_hat = np.zeros((Nfreq,Nbeta))
    S_44_hat = np.zeros((Nfreq,Nbeta))
    R_44_hat = np.zeros((Nfreq,Nbeta))
    S_55_hat = np.zeros((Nfreq,Nbeta))
    R_55_hat = np.zeros((Nfreq,Nbeta))
    
    S_34_hat = np.zeros((Nfreq,Nbeta))
    R_34_hat = np.zeros((Nfreq,Nbeta))
    S_35_hat = np.zeros((Nfreq,Nbeta))
    R_35_hat = np.zeros((Nfreq,Nbeta))
    S_45_hat = np.zeros((Nfreq,Nbeta))
    R_45_hat = np.zeros((Nfreq,Nbeta))
    
    Est_fp = np.zeros((6,Nbeta))
    Est_Hs = np.zeros((6,Nbeta))
    resid = np.zeros((6,Nbeta))
    
    num_it = np.zeros((6,Nbeta))
    
    for jj in range(Nbeta):
           
        Phi_w2 = np.abs(heave_TF[:,jj]**2)
        Phi_phi2 = np.abs(roll_TF[:,jj]**2)
        Phi_theta2 = np.abs(pitch_TF[:,jj]**2)
        Phi_wphi = np.abs(heave_TF[:,jj]*np.conj(roll_TF[:,jj]))
        Phi_wtheta = np.abs(heave_TF[:,jj]*np.conj(pitch_TF[:,jj]))
        Phi_phitheta = np.abs(roll_TF[:,jj]*np.conj(pitch_TF[:,jj]))
        
        # Residuals:
        res_33 = heaveheave
        res_44 = rollroll
        res_55 = pitchpitch
        res_34 = heaveroll
        res_35 = heavepitch
        res_45 = rollpitch
        
        it3 = 0
        while np.sum(np.abs(res_33)) > e_33: # Heave-Heave
            R_33_hat[:,jj] = Phi_w2*S_33_hat[:,jj]
            res_33 = heaveheave - R_33_hat[:,jj]
            S_33_hat[:,jj] = S_33_hat[:,jj] + h_33*res_33
            it3 = it3 + 1
            if it3 >= maxiter[0]:
                break
#        print('it3 = ',it3)

        it4 = 0
        while np.sum(np.abs(res_44)) > e_44: # Roll-Roll
            R_44_hat[:,jj] = Phi_phi2*S_44_hat[:,jj]
            res_44 = rollroll - R_44_hat[:,jj]
            S_44_hat[:,jj] = S_44_hat[:,jj] + h_44*res_44
            it4 = it4 + 1
            if it4 >= maxiter[1]:
                break
#        print('it4 = ',it4)
        
        it5 = 0
        while np.sum(np.abs(res_55)) > e_55: # Pitch-Pitch
            R_55_hat[:,jj] = Phi_theta2*S_55_hat[:,jj]
            res_55 = pitchpitch - R_55_hat[:,jj]
            S_55_hat[:,jj] = S_55_hat[:,jj] + h_55*res_55
            it5 = it5 + 1
            if it5 >= maxiter[2]:
                break
#        print('it5 = ',it5)
        
        it34 = 0
        while np.sum(np.abs(res_34)) > e_34: # Heave-Roll
            R_34_hat[:,jj] = Phi_wphi*S_34_hat[:,jj]
            res_34 = heaveroll - R_34_hat[:,jj]
            S_34_hat[:,jj] = S_34_hat[:,jj] + h_34*res_34
            it34 = it34 + 1
            if it34 >= maxiter[3]:
                break
#        print('it34 = ',it34)    
        
        it35=0
        while np.sum(np.abs(res_35)) > e_35: # Heave-Pitch
            R_35_hat[:,jj] = Phi_wtheta*S_35_hat[:,jj]
            res_35 = heavepitch - R_35_hat[:,jj]
            S_35_hat[:,jj] = S_35_hat[:,jj] + h_35*res_35
            it35 = it35 + 1
            if it35 >= maxiter[4]:
                break
#        print('it35 = ',it35)
        
        it45=0
        while np.sum(np.abs(res_45)) > e_45: # Roll-Pitch
            R_45_hat[:,jj] = Phi_phitheta*S_45_hat[:,jj]
            res_45 = rollpitch - R_45_hat[:,jj]
            S_45_hat[:,jj] = S_45_hat[:,jj] + h_45*res_45
            it45 = it45 + 1
            if it45 >= maxiter[5]:
                break
#        print('it45 = ',it45)
        

        num_it[:,jj] = [it3,it4,it5,it34,it35,it45] # Number of iterations     
       
        # Calculate estimated sea state parameters
        # Hs, Tp, Direction
        
        # Peak frequencies, peak periods
        idx33 = np.argmax(S_33_hat[:,jj])
        idx44 = np.argmax(S_44_hat[:,jj])
        idx55 = np.argmax(S_55_hat[:,jj])
        idx34 = np.argmax(S_34_hat[:,jj])
        idx35 = np.argmax(S_35_hat[:,jj])
        idx45 = np.argmax(S_45_hat[:,jj])
        wave33_fp = freq[idx33]
        wave44_fp = freq[idx44]
        wave55_fp = freq[idx55]
        wave34_fp = freq[idx34]
        wave35_fp = freq[idx35]
        wave45_fp = freq[idx45]
    
        start = 1
        stop = Nfreq
        # Significant wave height
        m0_33 = trapezoid(S_33_hat[start:stop,jj],freq[start:stop])
        m0_44 = trapezoid(S_44_hat[start:stop,jj],freq[start:stop])
        m0_55 = trapezoid(S_55_hat[start:stop,jj],freq[start:stop])
        m0_34 = trapezoid(S_34_hat[start:stop,jj],freq[start:stop])
        m0_35 = trapezoid(S_35_hat[start:stop,jj],freq[start:stop])
        m0_45 = trapezoid(S_45_hat[start:stop,jj],freq[start:stop])
        Hs33 = 4*np.sqrt(np.abs(m0_33))
        Hs44 = 4*np.sqrt(np.abs(m0_44))
        Hs55 = 4*np.sqrt(np.abs(m0_55))
        Hs34 = 4*np.sqrt(np.abs(m0_34))
        Hs35 = 4*np.sqrt(np.abs(m0_35))
        Hs45 = 4*np.sqrt(np.abs(m0_45))
    
        Est_fp[:,jj] = [wave33_fp, wave44_fp, wave55_fp, wave34_fp, wave35_fp, wave45_fp]
        Est_Hs[:,jj] = [Hs33, Hs44, Hs55, Hs34, Hs35, Hs45]
        resid[:,jj] = [np.sum(np.abs(res_33)),np.sum(np.abs(res_44)),np.sum(np.abs(res_55)),\
                       np.sum(np.abs(res_34)),np.sum(np.abs(res_35)),np.sum(np.abs(res_45))]

    ######
    #### Find Direction based on cross-spectra
    ##   Nielsen et al. 2018, Brodtkorb et al. 2018 (CAMS)
    ####

    # S_ij = np.array([S_33_hat,S_44_hat,S_55_hat,S_34_hat,S_35_hat,S_45_hat])
    # meanvar_S = np.mean(np.var(S_ij,axis=0,ddof=1),axis=0)
    var_Hs = np.var(Est_Hs,axis=0,ddof=1)
    # COV_Hs = np.sqrt(np.var(Est_Hs,axis=0,ddof=1))/np.mean(Est_Hs,axis=0)
    # COV_fp = np.sqrt(np.var(Est_fp,axis=0,ddof=1))/np.mean(Est_fp,axis=0)

    # Direction estimate, in [0,180] deg
    alpha_idx = np.argmin(var_Hs)
    # alpha_idx_Hs = np.argmin(Var_Hs)
    # alpha_idx_fp = np.argmin(Var_fp)
    # if np.abs((np.pi-beta_rad[alpha_idx_fp])-beta_rad[alpha_idx_Hs]) < np.abs(beta_rad[alpha_idx_fp]-beta_rad[alpha_idx_Hs]):
    #     alpha_idx_fp = np.argmin(np.abs(beta_rad-(np.pi-beta_rad[alpha_idx_fp])))
    # alpha_idx = round((alpha_idx_Hs+alpha_idx_fp)/2)
    alpha = beta_rad[alpha_idx]
    
    # Use the imaginary part of the cross spectra heave/roll, roll/pitch pairs
    # to find port/starboard and correct estimate for head/following seas, if
    # nessesary
    
    # Compute largest peak of imaginary component
    # maxIDX34 = np.argmax(np.abs(I_heaveroll))
    # Peak34 = I_heaveroll[maxIDX34,]
    # maxIDX35 = np.argmax(np.abs(I_heavepitch))
    # Peak35 = I_heavepitch[maxIDX35]
    
    # Compute the variance of the imaginary component
    Int34 = trapezoid(I_heaveroll[start:stop,],freq[start:stop])
    Int35 = trapezoid(I_heavepitch[start:stop,],freq[start:stop])
    
    #print([np.sign(Peak34),np.sign(Int34),np.sign(Peak35),np.sign(Int35)])

    Est_dir = alpha # initialize direction estimate

    # Head/following
    if (Int35 < 0):  # Following
        if Est_dir > np.pi/2: # Direction estimate from min(varHs) needs correction
            Est_dir = np.pi - Est_dir
        # elif Est_dir < -np.pi/2: # Direction estimate from min(varHs) needs correction
        #     Est_dir = -np.pi - Est_dir
    elif (Int35 > 0): # Head
        if Est_dir < np.pi/2 and Est_dir>0: # Direction estimate from min(varHs) needs correction
            Est_dir = np.pi - Est_dir
        # elif Est_dir < 0 and Est_dir > -np.pi/2:
        #     Est_dir = -np.pi - Est_dir
    alpha_idx = np.argmin(np.abs(beta_rad-Est_dir))
        
    # Port/starboard
    if (Int34 > 0):  # Starboard: (Int34 > 0) used in APOR paper (based upon measured response of R/V Gunnerus) 
        Est_dir = -Est_dir
        if Est_dir == -np.pi:
            Est_dir = np.abs(Est_dir)
    

    ######
    #### Output the estimates
    ######
    
    beta_est = np.degrees(Est_dir) # Relative wave heading estimate [deg]
    
    # 1-D wave spectrum estimate:
    S_wave = np.dot(wij,np.array([S_33_hat[:,alpha_idx],S_44_hat[:,alpha_idx],S_55_hat[:,alpha_idx],\
                  S_34_hat[:,alpha_idx],S_35_hat[:,alpha_idx],S_45_hat[:,alpha_idx]]))
    
    num_it = np.mean(num_it,axis=1)

    resid = resid[:,alpha_idx]
    
    # hatR_3 = R_33_hat[:,alpha_idx]  # heave-heave
    # hatR_4 = R_44_hat[:,alpha_idx]  # roll-roll
    # hatR_5 = R_55_hat[:,alpha_idx]  # pitch-pitch
    # hatR_34 = R_34_hat[:,alpha_idx] # heave-roll
    # hatR_35 = R_35_hat[:,alpha_idx] # heave-pitch
    # hatR_45 = R_45_hat[:,alpha_idx] # roll-pitch
    
    # R_3 = heaveheave
    # R_4 = rollroll
    # R_5 = pitchpitch
    # R_34 = heaveroll
    # R_35 = heavepitch
    # R_45 = rollpitch
    
    # hatS_3 = S_33_hat[:,alpha_idx] 
    # hatS_4 = S_44_hat[:,alpha_idx]
    # hatS_5 = S_55_hat[:,alpha_idx]    
    
    # Hs_matrix = Est_Hs
    # Hs_variance = varHs
    
    return S_wave,beta_est,num_it # resid,hatS_3,hatS_4,hatS_5,Hs_matrix,Hs_variance


def genspecres(Rxy, Hxy, freq, beta, opt=None):
    '''Computes an estimate of the point wave spectrum using a generalised version of the 
    spectral-residual method from Brodtkorb et al. (2017) and Nielsen et al. (2018).

    The cross-spectra from any number of responses are used as input.
    Using the motion transfer functions of the vessel, the wave spectrum is estimated 
    through iteration.
    
    .. warning::
        Long-crested wave conditions are assumed in this sea state estimation method. The present 
        version of the algorithm does not allow to distinguish waves coming from port and starboard
        sides.

    
    Parameters
    ----------
    Rxy : array_like of shape (Nresp,Nfreq)
        The response cross-spectra.

        .. note::
            The phase of the complex-valued response spectra is not important in this 
            implementation, and the amplitude (absolute value) alone can be provided without this affecting the estimation results.
    Hxy : array_like of shape (Nresp,Nbeta,Nfreq)
        The RAO products for the ship, provided in the same order of response pairs as for the 
        response cross-spectra `Rxy`.

        .. note::
            The phase of the complex-valued transfer functions is not important in this 
            implementation, and the amplitude alone can be provided without this affecting 
            the estimation results.
    freq : array_like of shape (Nfreq,) 
        The frequencies of the response spectra and the transfer functions (should 
        match).
    beta : array_like of shape (Nbeta,)
        The discretized heading angles [deg] at which the transfer functions
        are known.

        .. tip::
            For a port-starboard symmetric ship, directions from 0 deg to 180
            deg only can be considered to lower the computational cost.
    opt: dict, optional
        Optional parameters controlling the SSE calculation. Available options are:

        - 'maxiter' : int, or array_like of shape (`Nresp`,)
            Maximum number of iterations (default: 50).
        - 'tolCoef' : float, or array_like of shape (`Nresp`,)
            Tolerance coefficient (default: 0.1).
        - 'gainFact' : float, or array_like of shape (`Nresp`,)
            Gain factor, as a fraction of the maximum gain value (default: 0.5).
        - 'weights' : float, or array_like of shape (`Nresp`,)
            Weights given to each response in the calculation of the final spectrum estimate 
            (default: equal weight for each response, i.e. wij = 1/`Nresp`).
        
        .. note::
            `array_like` entries of the dictionary can be input for a response-specific option. 
            In such case, the array elements must be provided in the same order as for the response 
            spectra.

    Returns
    -------
    S_wave : array_like of shape (Nfreq,)
        The estimated 1-D wave spectrum.
    beta_est : float
        The estimated relative wave heading [degrees].
    num_it : array_like of shape (Nresp,) 
        The average number of iterations used per heading angle, for the individual 
        response pairs.

    References
    ----------
    1. Brodtkorb, A. H., Nielsen, U. D., & Sørensen, A. J. (2018). Online wave estimation 
       using vessel motion measurements. IFAC-PapersOnLine, 51(29), 244–249. 
       https://doi.org/10.1016/j.ifacol.2018.09.510 
    2. Brodtkorb, A. H., Nielsen, U. D., & Sørensen, A. J. (2018). Sea state estimation using 
       vessel response in dynamic positioning. Applied Ocean Research, 70, 76–86. 
       https://doi.org/10.1016/j.apor.2017.09.005 
    3. Nielsen, U. D., Brodtkorb, A. H., & Sørensen, A. J. (2018). A brute-force spectral approach 
       for wave estimation using measured vessel motions. Marine Structures, 60, 101–121. 
       https://doi.org/10.1016/j.marstruc.2018.03.011 
    4. Brodtkorb, A. H., & Nielsen, U. D. (2023). Automatic sea state estimation with online trust 
       measure based on ship response measurements. Control Engineering Practice, 130. 
       https://doi.org/10.1016/j.conengprac.2022.105375 

    Example
    -------
    >>> S_wave, beta_est, num_it = genspecres(Rxy, Hxy, freq, beta, opt=None)
    '''
    ######
    #### Deciphering inputs
    ######
    
    beta_rad = np.radians(beta)
    Nbeta = np.shape(beta_rad)[0] #//2+1
    Nfreq = np.shape(freq)[0]
    
    # Transfer function amplitudes:
    Hxy_abs = np.abs(Hxy)
    
    # Using response cross-spectra amplitudes for iteration:
    Rxy_abs = np.abs(Rxy)
    Nresp = np.shape(Rxy_abs)[0]

    ######
    #### Computing the upper bound on the gains hij
    ######

    max_Hxy = np.amax(Hxy_abs,axis=(1,2))
    max_h_ij = 2/max_Hxy

    ######
    #### Options
    ######

    maxiter = 50*np.ones((Nresp,))
    tolcoef = 0.1*np.ones((Nresp,))
    gainfact = 0.5*np.ones((Nresp,))
    wij = 1/Nresp*np.ones((Nresp,1))

    if opt==None:
        opt = []

    if 'maxiter' in opt:
        maxiter = opt['maxiter']
        if np.size(maxiter) == 1:
            maxiter = maxiter*np.ones((Nresp,))

    if 'tolCoef' in opt:
        tolcoef = opt['tolCoef']
        if np.size(tolcoef) == 1:
            tolcoef = tolcoef*np.ones((Nresp,))

    if 'gainFact' in opt:
        gainfact = opt['gainFact']
        if np.size(gainfact) == 1:
            gainfact = gainfact*np.ones((Nresp,))

    if 'weights' in opt:
        wij = opt['weights']
        if np.size(wij) == 1:
            wij = wij*np.ones((Nresp,1))
        wij = np.reshape(wij/np.sum(wij),(Nresp,1))

    ######
    #### Calculate tolerances
    ######

    e_ij = tolcoef*np.max(Rxy_abs,axis=1)

    ######
    #### Calculate the iteration gains
    ######

    h_ij = gainfact*max_h_ij

    ######
    #### Iteration procedure
    ##   Iterate to find estimates of the wave spectrum
    ######
    
    # Initialize
    S_ij_hat = np.zeros((Nresp,Nbeta,Nfreq))
    R_ij_hat = np.zeros((Nresp,Nbeta,Nfreq))
    resid = np.zeros((Nresp,Nbeta))
    num_it = np.zeros((Nresp,Nbeta))

    for i_beta in range(Nbeta):
        for i_resp in range(Nresp):
        
            # Residuals:
            res_ij = Rxy_abs[i_resp,:]

            it_ij = 0                
            while np.sum(np.abs(res_ij)) > e_ij[i_resp,]:
                R_ij_hat[i_resp,i_beta,:] = Hxy_abs[i_resp,i_beta,:]*S_ij_hat[i_resp,i_beta,:]
                res_ij = Rxy_abs[i_resp,:] - R_ij_hat[i_resp,i_beta,:]
                S_ij_hat[i_resp,i_beta,:] += h_ij[i_resp,]*res_ij
                it_ij += 1
                if it_ij >= maxiter[i_resp,]:
                    break
            # print('iteration = ', it_ij)
        
            num_it[i_resp,i_beta] = it_ij # Number of iterations
            resid[i_resp,i_beta] = np.sum(np.abs(res_ij)) 

    ######  
    #### Calculate estimated sea state parameters
    ######

    # Peak frequencies:
    idx_ij = np.argmax(S_ij_hat,axis=2)
    Est_fp = freq[idx_ij]

    # Significant wave height:
    start = 1
    stop = Nfreq
    m0_ij = trapezoid(S_ij_hat[:,:,start:stop],freq[start:stop,],axis=2)
    Est_Hs = 4*np.sqrt(np.abs(m0_ij))

    ######
    #### Find direction based on cross-spectra
    ##   Nielsen et al. 2018, Brodtkorb et al. 2018 (CAMS)
    ####

    std_Hs = weighted_std(Est_Hs,wij,axis=0,ddof=1)
    # COV_Hs = np.sqrt(np.var(Est_Hs,axis=0,ddof=1))/np.mean(Est_Hs,axis=0)
    # COV_fp = np.sqrt(np.var(Est_fp,axis=0,ddof=1))/np.mean(Est_fp,axis=0)

    # Direction estimate, in [0,180] deg
    alpha_idx = np.argmin(std_Hs)
    # alpha_idx_Hs = np.argmin(Var_Hs)
    # alpha_idx_fp = np.argmin(Var_fp)
    # if np.abs((np.pi-beta_rad[alpha_idx_fp])-beta_rad[alpha_idx_Hs]) < np.abs(beta_rad[alpha_idx_fp]-beta_rad[alpha_idx_Hs]):
    #     alpha_idx_fp = np.argmin(np.abs(beta_rad-(np.pi-beta_rad[alpha_idx_fp])))
    # alpha_idx = round((alpha_idx_Hs+alpha_idx_fp)/2)
    alpha = beta_rad[alpha_idx]
    Est_dir = alpha # initialize direction estimate
    
    ######
    #### Output the estimates
    ######
    
    # Relative wave heading estimate [deg] (between 0-180 degrees):
    beta_est = np.degrees(Est_dir)
    
    # Point wave spectrum estimate:
    S_wave = np.sum(wij*S_ij_hat[:,alpha_idx,:],axis=0)
    
    # Number of iterations:
    num_it = np.mean(num_it,axis=1)

    # Residuals:
    resid = resid[:,alpha_idx]   
    
    # Hs_matrix = Est_Hs
    # Hs_variance = varHs
    
    return S_wave,beta_est,num_it # resid,Hs_matrix,Hs_variance