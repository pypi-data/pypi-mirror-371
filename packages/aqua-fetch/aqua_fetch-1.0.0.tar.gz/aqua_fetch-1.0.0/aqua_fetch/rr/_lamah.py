
import gc
import os
import warnings
from datetime import datetime
import concurrent.futures as cf
from typing import Union, List, Dict

import numpy as np
import pandas as pd

from .._backend import xarray as xr
from .._backend import netCDF4

from ..utils import get_cpus
from ..utils import check_attributes, download, unzip
from .utils import _RainfallRunoff, _handle_dynamic
from .._geom_utils import laea_to_wgs84, lcc_to_wgs84

from ._map import (
    observed_streamflow_cms,
    min_air_temp,
    min_air_temp_with_specifier,
    max_air_temp_with_specifier,
    mean_air_temp_with_specifier,
    max_air_temp,
    mean_air_temp,
    total_precipitation,
    snow_water_equivalent,
    solar_radiation,
    max_solar_radiation,
    min_solar_radiation,
    max_thermal_radiation,
    mean_thermal_radiation,
    u_component_of_wind_at_10m,
    v_component_of_wind_at_10m,
    max_dewpoint_temperature_at_2m,
    min_dewpoint_temperature_at_2m,
    mean_dewpoint_temperature_at_2m,
    mean_air_pressure,
    total_potential_evapotranspiration,
)

from ._map import (
    catchment_area,
    gauge_latitude,
    gauge_longitude,
    slope
    )

SEP = os.sep

# todo : currently when saving .nc files for each variable, we first fetch data for all meteo
# variables and then save a single variable and extract data for all meteos again. This 
# is extremely inefficient. We should not make multiple calls to .fetch we saving .ncs
# todo : try to use mfopen_dataset instead of opening multiple .nc files separately
# without xarray, LamaHCE seems to be much faster

