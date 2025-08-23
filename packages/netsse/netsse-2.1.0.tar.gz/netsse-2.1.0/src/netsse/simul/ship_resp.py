# -*- coding: utf-8 -*-
"""
Numerical simulation of **ship responses**.

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
from scipy.interpolate import interp1d, interp2d
from numpy.random import default_rng
from threading import Thread
import queue
from netsse.tools.misc_func import *

####
## Create the Multithread class for queueing processes
####

# Class
class MultiThread(Thread):
    def __init__(self, name):
        Thread.__init__(self)
        self.name = name

    def run(self):
        #print(f"\t [Starting {self.name}]")
        process_queue()
        #print(f"\t [Completed {self.name}]")

# Create the queue
fifo_queue = queue.Queue()


def simul_ship_resp(S2D,freq_wave,betas_wave,U=0,RespStr='Waves',max_threads=0,\
                    freq_TRF=[0,],betas_TRF=0,TRF_amps=0,TRF_phases=0,\
                    NoTs=10,fs=10,T=30*60,Nomega=500,AddNoise=False,snr=20):
    """Generates several time histories of the waves encountered by a ship and, 
    optionally, the wave-induced vessel motion responses (heave, roll, pitch).
     
    A 2D wave spectrum must be given as input. If ship response is to be simulated
    too, then the wave-to-motion transfer functions of the vessel must also be 
    provided.

    Parameters
    ----------
    S2D : array_like of shape (Nf_wave,Nmu)
        2-D wave spectrum characterizing the sea state [m^2.s.s/rad].
    freq_wave : array_like of shape (Nf_wave,)
        Vector of wave frequencies [Hz] in which the wave spectrum is expressed. 
    betas_wave : array_like of shape (Nmu,)
        Vector of the `relative` wave headings [deg] for the wave spectrum.

        .. note::
            The relative wave headings are defined as:
            0 deg: following sea; 90 deg: beam waves from port side; 
            180 deg: head sea; 270 deg: beam waves from starboard side.
    U : float, default 0
        Vessel speed [m/s].
    RespStr : {'Waves','Motions'}, optional
        Use ``'Motions'`` if vessel motions in waves are also to be simulated 
        (in addition to the waves). Otherwise, use ``'Waves'`` and only the wave 
        surface elevation will be simulated. The default is ``'Waves'``.
    max_threads : int, default 0
        Indicates to maximum number of threads to be used to parallelize the 
        execution. 
        
        .. attention::
            A large value for ``max_threads`` should only be used if the program 
            is run on a high-performance computer. The code execution risks 
            crashing otherwise.
    freq_TRF : array_like of shape (Nf_TRF,), default [0,]
        Vector of wave frequencies [Hz] in which the transfer functions are 
        expressed.
    betas_TRF : array_like of shape (Nbeta,), default 0
        Vector of the relative wave headings [deg] indicating the direction of 
        propagation of the energy (relative to vessel heading) for the transfer
        functions.
    TRF_amps : array_like of shape (Nf_TRF, Nbeta, 3), optional
        The amplitude of the transfer functions for heave, roll, and pitch, 
        respectively. The default is 0.
    TRF_phases : array_like of shape (Nf_TRF, Nbeta), optional
        The phase of the transfer functions for heave, roll, and pitch, 
        respectively. The default is 0.
    NoTs : int, default 10
        Number of time series to be generated.
    fs : float, default 10
        Sampling frequency [Hz] for the generated time histories.
    T : float, optional
        Duration [s] of the time histories. The default is 30*60 = 1800 s.
    Nomega : int, default 500
        Number of wave components used for each direction to generate the time 
        histories.

    Returns
    -------
    time : array_like of shape (T*fs,).
        Vector of time [s].
    wavet : array_like of shape (NoTs,T*fs).
        Wave elevation [m] time series.
    heavet, rollt, pitcht: array_like of shape (NoTs,T*fs).
        Heave, roll and pitch time series. 
        
        .. note::
            ``heavet``, ``rollt``, ``pitcht`` are returned if and only if 
            RespStr = ``'Motions'``

    Other Parameters
    ----------------
    AddNoise : bool, default False
        A boolean that indicates whether random noise (Gaussian white noise) 
        is added to be added the motion time histories.
    snr : float, default 20
        The signal-to-noise ratio to be used for addition of noise.

    See Also
    --------
    sum_components : Performs the summation of the sine components to 
        simulate in the time domain the encountered wave elevation or the wave-induced 
        responses on a ship.
                
    Example
    -------
    >>> # Wave simulations
    >>> time, wavet =
    ...     simul_ship_resp(S2D,freq_wave,betas_wave,U,'Waves',0,NoTs=10,fs=10,T=30*60,
    ...                     Nomega=500,AddNoise=True,snr=20)
    >>> # Motion simulations
    >>> time, wavet, heavet, rollt, pitcht =
    ...     simul_ship_resp(S2D,freq_wave,betas_wave,U,'Motions',0,freq_TRF,betas_TRF,
    ...                     TRF_amps,TRF_phases,NoTs,fs,T,Nomega,AddNoise=True,snr=20)
    """

    # Physical quantities:
    g = 9.81   # Gravitational acceleration [m/s^2]
    rho = 1025 # Density of sea water [kg/m^3]
    
    # Initialize the random number generator:
    rng = default_rng()
    
    # Non-equidistant frequency spacing:
    freq_low = np.max((freq_wave[0,],freq_TRF[0,]))
    freq_high = np.min((freq_wave[-1,],freq_TRF[-1]))
    freq = np.sort(rng.uniform(freq_low,freq_high,Nomega))
    # Ensure that the Nyquist frequency equals freq_high:
    #freq *= freq_high/freq[-1,]
    
    omega = freq*(2*np.pi)
    domega = np.hstack((omega[1:,]-omega[0:-1,],np.array(omega[-1,]-omega[-2,]))).reshape((-1,1))
    
    dmu = betas_wave[1,]-betas_wave[0,]
    Nmu = np.shape(betas_wave)[0]
  
    f_interp = interp1d(freq_wave,S2D,kind='linear',axis=0,assume_sorted=True)
    S2D_new = f_interp(freq)/(2*np.pi) # Directional wave spectrum as a function of omega
    wave_amp = np.sqrt(S2D_new*domega*dmu*np.pi/180)
    
    if RespStr == 'Motions':
        # Extract TRFs amplitude and interpolate them at new frequencies:
        TRF_amps_heave = TRF_amps[:,:,0]
        TRF_amps_roll = TRF_amps[:,:,1]
        TRF_amps_pitch = TRF_amps[:,:,2]
        f_heave_amps = interp2d(betas_TRF,freq_TRF,TRF_amps_heave,\
                                kind='linear',bounds_error=True)
        f_roll_amps = interp2d(betas_TRF,freq_TRF,TRF_amps_roll,\
                               kind='linear',bounds_error=True)
        f_pitch_amps = interp2d(betas_TRF,freq_TRF,TRF_amps_pitch,\
                                kind='linear',bounds_error=True)
        TRF_amps_heave_new = np.expand_dims(f_heave_amps(betas_wave,freq),axis=2)
        TRF_amps_roll_new = np.expand_dims(f_roll_amps(betas_wave,freq),axis=2)
        TRF_amps_pitch_new = np.expand_dims(f_pitch_amps(betas_wave,freq),axis=2)
        
        # Extract TRFs phase and interpolate them at new frequencies:
        if np.shape(TRF_phases) == ():
            TRF_phases = np.zeros(np.shape(TRF_amps))
        TRF_phases_heave = TRF_phases[:,:,0]
        TRF_phases_roll = TRF_phases[:,:,1]
        TRF_phases_pitch = TRF_phases[:,:,2]
        f_heave_phases = interp2d(betas_TRF,freq_TRF,TRF_phases_heave,\
                                  kind='linear',bounds_error=True)
        f_roll_phases = interp2d(betas_TRF,freq_TRF,TRF_phases_roll,\
                                 kind='linear',bounds_error=True)
        f_pitch_phases = interp2d(betas_TRF,freq_TRF,TRF_phases_pitch,\
                                  kind='linear',bounds_error=True)
        TRF_phases_heave_new = np.expand_dims(f_heave_phases(betas_wave,freq),axis=2)
        TRF_phases_roll_new = np.expand_dims(f_roll_phases(betas_wave,freq),axis=2)
        TRF_phases_pitch_new = np.expand_dims(f_pitch_phases(betas_wave,freq),axis=2)      
    
    time = np.arange(0,T,1/fs).reshape((1,1,-1))
    Nt = np.shape(time)[2]
    wavet = np.zeros((NoTs,Nt))
    heavet, rollt, pitcht = np.zeros((NoTs,Nt)),np.zeros((NoTs,Nt)),np.zeros((NoTs,Nt))
    
    # Standard normal distributed variables with mean = 0 and std = 1:
    V = rng.normal(0,1,size=(Nomega,Nmu,NoTs))
    W = rng.normal(0,1,size=(Nomega,Nmu,NoTs))
    epsilon = rng.uniform(0,2*np.pi,size=(Nomega,Nmu,NoTs))
    
    # Encounter frequencies
    omega = omega.reshape((-1,1,1))
    betas_wave = betas_wave.reshape((1,-1,1))
    om_enc = omega-omega**2*U/g*np.cos(np.radians(betas_wave))
    
    # Wave amplitudes
    aw = np.expand_dims(wave_amp,axis=2)  
    
    if max_threads==0:
        if NoTs==1: 
            print('Wave simulation started for one seed')
            wavet = sum_components(aw,V,W,epsilon,om_enc,time,0,\
                wavet,RespStr='Waves',AddNoise=False)
        else:
            for seed in range(NoTs):
                print('Simulation started for SEED %s'%(seed+1))
                # Random coefficients
                V_seed = np.expand_dims(V[:,:,seed],axis=2)
                W_seed = np.expand_dims(W[:,:,seed],axis=2)
                epsilon_seed = np.expand_dims(epsilon[:,:,seed],axis=2)
                
                wavet = sum_components(aw,V_seed,W_seed,\
                                            epsilon_seed,om_enc,time,seed,wavet)            
        
    else: # Use multi-threading         
    
        # Create a list of threads:
        threads = []
        
        for seed in range(NoTs):
            
            # Random coefficients
            V_seed = np.expand_dims(V[:,:,seed],axis=2)
            W_seed = np.expand_dims(W[:,:,seed],axis=2)
            epsilon_seed = np.expand_dims(epsilon[:,:,seed],axis=2)
            
            ####
            ## Start the threads
            ####    
            
            ####
            ## Build the queue with the input arguments to run one thread per 
            ## seed and per motion component
            ####
            
            # Arguments for computation of the wave elevation time series:
            args_wave = [aw,V_seed,W_seed,epsilon_seed,om_enc,time,seed,wavet]
            fifo_queue.put(args_wave)
            
            if RespStr == 'Motions':
                
                # Arguments for computation of the heave motion time series:
                args_heave = [aw,V_seed,W_seed,epsilon_seed,om_enc,time,seed,\
                              heavet,TRF_amps_heave_new,TRF_phases_heave_new,\
                              'Motions']
                fifo_queue.put(args_heave)
            
                # Arguments for computation of the roll motion time series:
                args_roll = [aw,V_seed,W_seed,epsilon_seed,om_enc,time,seed,\
                             rollt,TRF_amps_roll_new,TRF_phases_roll_new,\
                             'Motions']
                fifo_queue.put(args_roll)
                
                # Arguments for computation of the pitch motion time series:
                args_pitch = [aw,V_seed,W_seed,epsilon_seed,om_enc,time,seed,\
                              pitcht,TRF_amps_pitch_new,TRF_phases_pitch_new,\
                              'Motions']
                fifo_queue.put(args_pitch)
        
        for i in range(max_threads):
            process = MultiThread('Thread '+str(i+1))
            process.start()
            threads.append(process)
            
        # We now pause execution on the main thread by 'joining' all of our started threads.
        # This ensures that each has finished running.
        for process in threads:
            process.join()
        print('Simulation completed for ALL seeds and motion components')
        
    # At this point, results for each seed are now neatly stored in order in 
    # 'wavet', 'heavet', 'rollt' & 'pitcht'.    
    if RespStr == 'Motions':
        return   np.squeeze(time), wavet, heavet, rollt, pitcht
    return np.squeeze(time), wavet


def sum_components(aw,V_seed,W_seed,epsilon_seed,om_enc,time,seed,result,\
                   TRF_amps=0,TRF_phases=0,RespStr='Waves',AddNoise=False,snr=20):
    r"""Performs the summation of the sine components to simulate in the time domain 
    the encountered wave elevation or the wave-induced responses on a ship.

    Parameters
    ----------
    aw : array_like of shape (Nfreq,Nbeta,1)
        Amplitude of the wave components.
    V_seed, W_seed : array_like of shape (Nfreq,Nbeta,1)
        Standard normal distributed variables with mean 0 and std. 1.
    epsilon_seed : array_like of shape (Nfreq,Nbeta,1)
        Random phases [rad] of the wave components. Those are uniformly distributed 
        variables between 0 and :math:`2\pi`.
    om_enc : array_like of shape (Nfreq,1,1)
        Vector of encounter wave frequencies [rad/s].
    time : array_like of shape (1,1,Nt)
        Vector of time [s].
    seed : int
        Index of the seed number.
    result : array_like of shape (Nseed,Nt)
        Anterior value of the vector of wave/response sequence.

        .. note::
            Consult the documentation of the :func:`netsse.simul.ship_resp.simul_ship_resp` 
            function for information on the other parameters.

    Returns
    -------
    result : array_like of shape (Nseed,Nt)
        Updated value of the vector of wave/response sequence.

    See Also
    --------
    simul_ship_resp, process_queue
    """    
    # Sum wave components
    if RespStr == 'Waves':
        #print('Simulation started for SEED %s - Waves'%(seed+1))    
        result[seed,:] = np.sum(aw*(V_seed*np.cos(om_enc*time+epsilon_seed)\
                            -W_seed*np.sin(om_enc*time+epsilon_seed)),axis=(0,1))
                
    # Sum motion components
    if RespStr == 'Motions':
        #print('Simulation started for SEED %s - Motions'%(seed+1))    
        result[seed,:] = \
        np.sum(aw*TRF_amps*(V_seed*np.cos(om_enc*time+epsilon_seed+TRF_phases)\
                            -W_seed*np.sin(om_enc*time+epsilon_seed+TRF_phases)),axis=(0,1))
        
        if AddNoise:
            rng_noise = default_rng()
            Nt = np.shape(time)[2]
            
            sigma_motiont = np.std(result[seed,:])
            sigma_noise = sigma_motiont/np.sqrt(snr)
            noise = rng_noise.normal(0,sigma_noise,size=(Nt,))
            result[seed,:] += noise

    return result
    

def process_queue():
    """A function to process the FIFO queue.

    This basic function runs the function 
    :func:`netsse.simul.ship_resp.sum_components` with the queued arguments, 
    until the queue is empty, after which it signals that the task is completed.

    See Also
    --------
    MultiThread, sum_components
    """
    while not fifo_queue.empty():
        args_sum = fifo_queue.get(block=False)
        sum_components(*args_sum)
        fifo_queue.task_done()
    return