# -*- coding: utf-8 -*-
""" **Class definitions** for the NetSSE software.

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

from datetime import datetime
import numpy as np
from scipy.signal import csd
import netsse.tools.misc_func
import netsse.model.envir_cond

class Network:
    """Class for network definition."""

    def __init__(self,name:str=None,nature:str='undefined',platforms:list=[]):
        """Initialises the network.

        Parameters
        ----------
        name : str, optional
            Network name. By default, the name string is generated randomly
            in the format ``NetworkXXXX``.
        nature : str, default 'undefined'
            Network nature.
        platforms : list, default []
            List of platforms (as `Platform` instances).

        See Also
        --------
        Platform

        Example
        -------
        >>> plaform1 = netsse.base.Platform()
        >>> network = netsse.base.Network(platforms=[plaform1])
        """
        if name==None:
            name = 'Network'+netsse.tools.misc_func.id_generator(size=4)
        self.name = name
        self.nature = nature
        self.platforms = platforms
    
    def add_platform(self,*args,ignore_msg:bool=False):
        """Add a `Platform` instance to the list of platforms in the network.

        Parameters
        ----------
        *args: Platform object
            Platform to be added to the network.
        ignore_msg : bool, default False
            If `False`, messages are printed to inform about any changes made to the network.
            If `True`, thoses messages are turned off.

        Example
        -------
        >>> plaform2 = netsse.base.Platform()
        >>> network.add_platform(platform2,ignore_msg=True)
        """    
        for arg in args:
            arg_class = type(arg).__name__
            if not arg_class=='Platform':
                if not ignore_msg:
                    print('Argument type is invalid.')

            existing_platform = False
            if self.platforms:
                for i_platform, platform in enumerate(self.platforms):
                    if platform.name == arg.name:
                        existing_platform = True
                        existing_platform_index = i_platform

            if existing_platform:
                self.platforms[existing_platform_index] = arg
                if not ignore_msg:
                    print("Platform '%s' in %s was updated with new information."%(arg.name,self.name))

            else:
                self.platforms.append(arg)
                if not ignore_msg:
                    print("Platform '%s' was added to the network."%arg.name)

    def remove_platform(self,*args,ignore_msg:bool=False):
        """Remove a `Platform` instance from the list of platforms in the network.

        Parameters
        ----------
        *args: Platform object or str
            Platform to be removed from the network. Identified by the corresponding 
            name or `Platform` instance.
        ignore_msg : bool, default False
            If `False`, messages are printed to inform about any changes made to the network.
            If `True`, thoses messages are turned off.

        Example
        -------
        >>> network.remove_platform(platform1,ignore_msg=True)
        """
        for arg in args:
            platform_found = False

            arg_class = type(arg).__name__
            match arg_class:
                case 'str':
                    arg_name = arg
                case 'Platform':
                    arg_name = arg.name
                case _ :
                    if not ignore_msg:
                        print('Platform cannot be identified')
                        platform_found = True

            if self.platforms:
                for platform in self.platforms:
                    if not platform_found:
                        if platform.name == arg_name:
                            self.platforms.remove(platform)
                            platform_found = True
                            if not ignore_msg:
                                print("Platform '%s' was removed from %s."%(arg_name,self.name))

            if not platform_found:
                if not ignore_msg:
                            print("Platform '%s' not found."%arg_name)


class Platform:
    """Class for platform definition."""

    def __init__(self,name:str=None,owner:str='undefined',operations:list=[],\
                 seastate_collections:list=[]):
        """Initialises the platform.

        Parameters
        ----------
        name : str, optional
            Name of the platform. By default, the name string is generated randomly
            in the format ``PlatformXXXXX``.
        owner : str, default 'undefined'
            Platform owner. 
        operations : list, default []
            List of operations.
        seastate_collections : list, default []
            List of sea state collections (as `SeaStateCollec` instances).

        See Also
        --------
        Network
        Operation, SeaStateCollec
        Vessel, Buoy, WaveRadar

        Example
        -------
        >>> operation1 = netsse.base.Operation()
        >>> seastatecollec1 = netsse.base.SeaStateCollec()
        >>> platform1 = netsse.base.Platform(name='MyPlatform',owner='SomeCompany',\
        ...                                  operations=[operation1],\
        ...                                  seastate_collections=[seastatecollec1])
        """
        if name==None:
            name = 'Platform'+netsse.tools.misc_func.id_generator(size=5)
        self.name = name
        self.owner = owner
        self.operations = operations
        self.seastate_collections = seastate_collections            

    def add_operation(self,*args,ignore_msg:bool=False):
        """Add an `Operation` instance to the list of operations of the platform.

        Parameters
        ----------
        *args: Operation object
            Operation to be added to the platform.
        ignore_msg : bool, default False
            If `False`, messages are printed to inform about any changes made to the 
            platform. If `True`, thoses messages are turned off.

        Example
        -------
        >>> operation2 = netsse.base.Operation()
        >>> platform1.add_operation(operation2,ignore_msg=True)
        """
        for arg in args:
            arg_class = type(arg).__name__
            if not arg_class=='Operation':
                if not ignore_msg:
                    print('Argument type is invalid.')

            existing_operation = False
            if self.operations:
                for i_operation, operation in enumerate(self.operations):
                    if operation.id == arg.id:
                        existing_operation = True
                        existing_operation_index = i_operation

            if existing_operation:
                self.operations[existing_operation_index] = arg
                if not ignore_msg:
                    print("Operation '%s' of %s was updated with new information."%(arg.id,self.name))

            else:
                self.operations.append(arg)
                if not ignore_msg:
                    print("Operation '%s' was added to %s."%(arg.id,self.name))

    def remove_operation(self,*args,ignore_msg:bool=False):
        """Remove an existing `Operation` instance from the list of operations of the 
        platform.

        Parameters
        ----------
        *args: Operation object or str
            Operation to be removed from the network. Identified by the corresponding 
            identifier or `Operation` instance.
        ignore_msg : bool, default False
            If `False`, messages are printed to inform about any changes made to the 
            platform. If `True`, thoses messages are turned off.

        Example
        -------
        >>> platform1.remove_operation(platform1,ignore_msg=True)
        """
        for arg in args:
            operation_found = False

            arg_class = type(arg).__name__
            match arg_class:
                case 'str':
                    arg_id = arg
                case 'Operation':
                    arg_id = arg.id
                case _ :
                    if not ignore_msg:
                        print('Operation cannot be identified.')
                        operation_found = True

            if self.operations:
                for operation in self.operations:
                    if not operation_found:
                        if operation.id == arg_id:
                            self.operations.remove(operation)
                            if not ignore_msg:
                                print("Operation '%s' was removed from the list."%arg_id)

            if not operation_found:
                if not ignore_msg:
                    print("Operation '%s' not found."%arg_id)

    def add_seastatecollec(self,*args,ignore_msg:bool=False):
        """Add a `SeaStateCollec` instance to the list of sea state collections 
        of the platform.

        Parameters
        ----------
        *args: SeaStateCollec object
            Collections to be added to the platform.
        ignore_msg : bool, default False
            If `False`, messages are printed to inform about any changes made to
            the platform. If `True`, thoses messages are turned off.

        Example
        -------
        >>> seastatecollec2 = netsse.base.SeaStateCollec()
        >>> platform1.add_seastatecollec(seastatecollec2,ignore_msg=True)
        """
        for arg in args:
            arg_class = type(arg).__name__
            if not arg_class=='SeaStateCollec':
                if not ignore_msg:
                    print('Argument type is invalid.')

            existing_collec = False
            if self.seastate_collections:
                for i_collec, collec in enumerate(self.seastate_collections):
                    if collec.id == arg.id:
                        existing_collec = True
                        existing_collec_index = i_collec

            if existing_collec:
                self.seastate_collections[existing_collec_index] = arg
                if not ignore_msg:
                    print("Collection '%s' of %s was updated with new information."%(arg.id,self.name))

            else:
                self.seastate_collections.append(arg)
                if not ignore_msg:
                    print("Collection '%s' was added to %s."%(arg.id,self.name))

    def remove_seastatecollec(self,*args,ignore_msg:bool=False):
        """Remove an existing `SeaStateCollec` instance from the list of sea state collections
        of the platform.

        Parameters
        ----------
        *args: SeaStateCollec object or str
            Collections to be removed from the network. Identified by the corresponding 
            identifier or `SeaStateCollec` instance.
        ignore_msg : bool, default False
            If `False`, messages are printed to inform about any changes made to the 
            platform. If `True`, thoses messages are turned off.

        Example
        -------
        >>> platform1.remove_seastatecollec(seastatecollec1,ignore_msg=True)
        """
        for arg in args:
            collec_found = False

            arg_class = type(arg).__name__
            match arg_class:
                case 'str':
                    arg_id = arg
                case 'SeaStateCollec':
                    arg_id = arg.id
                case _ :
                    if not ignore_msg:
                        print('Collection cannot be identified.')
                        collec_found = True

            if self.seastate_collections:
                for collec in self.seastate_collections:
                    if not collec_found:
                        if collec.id == arg_id:
                            self.seastate_collections.remove(collec)
                            if not ignore_msg:
                                print("Collection '%s' was removed from the list."%arg_id)

            if not collec_found:
                if not ignore_msg:
                    print("Collection '%s' not found."%arg_id)


class Collection:
    """Class for collection definition."""

    def __init__(self,area:str='undefined',nature:str='undefined',origin='undefined',\
                 datetime_start=datetime.now(),datetime_end=datetime.now(),\
                 lat_min:float=0,lat_max:float=0,lon_min:float=0,lon_max:float=0):
        """Initialises the data collection.

        Parameters
        ----------
        area : str, default 'undefined'
            Area of data collection.
        nature : str, default 'undefined'
            Nature of the data collection.
        origin : str or object, default 'undefined'
            Origin or source of the data collection.
        datetime_start, datetime_end : datetime object, default datetime.now()
            Time coverage of the data collection.
        lat_min, lat_max : float, default 0
            Latitude [deg North] at the southern/northern edge of the geographical 
            domain covered by the data collection.
        lon_min, lon_max : float, default 0
            Longitude [deg East] at the western/eastern edge of the geographical 
            domain covered by the data collection.

        See Also
        --------
        Operation, SeaStateCollec

        Example
        -------
        >>> collec1 = netsse.base.Collection()
        """
        self.area = area
        self.nature = nature
        self.origin = origin
        self.datetime_start = datetime_start
        self.datetime_end = datetime_end
        self.lat_min = lat_min
        self.lat_max = lat_max
        self.lon_min = lon_min
        self.lon_max = lon_max


class Operation:
    """Class for operation definition."""

    def __init__(self,id:str=None,area:str='undefined',nature:str='undefined',\
                 origin='undefined',datetime_start=datetime.now(),datetime_end=datetime.now(),\
                 lat_min:float=0,lat_max:float=0,lon_min:float=0,lon_max:float=0,\
                 segments:list=[]):
        """Initialises the operation.

        Parameters
        ----------
        id : str, optional
            Operation identifier. By default, the id string is generated randomly
            in the format ``OperXXXXX``.
        segments : list, default []
            List of segments (as `Segment` instances) gathered during the operation.

            .. note::
                Consult :func:`netsse.base.Collection.__init__` for information on 
                the other parameters.

        See Also
        --------
        Collection
        Platform
        Segment

        Example
        -------
        >>> operation1 = netsse.base.Operation()
        """
        if id==None:
            id = 'Oper'+netsse.tools.misc_func.id_generator(size=5)
        self.id = id
        Collection.__init__(self,area,nature,origin,datetime_start,datetime_end,\
                            lat_min,lat_max,lon_min,lon_max)
        self.segments = segments


class SeaStateCollec:
    """Class for defining collections of sea states."""

    def __init__(self,id:str=None,area:str='undefined',nature:str='undefined',\
                origin='undefined',datetime_start=datetime.now(),datetime_end=datetime.now(),\
                lat_min:float=0,lat_max:float=0,lon_min:float=0,lon_max:float=0,\
                seastates:list=[]):
        """Initialises the sea state collection.

        Parameters
        ----------
        id : str, optional
            Data collection identifier. By default, the `id` string is generated
            randomly in the format ``CollecXXXXX``.
        seastates : list, default []
            List of sea states (as `SeaState` instances) gathered in the data 
            collection.
            
            .. note::
                Consult :func:`netsse.base.Collection.__init__` for information on 
                the other parameters.

        See Also
        --------
        Collection
        Platform
        SeaState

        Example
        -------
        >>> seastatecollec1 = netsse.base.SeaStateCollec()
        """
        if id==None:
            id = 'Collec'+netsse.tools.misc_func.id_generator(size=5)
        self.id = id
        Collection.__init__(self,area,nature,origin,datetime_start,datetime_end,\
                            lat_min,lat_max,lon_min,lon_max)
        self.seastates = seastates
        

class SeaState:
    """Class for sea state definitions.

    A sea state is a chacterisation of the ocean wave system at a given time 
    and position (Mounet, 2023).

    See Also
    --------
    WaveSequence, WaveSpectrum

    References
    ----------
    Mounet, R.E.G. (2023). Sea State Estimation Based on Measurements from 
    Multiple Observation Platforms. PhD Thesis. Technical University of Denmark. 
    https://orbit.dtu.dk/en/publications/sea-state-estimation-based-on-measurements-from-multiple-observat
    """

    def __init__(self,Hs=0,Tp=0,timestamp=datetime.now(),lat=0,lon=0,depth=0,duration=30*60):
        """Initialises the sea state at a given time and geographical position in the ocean.

        Parameters
        ----------
        Hs : float, default 0
            Significant wave height [m].
        Tp : float, default 0
            Peak wave period [s].
        timestamp : datetime object, default datetime.now()
            Timestamp at which the sea state applies.
        lat : float, default 0
            Latitude [degrees North].
        lon : float, default 0
            Longitude [degrees East].
        depth : float, default 0
            Water depth [m] at the studied location.
        duration : float, optional
            Time duration of the sea state [s], by default 30*60 = 1800 s.

        Examples
        --------
        >>> seastate = SeaState(Hs,Tp,timestamp,lat,lon,depth,duration)
        """
        self.set_params(Hs,Tp)
        self.timestamp = timestamp
        self.lat = lat
        self.lon = lon
        self.depth = depth
        self.duration = duration

    def set_params(self,Hs,Tp):
        """Sets the sea state parameters :math:`H_s` and :math:`T_p` to new
        user-defined values.

        Parameters
        ----------
        Hs : float
            Significant wave height [m].
        Tp : float
            Peak wave period [s].

        Examples
        --------
        >>> seastate.set_params(Hs,Tp)
        """
        self.Hs = Hs
        self.Tp = Tp


class WaveSequence(SeaState):
    """Class for wave sequence definitions.

    See Also
    --------
    SeaState, WaveSpectrum 
    """

    def __init__(self,Hs=0,Tp=0,timestamp=datetime.now(),lat=0,lon=0,depth=0,\
                 wave=None,time=None,fs=10):
        """Initialises the wave sequence.

        Parameters
        ----------
        wave : array-like of shape (Nt,), optional
            Sea surface elevation time-series [m]. By default ``None``.
        time : array-like of shape (Nt,), optional
            Vector of time [s], by default ``None``.
        
        Other parameters
        ----------------
        fs : float, default 10
            Sampling frequency [Hz].

            .. note::
                Consult :func:`netsse.base.SeaState.__init__` for information on the other
                parameters.

        Raises
        ------
        ValueError
            In case the input ``time`` and ``wave`` vectors do not have the same length.

        Examples
        --------
        >>> waveseq =
        ...     WaveSequence(Hs, Tp, timestamp, lat, lon, depth, wave, time)
        """
        super().__init__(Hs,Tp,timestamp,lat,lon,depth)

        if wave!=None:
            self.wave = wave
            self.Nt = np.shape(wave)[0]

            if time==None:
                dt = 1/fs
                self.time = np.linspace(0,(self.Nt-1)*dt,self.Nt)
            else:
                if np.shape(time)[0]!=self.Nt:
                    raise ValueError(f"The input time and wave should have the same length.")        
                
        else:
            if time==None:
                dt = 1/fs
                self.time = np.arange(0,self.duration+dt,dt)

            self.Nt = np.shape(self.time)[0]

        dt = np.mean(self.time[1:,]-self.time[:-1,])
        self.fs = 1/dt
        self.duration = self.time[-1,]-self.time[0,]

    def get_wavespec(self,method='Welch',nperseg=2**8,fmax=0):
        
        wavespec = WaveSpectrum(Hs=self.Hs,Tp=self.Tp,timestamp=self.timestamp,\
                                lat=self.lat,lon=self.lon,depth=self.depth,duration=self.duration)
        
        return wavespec.set_from_waveseq(self,method='Welch',nperseg=2**8,fmax=0)


class Spectrum:

    def __init__(self,freq=np.linspace(0,1,100),ord=np.zeros((100,)),unit_freq='Hz'):
        
        accepted_values_unit_freq = ['Hz','rad/s']
        if unit_freq not in accepted_values_unit_freq:
            raise ValueError(f"Invalid input unit_freq. Accepted values are: {', '.join(accepted_values_unit_freq)}")

        match unit_freq:
            case 'Hz':
                self.f = freq
                self.Sf = ord
                self.om = (2*np.pi)*freq
                self.Som = ord/(2*np.pi)

            case 'rad/s':
                self.f = freq/(2*np.pi)
                self.Sf = (2*np.pi)*ord
                self.om = freq
                self.Som = ord


class WaveSpectrum(Spectrum,SeaState):

    def __init__(self,Hs=np.nan,Tp=np.nan,freq=np.linspace(0,1,100),ord=np.zeros((100,)),\
                 unit_freq='Hz',timestamp=datetime.now(),lat=0,lon=0,depth=0,duration=30*60):
        
        SeaState.__init__(self,Hs,Tp,timestamp,lat,lon,depth,duration)
        Spectrum.__init__(self,freq,ord,unit_freq)
        

    def set_from_standard(self,method='JONSWAP',gamma=3.3):

        accepted_values_method = ['JONSWAP','PM','TMA']
        if method not in accepted_values_method:
            raise ValueError(f"Invalid input method. Accepted values are: {', '.join(accepted_values_method)}")
        
        self.nature = 'standard'
        self.method = method

        self.gamma = gamma

        match method:

            case 'JONSWAP':                    
                S_J = netsse.model.envir_cond.JONSWAP_DNV(self.Tp,self.Hs,self.om[self.om>0,],self.gamma)
            
            case 'PM':
                self.gamma = 1
                S_J = netsse.model.envir_cond.JONSWAP_DNV(self.Tp,self.Hs,self.om[self.om>0,],self.gamma)

            case 'TMA':
                if self.depth<=0:
                    raise ValueError(f"Invalid water depth. For a TMA spectrum, depth should have been specified\
                                      with a positive value.")
                S_J = netsse.model.envir_cond.JONSWAP_DNV(self.Tp,self.Hs,self.om[self.om>0,],self.gamma,self.depth)
                
        self.Som[self.om>0] = S_J
        self.Sf[self.om>0] = (2*np.pi)*S_J

        return self

    
    def set_from_waveseq(self,waveseq,method='Welch',nperseg=2**8,fmax=0):

        accepted_values_method = ['Welch']
        if method not in accepted_values_method:
            raise ValueError(f"Invalid input method. Accepted values are: {', '.join(accepted_values_method)}")

        match method:

            case 'Welch':

                f, Sf = csd(waveseq.wave,waveseq.wave,fs=waveseq.fs,nperseg=nperseg)
                if fmax>0:
                    index_fmax = np.argmin(np.abs(f-fmax))
                else:
                    index_fmax = np.shape(f)[0]
                self.f = f[:index_fmax,]
                self.Sf = np.abs(Sf[:index_fmax,])
                self.om = (2*np.pi)*self.f
                self.Som = self.Sf/(2*np.pi)
            
        return self


    # def set_from_obs(self,method='MEP'):

    def get_params(self,smooth_Tp=True):

        _,Hm0,Tp,Tm01,Tm02,Tm24,TE,_,epsilon,_ = \
            netsse.analys.spec.spec1d_to_params(self.Sf,self.f,'Hz',smooth_Tp)
        
        self.spec_params = {'Hm0':Hm0,'Tp':Tp,'Tm01':Tm01,'Tm02':Tm02,'Tm24':Tm24,'TE':TE,'epsilon':epsilon}

        return self
    

class Buoy(Platform):
    "Class for buoy definition"

    def __init__(self,name:str=None,owner:str='undefined',operations:list=[],\
                 seastate_collections:list=[],type:str='undefined'):
        """Initialises the buoy as a platform.

        Parameters
        ----------
        type : str, default 'undefined'
            Buoy type.

            .. note::
                Consult :func:`netsse.base.Platform.__init__` for information
                on the other parameters.
        
        Example
        -------
        >>> buoy1 = netsse.base.Buoy()
        """
        Platform.__init__(self,name,owner,operations,seastate_collections)
        self.type = type


class WaveRadar(Platform):
    "Class for wave radar definition"

    def __init__(self,name:str=None,owner:str='undefined',operations:list=[],\
                 seastate_collections:list=[],type:str='undefined'):
        """Initialises the wave radar as a platform.

        Parameters
        ----------
        type : str, default 'undefined'
            Wave radar type.

            .. note::
                Consult :func:`netsse.base.Platform.__init__` for information
                on the other parameters.
        
        Example
        -------
        >>> radar1 = netsse.base.WaveRadar()
        """
        Platform.__init__(self,name,owner,operations,seastate_collections)
        self.type = type


class Vessel(Platform):
    "Class for vessel definition"

    def __init__(self,name:str=None,owner:str='undefined',operations:list=[],\
                 seastate_collections:list=[],type:str='undefined',params:dict={},\
                 raos:list=[]):
        """Initialises the wave radar as a platform.

        Parameters
        ----------
        type : str, default 'undefined'
            Wave radar type.
        params : dict, default {}
            Vessel main dimensions and other geometrical parameters.
        raos : list, default []
            Vessel response amplitude operators.

            .. note::
                Consult :func:`netsse.base.Platform.__init__` for information
                on the other parameters.
        
        Example
        -------
        >>> vessel1 = netsse.base.Vessel(params={'L':200,'B':25,'T':30})
        """
        Platform.__init__(self,name,owner,operations,seastate_collections)
        self.type = type
        self.params = params
        self.raos = raos
    
    def add_rao(self,*args):
        pass

# if __name__ == "__main__":

#     waveseq = WaveSequence(Hs=2,Tp=10)
#     print(waveseq.duration)
#     print(waveseq.time)
#     print(waveseq.Hs)
#     waveseq.wave = waveseq.Hs/4*np.random.normal(size=(waveseq.Nt,))
#     wavespec = waveseq.get_wavespec(waveseq,fmax=0.5)

#     print(wavespec.get_params().spec_params['Hm0'])