class LamaHCE(_RainfallRunoff):
    """
    Large-Sample Data for Hydrology and Environmental Sciences for Central Europe
    (mainly Austria). The dataset is downloaded from
    `zenodo <https://zenodo.org/record/4609826#.YFNp59zt02w>`_
    following the work of
    `Klingler et al., 2021 <https://doi.org/10.5194/essd-13-4529-2021>`_ .
    For ``total_upstrm`` data, there are 859 stations with 61 static features
    and 17 dynamic features. The temporal extent of data is from 1981-01-01
    to 2019-12-31.
    """

    url = {
        '1_LamaH-CE_daily_hourly.tar.gz': 'https://zenodo.org/records/5153305/files/1_LamaH-CE_daily_hourly.tar.gz',
        '2_LamaH-CE_daily.tar.gz': 'https://zenodo.org/records/5153305/files/2_LamaH-CE_daily.tar.gz'
    }

    _data_types = ['total_upstrm', 'intermediate_all', 'intermediate_lowimp']
    time_steps = ['D', 'H']

    def __init__(
            self,
            path=None,
            *,
            timestep: str = 'D',
            data_type: str = 'total_upstrm',
            to_netcdf: bool = False,  # todo : current IO for .ncs are slow
            overwrite=False,
            **kwargs
            ):

        """
    Parameters
    ----------
        path : str
            If the data is alredy downloaded then provide the complete
            path to it. If None, then the data will be downloaded.
            The data is downloaded once and therefore susbsequent
            calls to this class will not download the data unless
            ``overwrite`` is set to True.
        timestep :
                possible values are ``D`` for daily or ``H`` for hourly timestep
        data_type :
                possible values are ``total_upstrm``, ``intermediate_all``
                or ``intermediate_lowimp``

    Examples
    --------
    >>> from aqua_fetch import LamaHCE
    # by default the timestep is daily and data_type is 'total_upstrm'
    >>> dataset = LamaHCE()
    ... # get data by station id
    >>> _, dynamic = dataset.fetch(stations='826', as_dataframe=True)
    >>> df = dynamic['826'] # dynamic is a dictionary of with keys as station names and values as DataFrames
    >>> df.shape
    (14244, 22)
    ...
    ... # get name of all stations as list
    >>> stns = dataset.stations()
    >>> len(stns)
       859
    ... # get data of 10 % of stations as dataframe
    >>> _, dynamic = dataset.fetch(0.1, as_dataframe=True)
    >>> len(dynamic)  # dynamic has data for 10% of stations (85 out of 859)
       85
    ...
    ... # dynamic is a dictionary whose values are dataframes of dynamic features
    >>> [df.shape for df in dynamic.values()]
        [(14244, 22), (14244, 22), (14244, 22),... (14244, 22), (14244, 22)]
    ...
    ... get the data of a single (randomly selected) station
    >>> _, dynamic = dataset.fetch(stations=1, as_dataframe=True)
    >>> len(dynamic)  # dynamic has data for 1 station
        1
    ... # get names of available dynamic features
    >>> dataset.dynamic_features
    ... # get only selected dynamic features
    >>> _, dynamic = dataset.fetch('826', as_dataframe=True,
    ...  dynamic_features=['airtemp_C_mean', 'total_et', 'pcp_mm', 'q_cms_obs'])
    >>> dynamic['826'].shape
       (14244, 4)
    ...
    ... # get names of available static features
    >>> dataset.static_features
    ... # get data of 10 random stations
    >>> _, dynamic = dataset.fetch(10, as_dataframe=True)
    >>> len(dynamic)  # remember this is a dictionary with values as dataframe
       10
    ...
    # If we get both static and dynamic data
    >>> static, dynamic = dataset.fetch(stations='826', static_features="all", as_dataframe=True)
    >>> static.shape, len(dynamic), dynamic['826'].shape
    ((1, 84), 1, (14244, 22))
    ...
    # If we don't set as_dataframe=True and have xarray installed then the returned data will be a xarray Dataset
    >>> _, dynamic = dataset.fetch(10)
    ... type(dynamic)   
    xarray.core.dataset.Dataset
    ...
    >>> dynamic.dims
    FrozenMappingWarningOnValuesAccess({'time': 14244, 'dynamic_features': 22})
    ...
    >>> len(dynamic.data_vars)
    10
    ...
    >>> coords = dataset.stn_coords() # returns coordinates of all stations
    >>> coords.shape
        (859, 2)
    >>> dataset.stn_coords('826')  # returns coordinates of station whose id is 826
        2995596.0	4811891.0
    >>> dataset.stn_coords(['826', '819'])  # returns coordinates of two stations
    ...
    # get area of a single station
    >>> dataset.area('826')
    # get coordinates of two stations
    >>> dataset.area(['826', '819'])
    ...
    # if fiona library is installed we can get the boundary as fiona Geometry
    >>> dataset.get_boundary('826')
    ...
    # the data_type can also be 'intermediate_all'
    >>> dataset = LamaHCE(data_type='intermediate_all')
    ...
    # or 'intermediate_lowimp'
    >>> dataset = LamaHCE(data_type='intermediate_lowimp')
    >>> len(dataset.stations())
    454
    ...
    # the timestep can also be hourly i.e. 'H'
    >>> dataset = LamaHCE(timestep='H')
    >>> _, dynamic = dataset.fetch(stations='79', as_dataframe=True)
    >>> dynamic['79'].shape
    (341856, 16)  # there are 16 dynamic features for hourly data
    """

        assert timestep in self.time_steps, f"invalid timestep '{timestep}' given, choose from {self.time_steps}"
        assert data_type in self._data_types, f"invalid data_type '{data_type}' given, choose from {self._data_types}"

        self.timestep = timestep
        self.data_type = data_type

        super().__init__(path=path, overwrite=overwrite, **kwargs)

        self.timestep = timestep

        if timestep == "D" and "1_LamaH-CE_daily_hourly.tar.gz" in self.url:
            self.url.pop("1_LamaH-CE_daily_hourly.tar.gz")
        if timestep == 'H' and '2_LamaH-CE_daily.tar.gz' in self.url:
            self.url.pop('2_LamaH-CE_daily.tar.gz')

        if not os.path.exists(self.path):
            os.makedirs(self.path)

        for fname, url in self.url.items():
            fpath = os.path.join(self.path, fname)
            if not os.path.exists(fpath):
                if self.verbosity: 
                    print(f'downloading {fname}')
                download(url, self.path, fname)

                unzip(self.path, verbosity=self.verbosity)

        self._static_features = self.static_data().columns.to_list()

        self._dynamic_features = self.__dynamic_features()

        if netCDF4 is None:
            to_netcdf = False

        if not self.all_ncs_exist and to_netcdf:
            self._maybe_to_netcdf(fdir=f"{data_type}_{timestep}")

    @property
    def dyn_fname(self) -> Union[str, os.PathLike]:
        """
        name of the .nc file which contains dynamic features. This file is created during dataset initialization
        only if to_netcdf is True and xarray is installed and the file does not already exists. The creation of this
        file can take some time however it leads to faster I/O operations.
        """
        return self.name.lower() + f"_{self.timestep}_{self.self.data_type}.nc"

    @property
    def static_map(self) -> Dict[str, str]:
        return {
                'area_calc': catchment_area(), # todo : difference between area_calc and area_gov?
                'lat': gauge_latitude(),
                'slope_mean': slope('mkm-1'),
                'lon': gauge_longitude(),
        }

    @property
    def dyn_map(self):
        return {
            'D': {
                'q_cms': observed_streamflow_cms(),
                '2m_temp_min': min_air_temp(),  # todo : what about height?
                '2m_temp_max': max_air_temp(),
                '2m_temp_mean': mean_air_temp(),
                'prec': total_precipitation(),
                'swe': snow_water_equivalent(),
                'surf_net_solar_rad_max': max_solar_radiation(),
                'surf_net_solar_rad_mean': solar_radiation(),
                'surf_net_therm_rad_max': max_thermal_radiation(),
                'surf_net_therm_rad_mean': mean_thermal_radiation(),
                '10m_wind_u': u_component_of_wind_at_10m(),
                '10m_wind_v': v_component_of_wind_at_10m(),
                '2m_dp_temp_max': max_dewpoint_temperature_at_2m(),
                '2m_dp_temp_mean': mean_dewpoint_temperature_at_2m(),
                '2m_dp_temp_min': min_dewpoint_temperature_at_2m(),
                'surf_press': mean_air_pressure(),  # todo : is this air pressure?
            },
            'H': {
                'q_cms': observed_streamflow_cms(),
                '2m_temp': mean_air_temp(),
                'prec': total_precipitation(),
                'swe': snow_water_equivalent(),
                '10m_wind_u': u_component_of_wind_at_10m(),
                '10m_wind_v': v_component_of_wind_at_10m(),
                '2m_dp_temp': mean_dewpoint_temperature_at_2m(),
                'surf_net_solar_rad': solar_radiation(),
                'surf_net_therm_rad': mean_thermal_radiation(),
                'surf_press': mean_air_pressure(),  # todo : is this air pressure?
            }
        }

    @property
    def dyn_factors(self) -> Dict[str, float]:
        return {
            mean_air_pressure(): 0.01,
        }

    @property
    def boundary_file(self) -> os.PathLike:
        if self.timestep == 'D':
            return os.path.join(self.path,
                                "A_basins_total_upstrm",
                                "3_shapefiles", "Basins_A.shp")
        else:
            return os.path.join(self.path,
                                "A_basins_total_upstrm",
                                "3_shapefiles", "Basins_A.shp")

    def _maybe_to_netcdf(self, fdir: str):
        # since data is very large, saving all the data in one file
        # consumes a lot of memory, which is impractical for most of the personal
        # computers! Therefore, saving each feature separately

        # todo: if we are only interested in one dynamic feature say 'o_cms_obs', 
        # then why do we need to save all the dynamic features in the netcdf file?

        fdir = os.path.join(self.path, fdir)
        if not os.path.exists(fdir):
            os.makedirs(fdir)

        if not self.all_ncs_exist:
            print(f'converting data to netcdf format for faster io operations')

            for feature in self.dynamic_features:

                # we must specify class level dyn_fname feature
                dyn_fname = os.path.join(fdir, f"{feature}.nc")

                if not os.path.exists(dyn_fname):
                    print(f'Saving {feature} as {dyn_fname}')
                    _, data = self.fetch(static_features=None, dynamic_features=feature)

                    data.to_netcdf(dyn_fname)

                    gc.collect()
        return

    @property
    def dynamic_fnames(self):
        return [f"{feature}.nc" for feature in self.dynamic_features]

    @property
    def all_ncs_exist(self):
        fdir = os.path.join(self.path, f"{self.data_type}_{self.timestep}")
        return all(os.path.exists(os.path.join(fdir, fname_)) for fname_ in self.dynamic_fnames)

    @property
    def dynamic_features(self):
        return self._dynamic_features

    def __dynamic_features(self) -> List[str]:
        station = self.stations()[0]
        df = self._read_stn_dyn(station)  # this takes time
        cols = df.columns.to_list()
        [cols.remove(val) for val in ['DOY', 'ckhs', 'checked', 'HOD', 'qceq', 'qcol'] if val in cols]
        return cols

    @property
    def static_features(self) -> List[str]:
        return self._static_features

    @property
    def data_type_dir(self):
        f = [f for f in os.listdir(self.path) if f.endswith(self.data_type)][0]
        return os.path.join(self.path, f'{self.path}{SEP}{f}')

    @property
    def q_dir(self):
        return os.path.join(self.path, 'D_gauges', '2_timeseries')

    def stations(self) -> list:
        # assuming file_names of the format ID_{stn_id}.csv
        ts_dir = {'H': 'hourly', 'D': 'daily'}[self.timestep]
        _dirs = os.listdir(os.path.join(self.data_type_dir,
                                        f'2_timeseries{SEP}{ts_dir}'))
        s = [f.split('_')[1].split('.csv')[0] for f in _dirs]
        return s

    def transform_stn_coords(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        transforms coordinates from EPSG:3035 (LAEA Europe) to projected

        """

        # following 2 lines are from .prj file 
        false_easting, false_northing = 4321000.0, 3210000.0
        lat_0, lon_0 = 52, 10

        x, y = laea_to_wgs84(df.loc[:, 'long'], df.loc[:, 'lat'], lon_0, lat_0, false_easting, false_northing)

        coord_m = pd.concat([x, y], axis=1)
        coord_m.columns = ['lat', 'long']
        return coord_m

    def fetch_stations_features(
            self,
            stations: list,
            dynamic_features='all',
            static_features=None,
            st=None,
            en=None,
            as_dataframe: bool = False,
            **kwargs
    ):
        """Reads attributes of more than one stations.

        This function checks of .nc files exist, then they are not prepared
        and saved otherwise first nc files are prepared and then the data is
        read again from nc files. Upon subsequent calls, the nc files are used
        for reading the data.

        Arguments:
            stations : list of stations for which data is to be fetched.
            dynamic_features : list of dynamic attributes to be fetched.
                if 'all', then all dynamic attributes will be fetched.
            static_features : list of static attributes to be fetched.
                If `all`, then all static attributes will be fetched. If None,
                then no static attribute will be fetched.
            st : start of data to be fetched.
            en : end of data to be fetched.
            as_dataframe : whether to return the data as pandas dataframe. default
                is :obj:`xarray.Dataset` object
            kwargs dict: additional keyword arguments

        Returns
        -------
        tuple
            A tuple of static and dynamic features. Static features are always
            returned as :obj:`pandas.DataFrame` with shape (stations, static features).
            The index of static features' DataFrame is the station/gauge ids while the columns 
            are names of the static features. Dynamic features are returned either as
            :obj:`xarray.Dataset` or a dictionary with keys as station names and values
            as :obj:`pandas.DataFrame` depending upon whether `as_dataframe`
            is True or False and whether the :obj:`xarray` library is installed or not.
            If dynamic features are :obj:`xarray.Dataset`, then this dataset consists of `data_vars`
            equal to the number of stations and station names as :obj:`xarray.Dataset.variables`  
            and `time` and `dynamic_features` as dimensions and coordinates.

        Raises:
            ValueError, if both dynamic_features and static_features are None

        Examples
        --------
        >>> from aqua_fetch import CAMELS_AUS
        >>> dataset = CAMELS_AUS()
        ... # find out station ids
        >>> dataset.stations()
        ... # get data of selected stations
        >>> dataset.fetch_stations_features(['912101A', '912105A', '915011A'],
        ...  as_dataframe=True)
        """

        if xr is None:
            if not as_dataframe:
                if self.verbosity: warnings.warn("xarray module is not installed so as_dataframe will have no effect. "
                              "Dynamic features will be returned as pandas DataFrame")
                as_dataframe = True

        st, en = self._check_length(st, en)
        static, dynamic = None, None

        if dynamic_features is not None:

            if self.verbosity>2:
                print(f'fetching data for {len(dynamic_features)} dynamic features for {len(stations)} stations')

            dynamic_features = check_attributes(dynamic_features, self.dynamic_features, 'dynamic_features')

            if netCDF4 is None or not self.all_ncs_exist:
                # read from csv files
                # following code will run only once when fetch is called inside init method
                dynamic = self._read_dynamic(stations, dynamic_features, st=st, en=en)
            else:
                dynamic = self._make_ds_from_ncs(dynamic_features, stations, st, en)

                if as_dataframe:
                    dynamic = {stn: dynamic[stn].to_pandas() for stn in dynamic}

            if static_features is not None:
                static = self.fetch_static_features(stations, static_features)
                dynamic = _handle_dynamic(dynamic, as_dataframe)
            else:
                # if the dyn is a dictionary of key, DataFames, we will return a as it is
                dynamic = _handle_dynamic(dynamic, as_dataframe)

        elif static_features is not None:

            static = self.fetch_static_features(stations, static_features)

        else:
            raise ValueError

        return static, dynamic

    @property
    def _q_name(self) -> str:
        return observed_streamflow_cms()

    def gauge_attributes(self) -> pd.DataFrame:
        fname = os.path.join(self.path,
                             'D_gauges',
                             '1_attributes',
                             'Gauge_attributes.csv')
        df = pd.read_csv(fname, sep=';', index_col='ID')

        df.index = df.index.astype(str)
        return df

    def catchment_attributes(self) -> pd.DataFrame:
        fname = os.path.join(self.data_type_dir,
                             f'1_attributes{SEP}Catchment_attributes.csv')

        df = pd.read_csv(fname, sep=';', index_col='ID')
        df.index = df.index.astype(str)
        return df

    def static_data(self) -> pd.DataFrame:
        """returns all static attributes of LamaHCE dataset"""
        df = pd.concat([self.catchment_attributes(), self.gauge_attributes()], axis=1)
        df.rename(columns=self.static_map, inplace=True)
        return df

    def _read_dynamic(
            self,
            stations,
            dynamic_features: Union[str, list] = 'all',
            st=None,
            en=None,
    ):
        """Reads features of one or more station"""

        cpus = self.processes or min(get_cpus(), 32)
        st, en = self._check_length(st, en)

        if cpus == 1 or len(stations) < 10:
            results = {}
            for idx, stn in enumerate(stations):
                results[stn] = self._read_stn_dyn(stn).loc[st:en, dynamic_features]

                if self.verbosity > 0 and idx % 10 == 0:
                    print(f'{idx} stations read')
        else:

            with  cf.ProcessPoolExecutor(max_workers=cpus) as executor:
                results = executor.map(
                    self._read_stn_dyn,
                    stations
                )

            results = {stn: data.loc[st:en, dynamic_features] for stn, data in zip(stations, results)}
        return results

    def _make_ds_from_ncs(self, dynamic_features, stations, st, en):
        """makes xarray Dataset by reading multiple .nc files"""

        if self.verbosity>1:
            print(f'fetching data for {len(dynamic_features)} dynamic features for {len(stations)} stations')

        dyns = []
        for idx, f in enumerate(dynamic_features):
            dyn_fpath = os.path.join(self.path, f"{self.data_type}_{self.timestep}", f'{f}.nc')
            dyn = xr.open_dataset(dyn_fpath)  # daataset
            dyns.append(dyn[stations].sel(time=slice(st, en)))

            if self.verbosity>3:
                print(f'{idx}: {f} read')

        xds = xr.concat(dyns, dim='dynamic_features')  # dataset todo: taking too much time!

        if self.verbosity>3:
            print(f'concatenated')
        return xds

    def fetch_static_features(
            self,
            stations: Union[str, List[str]] = "all",
            static_features: Union[str, List[str]] = None
    ) -> pd.DataFrame:
        """
        static features of LamaHCE

        Parameters
        ----------
            stations : str
                name/id of station of which to extract the data
            static_features : list/str, optional (default="all")
                The name/names of features to fetch. By default, all available
                static features are returned.

        Examples
        --------
            >>> from aqua_fetch import LamaHCE
            >>> dataset = LamaHCE(timestep='D', data_type='total_upstrm')
            >>> df = dataset.fetch_static_features('99')  # (1, 61)
            ...  # get list of all static features
            >>> dataset.static_features
            >>> dataset.fetch_static_features('99',
            >>> static_features=['area_calc', 'elev_mean', 'agr_fra', 'sand_fra'])  # (1, 4)
        """

        df = self.static_data()

        static_features = check_attributes(static_features, self.static_features, 'static features')
        stations = check_attributes(stations, self.stations(), 'stations')

        df = df[static_features]

        df.index = df.index.astype(str)
        df = df.loc[stations]
        if isinstance(df, pd.Series):
            df = pd.DataFrame(df).transpose()

        return df

    @property
    def chk_col(self):
        cols = {'D': 'checked',
                'H': 'ckhs'}
        return cols[self.timestep]

    def _read_stn_dyn(
            self,
            station,
            # features=None
    ) -> pd.DataFrame:
        # read a file containing timeseries data for one station
        q_df = self._read_q_for_station(station)

        met_df = self._read_met_for_station(station, features=None)

        df = pd.concat([met_df, q_df], axis=1)
        # change the column names to the names of dynamic features
        df.rename(columns=self.dyn_map[self.timestep], inplace=True)

        # change the units of the dynamic features
        for col in self.dyn_factors:
            df[col] = df[col] * self.dyn_factors[col]

        df.columns.name = "dynamic_features"
        df.index.name = "time"
        return df

    def met_fname(self, station):
        ts_folder = {'D': 'daily', 'H': 'hourly'}[self.timestep]
        return os.path.join(
            self.data_type_dir,
            f'2_timeseries{SEP}{ts_folder}{SEP}ID_{station}.csv')

    def _read_met_for_station(self, station, features):
        if isinstance(features, list):
            features = features.copy()
            [features.remove(itm) for itm in ['q_cms', 'ckhs'] if itm in features]

        met_dtype = {
            'YYYY': np.int32,
            'MM': np.int32,
            'DD': np.int32,
            'DOY': np.int32,
            '2m_temp_max': np.float32,
            '2m_temp_mean': np.float32,
            '2m_temp_min': np.float32,
            '2m_dp_temp_max': np.float32,
            '2m_dp_temp_mean': np.float32,
            '2m_dp_temp_min': np.float32,
            '10m_wind_u': np.float32,
            '10m_wind_v': np.float32,
            'fcst_alb': np.float32,
            'lai_high_veg': np.float32,
            'lai_low_veg': np.float32,
            'swe': np.float32,
            'surf_net_solar_rad_max': np.float32,
            'surf_net_solar_rad_mean': np.float32,
            'surf_net_therm_rad_max': np.float32,
            'surf_net_therm_rad_mean': np.float32,
            'surf_press': np.float32,
            'total_et': np.float32,
            'prec': np.float32,
            'volsw_123': np.float32,
            'volsw_4': np.float32
        }

        if self.timestep == 'D':
            if features:
                if not isinstance(features, list):
                    features = [features]

            met_df = pd.read_csv(self.met_fname(station), 
                                 sep=';', 
                                 dtype=met_dtype,
                                 )

            if pd.__version__ > "2.1.4":
                periods = pd.PeriodIndex.from_fields(year=met_df["YYYY"],
                                                    month=met_df["MM"], day=met_df["DD"],
                                                    freq="D")
            else:
                periods = pd.PeriodIndex(year=met_df["YYYY"],
                            month=met_df["MM"], day=met_df["DD"],
                            freq="D")
            met_df.index = periods.to_timestamp()

        else:
            if features:
                if not isinstance(features, list):
                    features = [features]

            met_dtype.update({
                'hh': np.int32,
                'mm': np.int32,
                'HOD': np.int32,
                '2m_temp': np.float32,
                '2m_dp_temp': np.float32,
                'surf_net_solar_rad': np.float32,
                'surf_net_therm_rad': np.float32
            })

            met_df = pd.read_csv(self.met_fname(station), sep=';', 
                                 dtype=met_dtype)

            if pd.__version__ > "2.1.4":
                periods = pd.PeriodIndex.from_fields(year=met_df["YYYY"],
                                                    month=met_df["MM"], 
                                                    day=met_df["DD"], 
                                                    hour=met_df["hh"],
                                                    minute=met_df["mm"], 
                                                    freq="h")
            else:
                periods = pd.PeriodIndex(year=met_df["YYYY"],
                            month=met_df["MM"], day=met_df["DD"], hour=met_df["hh"],
                            minute=met_df["mm"], freq="h")
            met_df.index = periods.to_timestamp()

        # remove the cols specifying index
        [met_df.pop(item) for item in ['YYYY', 'MM', 'DD', 'hh', 'mm'] if item in met_df]
        return met_df

    def _read_q_for_station(self, station):

        ts_folder = {'D': 'daily', 'H': 'hourly'}[self.timestep]

        q_fname = os.path.join(self.q_dir,
                               f'{ts_folder}{SEP}ID_{station}.csv')

        q_dtype = {
            'YYYY': np.int32,
            'MM': np.int32,
            'DD': np.int32,
            'qobs': np.float32,
            'checked': np.bool_
        }

        if self.timestep == 'D':
            q_df = pd.read_csv(q_fname, sep=';', dtype=q_dtype)

            if pd.__version__ > "2.1.4":
                periods = pd.PeriodIndex.from_fields(year=q_df["YYYY"],
                                                 month=q_df["MM"], day=q_df["DD"],
                                                 freq="D")
            else:
                periods = pd.PeriodIndex(year=q_df["YYYY"],
                            month=q_df["MM"], day=q_df["DD"],
                            freq="D")

            q_df.index = periods.to_timestamp()
            index = pd.date_range("1981-01-01", "2017-12-31", freq="D")
            q_df = q_df.reindex(index=index)
        else:
            q_dtype.update({
                'hh': np.int32,
                'mm': np.int32
            })

            q_df = pd.read_csv(q_fname, sep=';', dtype=q_dtype)

            if pd.__version__ > "2.1.4":
                periods = pd.PeriodIndex.from_fields(year=q_df["YYYY"],
                                                 month=q_df["MM"], day=q_df["DD"], hour=q_df["hh"],
                                                 minute=q_df["mm"], freq="h")
            else:
                periods = pd.PeriodIndex(year=q_df["YYYY"],
                            month=q_df["MM"], day=q_df["DD"], hour=q_df["hh"],
                            minute=q_df["mm"], freq="h")

            q_df.index = periods.to_timestamp()
            index = pd.date_range("1981-01-01", "2017-12-31", freq="h")
            q_df = q_df.reindex(index=index)

        [q_df.pop(item) for item in ['YYYY', 'MM', 'DD', 'hh', 'mm'] if item in q_df]
        q_df.rename(columns={'qobs': 'q_cms'}, inplace=True)

        q_df.columns.name = "dynamic_features"
        q_df.index.name = "time"

        return q_df

    @property
    def start(self):
        return "19810101"

    @property
    def end(self):  # todo, is it untill 2017 or 2019?
        return pd.Timestamp("2019-12-31 23:00:00")


class LamaHIce(LamaHCE):
    """
    Daily and hourly hydro-meteorological time series data of river basins
    of Iceland following `Helgason et al., 2024 <https://doi.org/10.5194/essd-16-2741-2024>`_.
    The total period of dataset is from 1950 to 2021 from 111 catchments for daily
    and from 1976-2023 for hourly timestep. The average
    length of daily data is 33 years while for that of hourly it is 11 years.
    The dataset is available on `hydroshare <https://www.hydroshare.org/resource/86117a5f36cc4b7c90a5d54e18161c91/>`_

    Examples
    --------
    >>> from aqua_fetch import LamaHIce
    # by default the timestep is daily and data_type is 'total_upstrm'
    >>> dataset = LamaHIce()
    ... # get data by station id
    >>> _, dynamic = dataset.fetch(stations='92', as_dataframe=True)
    >>> df = dynamic['92'] # dynamic is a dictionary of with keys as station names and values as DataFrames
    >>> df.shape
    (26298, 36)
    ...
    ... # get name of all stations as list
    >>> stns = dataset.stations()
    >>> len(stns)
       111
    ... # get data of 10 % of stations as dataframe
    >>> _, dynamic = dataset.fetch(0.1, as_dataframe=True)
    >>> len(dynamic)  # dynamic has data for 10% of stations (11 out of 111)
       11
    ...
    ... # dynamic is a dictionary whose values are dataframes of dynamic features
    >>> [df.shape for df in dynamic.values()]
        [(26298, 36), (26298, 36), (26298, 36),... (26298, 36), (26298, 36)]
    ...
    ... get the data of a single (randomly selected) station
    >>> _, dynamic = dataset.fetch(stations=1, as_dataframe=True)
    >>> len(dynamic)  # dynamic has data for 1 station
        1
    ... # get names of available dynamic features
    >>> dataset.dynamic_features
    ... # get only selected dynamic features
    >>> _, dynamic = dataset.fetch('92', as_dataframe=True,
    ...  dynamic_features=['swe', 'pet_mm', 'pcp_mm', 'q_cms_obs'])
    >>> dynamic['92'].shape
       (26298, 4)
    ...
    ... # get names of available static features
    >>> dataset.static_features
    ... # get data of 10 random stations
    >>> _, dynamic = dataset.fetch(10, as_dataframe=True)
    >>> len(dynamic)  # remember this is a dictionary with values as dataframe
       10
    ...
    # If we get both static and dynamic data
    >>> static, dynamic = dataset.fetch(stations='92', static_features="all", as_dataframe=True)
    >>> static.shape, len(dynamic), dynamic['92'].shape
    ((1, 154), 1, (26298, 36))
    ...
    # If we don't set as_dataframe=True and have xarray installed then the returned data will be a xarray Dataset
    >>> _, dynamic = dataset.fetch(10)
    ... type(dynamic)   
    xarray.core.dataset.Dataset
    ...
    >>> dynamic.dims
    FrozenMappingWarningOnValuesAccess({'time': 26298, 'dynamic_features': 36})
    ...
    >>> len(dynamic.data_vars)
    10
    ...
    >>> coords = dataset.stn_coords() # returns coordinates of all stations
    >>> coords.shape
        (111, 2)
    >>> dataset.stn_coords('92')  # returns coordinates of station whose id is 92
        571777.0	309737.0
    >>> dataset.stn_coords(['92', '5'])  # returns coordinates of two stations
    ...
    # get area of a single station
    >>> dataset.area('92')
    # get coordinates of two stations
    >>> dataset.area(['92', '5'])
    ...
    # if fiona library is installed we can get the boundary as fiona Geometry
    >>> dataset.get_boundary('92')
    ...
    # the data_type can also be 'intermediate_all'
    >>> dataset = LamaHIce(data_type='intermediate_all')
    ...
    # or 'intermediate_lowimp'
    >>> dataset = LamaHIce(data_type='intermediate_lowimp')
    >>> len(dataset.stations())
    86
    ...
    # the timestep can also be 'H'
    >>> dataset = LamaHIce(timestep='H')
    >>> _, dynamic = dataset.fetch(stations='79', as_dataframe=True)
    >>> dynamic['79'].shape
    (412848, 28)  # there are 28 dynamic features for hourly data
    
    """

    url = {
        'Caravan_extension_lamahice.zip':
            'https://www.hydroshare.org/resource/86117a5f36cc4b7c90a5d54e18161c91/data/contents/Caravan_extension_lamahice.zip',
        'lamah_ice.zip':
            'https://www.hydroshare.org/resource/86117a5f36cc4b7c90a5d54e18161c91/data/contents/lamah_ice.zip',
        'lamah_ice_hourly.zip':
            'https://www.hydroshare.org/resource/86117a5f36cc4b7c90a5d54e18161c91/data/contents/lamah_ice_hourly.zip'
    }
    _data_types = ['total_upstrm', 'intermediate_all', 'intermediate_lowimp']
    time_steps = ['D', 'H']
    DTYPES = {
        'total_upstrm': 'A_basins_total_upstrm',
        'intermediate_all': 'B_basins_intermediate_all',
        'intermediate_lowimp': 'C_basins_intermediate_lowimp'
    }

    def __init__(
            self,
            path=None,
            overwrite=False,
            *,
            timestep: str = "D",
            data_type: str = "total_upstrm",
            to_netcdf: bool = False,
            **kwargs):
        """

        Parameters
        ----------
            path : str
                If the data is alredy downloaded then provide the complete
                path to it. If None, then the data will be downloaded.
                The data is downloaded once and therefore susbsequent
                calls to this class will not download the data unless
                ``overwrite`` is set to True.
            timestep :
                    possible values are ``D`` for daily or ``H`` for hourly timestep
            data_type :
                    possible values are ``total_upstrm``, ``intermediate_all``
                    or ``intermediate_lowimp``
        """

        # don't download hourly data if timestep is daily
        if timestep == "D" and "lamah_ice_hourly.zip" in self.url:
            self.url.pop("lamah_ice_hourly.zip")
        if timestep == 'H' and 'Caravan_extension_lamahice.zip' in self.url:
            self.url.pop('Caravan_extension_lamahice.zip')

        super().__init__(path=path,
                         timestep=timestep,
                         data_type=data_type,
                         overwrite=overwrite,
                         to_netcdf=to_netcdf,
                         **kwargs)

    @property
    def static_map(self) -> Dict[str, str]:
        return {
                'area_calc_basin': catchment_area(),
                'lat_gauge': gauge_latitude(),
                'slope_mean_basin': slope('mkm-1'),
                'lon_gauge': gauge_longitude(),
        }

    @property
    def dyn_map(self):
        return {
            'D': {
                'qobs': observed_streamflow_cms(),
                '2m_temp_min': min_air_temp_with_specifier('2m'),
                '2m_temp_max': max_air_temp_with_specifier('2m'),
                '2m_temp_mean': mean_air_temp_with_specifier('2m'),
                'prec': total_precipitation(),
                'pet': total_potential_evapotranspiration(),
                'ref_et_rav': 'ref_et_mm',
            },
            'H': {
                'qobs': observed_streamflow_cms(),
                '2m_temp': mean_air_temp_with_specifier('2m'),
                'prec': total_precipitation(),
                'pet': total_potential_evapotranspiration(),
                'ref_et_rav': 'ref_et_mm',
            }
        }

    @property
    def dyn_factors(self) -> Dict[str, float]:
        return {}

    @property
    def q_dir(self):
        """returns the path where q files are located"""
        if self.timestep == 'H':
            return os.path.join(
                self.path, 
                    "lamah_ice_hourly", 
                    "lamah_ice_hourly",
                    'D_gauges', '2_timeseries')

        return os.path.join(self.path, "lamah_ice", 
                            "lamah_ice",
                            'D_gauges', '2_timeseries')

    @property
    def boundary_file(self) -> os.PathLike:
        return os.path.join(self.path,
                            "lamah_ice",
                            "lamah_ice",
                            "A_basins_total_upstrm",
                            "3_shapefiles", "Basins_A.shp")

    @property
    def start(self):
        if self.timestep == "H":
            return pd.Timestamp("19760826 00:00")
        return pd.Timestamp("19500101")

    @property
    def end(self):
        if self.timestep == "H":
            return pd.Timestamp("20230930 23:00")
        return pd.Timestamp("20211231")

    @property
    def gauges_path(self):
        """returns the path where gauge data files are located"""
        if self.timestep == "H":
            return os.path.join(self.path, "lamah_ice_hourly", "lamah_ice_hourly", "D_gauges")
        return os.path.join(self.path, "lamah_ice", "lamah_ice", "D_gauges")

    @property
    def q_path(self):
        """path where all q files are located"""
        if self.timestep == "H":
            return os.path.join(self.gauges_path, "2_timeseries", "hourly")
        return os.path.join(self.gauges_path, "2_timeseries", "daily")

    def transform_stn_coords(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        transforms coordinates from EPSG:3057 (Lambert 1993) to EPSG:4326 (WGS84)

        """

        # following values are from .prj file 
        # Parameters for EPSG:3057
        lon_0 = -19.0        # Central Meridian
        lat_0 = 65.0         # Latitude of Origin
        lat_1 = 64.25        # First standard parallel
        lat_2 = 65.75        # Second standard parallel
        false_easting = 500000.0
        false_northing = 500000.0

        lat, lon = lcc_to_wgs84(
        df['long'].values, df['lat'].values, 
        lon_0, lat_0, lat_1, lat_2, false_easting, 
        false_northing)

        coords_m = pd.DataFrame({'lat': lat, 'long': lon})
        return coords_m

    def met_fname(self, station):
        ts_folder = {'D': 'daily', 'H': 'hourly'}[self.timestep]
        return os.path.join(
                self.data_type_dir,
                f'2_timeseries{SEP}{ts_folder}{SEP}meteorological_data{SEP}ID_{station}.csv')

    def stations(self) -> List[str]:
        """
        returns names of stations as a list
        """
        return [fname.split('.')[0].split('_')[1] for fname in os.listdir(self._clim_ts_path())]

    def static_data(self) -> pd.DataFrame:
        """
        returns static data of all stations
        """

        if self.verbosity>2:
            print('reading static data')
        df = pd.concat([self.basin_attributes(), self.gauge_attributes()], axis=1)

        df.rename(columns=self.static_map, inplace=True)

        return df

    def gauge_attributes(self) -> pd.DataFrame:
        """
        returns gauge attributes from following two files

            - Gauge_attributes.csv
            - hydro_indices_1981_2018.csv

        Returns
        -------
        pd.DataFrame
            a dataframe of shape (111, 28)
        """
        g_attr_fpath = os.path.join(self.gauges_path, "1_attributes", "Gauge_attributes.csv")

        df_gattr = pd.read_csv(g_attr_fpath, sep=';', index_col='id')
        df_gattr.index = df_gattr.index.astype(str)

        hydro_idx_fpath = os.path.join(self.gauges_path, "1_attributes", "hydro_indices_1981_2018.csv")

        df_hidx = pd.read_csv(hydro_idx_fpath, sep=';', index_col='id')
        df_hidx.index = df_hidx.index.astype(str)

        df = pd.concat([df_gattr, df_hidx], axis=1)

        df.columns = [col + "_gauge" for col in df.columns]

        return df

    def _catch_attr_path(self) -> os.PathLike:
        return os.path.join(self.data_type_dir, "1_attributes")

    def _clim_ts_path(self) -> str:
        p0 = "lamah_ice"
        p1 = "2_timeseries"
        p2 = "daily"

        if self.timestep == "H":
            p0 = "lamah_ice_hourly"
            p1 = "2_timeseries"
            p2 = "hourly"

        path = os.path.join(self.path, p0, p0,
                            self.DTYPES[self.data_type],
                            p1, p2, "meteorological_data")
        return path

    def catchment_attributes(self) -> pd.DataFrame:
        """returns catchment attributes as DataFrame with 90 columns
        """

        fpath = os.path.join(self._catch_attr_path(), "Catchment_attributes.csv")

        if self.data_type == 'intermediate_lowimp':
            df = pd.read_csv(fpath, index_col='id')
        else:
            df = pd.read_csv(fpath, sep=';', index_col='id')
        df.index = df.index.astype(str)
        return df

    def wat_bal_attrs(self) -> pd.DataFrame:
        """water balance attributes"""
        fpath = os.path.join(self._catch_attr_path(),
                             "water_balance.csv")

        df = pd.read_csv(fpath, sep=';', index_col='id')
        df.index = df.index.astype(str)
        df.columns = [col + "_all" for col in df.columns]
        return df

    def wat_bal_unfiltered(self) -> pd.DataFrame:
        """water balance attributes from unfiltered q"""
        fpath = os.path.join(self._catch_attr_path(),
                             "water_balance_unfiltered.csv")

        df = pd.read_csv(fpath, sep=';', index_col='id')
        df.index = df.index.astype(str)
        df.columns = [col + "_unfiltered" for col in df.columns]
        return df

    def basin_attributes(self) -> pd.DataFrame:
        """returns basin attributes which are catchment attributes, water
        balance all attributes and water balance filtered attributes

        Returns
        -------
        pd.DataFrame
            a dataframe of shape (111, 104) where 104 are the static
            catchment/basin attributes
        """
        cat = self.catchment_attributes()

        if self.timestep == 'D' and self.data_type == 'total_upstrm':
            wat_bal_all = self.wat_bal_attrs()
            wat_bal_filt = self.wat_bal_unfiltered()
            df = pd.concat([cat, wat_bal_all, wat_bal_filt], axis=1)
        else:
            df = cat
        df.columns = [col + '_basin' for col in df.columns]
        return df

    def fetch_static_features(
            self,
            stations: Union[str, list] = 'all',
            static_features: Union[str, list] = None
    ) -> pd.DataFrame:
        """
        fetches static features of one or more stations
        """
        df = self.static_data()
        df.index = df.index.astype(str)

        static_features = check_attributes(static_features, self.static_features, 'static_features')
        stations = check_attributes(stations, self.stations(), 'stations')

        df = df.loc[stations, static_features]

        return df

    def q_mm(
            self,
            stations: Union[str, List[str]] = None
    ) -> pd.DataFrame:
        """
        returns streamflow in the units of milimeter per timestep (e.g. mm/day or mm/hour). This is obtained
        by diving q_cms/area

        parameters
        ----------
        stations : str/list
            name/names of stations. Default is None, which will return
            area of all stations

        Returns
        --------
        pd.DataFrame
            a :obj:`pandas.DataFrame` whose indices are time-steps and columns
            are catchment/station ids.

        """
        if self.timestep.lower().startswith('d'):
            conversion_factor = 86400
        elif self.timestep.lower().startswith('h'):
            conversion_factor = 3600
        else:
            raise ValueError(f"Invalid timestep: {self.timestep}. ")

        stations = check_attributes(stations, self.stations(), 'stations')
        q = self.fetch_q(stations)
        area_m2 = self.area(stations) * 1e6  # area in m2
        q = (q / area_m2) * conversion_factor  # cms to m
        return q * 1e3  # to mm

    def fetch_q(
            self,
            stations: Union[str, List[str]] = None,
            qc_flag: int = None
    ):
        """
        returns streamflow for one or more stations

        parameters
        -----------
        stations : str/List[str]
            name or names of stations for which streamflow is to be fetched
        qc_flag : int
            following flags are available
            40 Good
            80 Fair
            100 Estimated
            120 suspect
            200 unchecked
            250 missing

        Returns
        --------
        pd.DataFrame
            a :obj:`pandas.DataFrame` whose index is the time and columns are names of stations
            For daily timestep, the dataframe has shape of 32630 rows and 111 columns

        """
        stations = check_attributes(stations, self.stations(), 'stations')

        cpus = self.processes or min(get_cpus(), 16)
        if len(stations)<=10: cpus=1

        if self.verbosity>1:
            print(f"fetching streamflow for {len(stations)} stations with {cpus} cpus")

        if cpus == 1:
            qs = []
            for stn in stations:
                qs.append(self.fetch_stn_q(stn, qc_flag=qc_flag))
        else:
            qc_flag = [qc_flag for _ in range(len(stations))]
            with  cf.ProcessPoolExecutor(max_workers=cpus) as executor:
                qs = list(executor.map(
                    self.fetch_stn_q,
                    stations,
                    qc_flag
                ))

        df = pd.concat(qs, axis=1)
        df.columns = stations
        return df

    def fetch_stn_q(
            self,
            stn: str,
            qc_flag: int = None
    ) -> pd.Series:
        """returns streamflow for single station"""

        fpath = os.path.join(self.q_path, f"ID_{stn}.csv")

        if not os.path.exists(fpath):
            timestep = {'H': 'h', 'D': 'd'}[self.timestep]

            return pd.Series(dtype=np.float32,
                             index=pd.date_range(self.start, self.end, freq=timestep),
                             name='qobs')

        df = pd.read_csv(fpath, sep=';',
                         dtype={'YYYY': int,
                                'MM': int,
                                'DD': int,
                                'qobs': np.float32,
                                'qc_flag': np.float32
                                })

        # todo : consider quality code!

        index = df.apply(  # todo, is it taking more time?
            lambda x: datetime.strptime("{0} {1} {2}".format(
                x['YYYY'].astype(int), x['MM'].astype(int), x['DD'].astype(int)), "%Y %m %d"),
            axis=1)

        if self.timestep == "H":
            hour = df.groupby(['YYYY', 'MM', 'DD']).cumcount()
            df.index = index + pd.to_timedelta(hour, unit='h')
        else:
            df.index = pd.to_datetime(index)
        s = df['qobs']
        # s.name = stn
        return s

    def fetch_clim_features(
            self,
            stations: Union[str, List[str]] = None
    ):
        """Returns climate time series data for one or more stations

        Returns
        -------
        pd.DataFrame
        """
        stations = check_attributes(stations, self.stations(), 'stations')

        dfs = []
        for stn in stations:
            dfs.append(self.fetch_stn_meteo(stn))

        return pd.concat(dfs, axis=1)

    def fetch_stn_meteo(
            self,
            stn: str,
            nrows: int = None
    ) -> pd.DataFrame:
        """returns climate/meteorological time series data for one station

        Returns
        -------
        pd.DataFrame
            a :obj:`pandas.DataFrame` with 23 columns
        """
        fpath = os.path.join(self._clim_ts_path(), f"ID_{stn}.csv")

        dtypes = {
            "YYYY": np.int32,
            "DD": np.int32,
            "MM": np.int32,
            "2m_temp_max": np.float32,
            "2m_temp_mean": np.float32,
            "2m_temp_min": np.float32,
            "2m_dp_temp_max": np.float32,
            "2m_dp_temp_mean": np.float32,
            "2m_dp_temp_min": np.float32,
            "10m_wind_u": np.float32,
            "10m_wind_v": np.float32,
            "fcst_alb": np.float32,
            "lai_high_veg": np.float32,
            "lai_low_veg": np.float32,
            "swe": np.float32,
            "surf_net_solar_rad_max": np.int32,
            "surf_net_solar_rad_mean": np.int32,
            "surf_net_therm_rad_max": np.int32,
            "surf_net_therm_rad_mean": np.int32,
            "surf_press": np.float32,
            "total_et": np.float32,
            "prec": np.float32,
            "volsw_123": np.float32,
            "volsw_4": np.float32,
            "prec_rav": np.float32,
            "prec_carra": np.float32,
        }

        if not os.path.exists(fpath):
            raise FileNotFoundError(f"File not found: {fpath}")

        df = pd.read_csv(fpath, sep=';', dtype=dtypes, nrows=nrows)

        index = df.apply(
            lambda x: datetime.strptime("{0} {1} {2}".format(
                x['YYYY'].astype(int), x['MM'].astype(int), x['DD'].astype(int)), "%Y %m %d"),
            axis=1)

        if self.timestep == "H":
            # hour = df.groupby(['YYYY', 'MM', 'DD']).cumcount()
            df.index = index + pd.to_timedelta(df['HOD'], unit='h')
            for col in ['YYYY', 'MM', 'DD', 'DOY', 'hh', 'mm', 'HOD']:
                df.pop(col)
        else:
            df.index = pd.to_datetime(index)
            for col in ['YYYY', 'MM', 'DD', 'DOY', ]:
                df.pop(col)

        return df

    @property
    def data_type_dir(self):
        p = "lamah_ice"
        if self.timestep == "H":
            p = "lamah_ice_hourly"
        return os.path.join(self.path, p, p, self.DTYPES[self.data_type])

    def _read_dynamic(
            self,
            stations,
            dynamic_features: Union[str, list] = 'all',
            st=None,
            en=None,
    ):
        """Reads features of one or more station"""

        cpus = self.processes or min(get_cpus(), 16)
        st, en = self._check_length(st, en)

        if self.verbosity>1: 
            print(f"reading dynamic data for {len(stations)} stations with {cpus} cpus")

        if cpus > 1:

            with  cf.ProcessPoolExecutor(max_workers=cpus) as executor:
                results = executor.map(
                    self._read_stn_dyn,
                    stations
                )

            if dynamic_features == 'all':
                results = {stn: data for stn, data in zip(stations, results)}
            else:
                results = {stn: data.loc[st:en, dynamic_features] for stn, data in zip(stations, results)}
        else:
            results = {}
            for idx, stn in enumerate(stations):
                if dynamic_features == 'all':
                    results[stn] = self._read_stn_dyn(stn)
                else:
                    results[stn] = self._read_stn_dyn(stn).loc[st:en, dynamic_features]

                if idx % 10 == 0:
                    print(f"processed {idx} stations")

        return results

    def _read_stn_dyn(
            self,
            station: str
    ) -> pd.DataFrame:
        """
        Reads daily dynamic (meteorological + streamflow) data for one catchment
        and returns as DataFrame
        """

        if self.verbosity>2:
            print(f"reading data for {station}")

        q = self.fetch_stn_q(station).copy()
        met = self.fetch_stn_meteo(station).copy()

        # drop duplicated index from met
        met = met.loc[~met.index.duplicated(keep='first')].copy()

        df = pd.concat([met, q], axis=1).loc[self.start:self.end, :].copy()

        for col in self.dyn_map[self.timestep]:
            if col in df.columns:
                df.rename(columns={col: self.dyn_map[self.timestep][col]}, inplace=True)

        df.columns.name = "dynamic_features"
        df.index.name = "time"

        df = df.sort_index()
        # Ensure df always extends to self.end
        if df.index[-1] < self.end or df.index[0] > self.start:
            timestep = {'H': 'h', 'D': 'd'}[self.timestep]
            # Create complete date range from start of existing data to self.end
            complete_range = pd.date_range(start=self.start, end=self.end, freq=timestep)
            # Reindex to fill missing dates with NaN
            df = df.reindex(complete_range)
        return df

    @property
    def dynamic_fnames(self):
        return [f"{feature}.nc" for feature in self.dynamic_features]
