
import os
from typing import List, Union, Dict

import pandas as pd

from .utils import _RainfallRunoff
from ..utils import check_attributes

from ._map import (
    observed_streamflow_cms,
    observed_streamflow_mm,
    # evapotranspiration
    catchment_area,
    gauge_latitude,
    gauge_longitude,
    slope,
    total_precipitation,
    )


class WaterBenchIowa(_RainfallRunoff):
    """
    Rainfall run-off dataset for Iowa (US) following the work of
    `Demir et al., 2022 <https://doi.org/10.5194/essd-14-5605-2022>`_
    This is hourly dataset of 125 catchments with
    7 static features and 3 dynamic features (pcp, et, discharge) for each catchment.
    The dynamic features are timeseries from 2011-10-01 12:00 to 2018-09-30 11:00.

    **Note: ** Currently the coordinates and catchment boundary files are not available
    for this dataset.

    Examples
    --------
    >>> from aqua_fetch import WaterBenchIowa
    >>> ds = WaterBenchIowa()
    ... # fetch static and dynamic features of 5 stations
    >>> static, dynamic = ds.fetch(5, static_features='all', as_dataframe=True)
    >>> len(dynamic)  # it is a dictionary with DataFrame
    5 
    ... # keys of dynamic are station names and values are DataFrames
    >>> data = dynamic.popitem()[1]
    >>> data.shape
    (61344, 3)
    >>> static.shape
    (5, 7)
    ...
    ... # using another method
    >>> dynamic = ds.fetch_dynamic_features('644', as_dataframe=True)
    >>> dynamic['644'].shape
    (61344, 3)
    ...
    >>> static, dynamic = ds.fetch(stations='644', static_features="all", as_dataframe=True)
    >>> static.shape, dynamic['644'].shape
    >>> ((1, 7), (61344, 3))
    """
    url = "https://zenodo.org/record/7087806#.Y6rW-BVByUk"

    def __init__(self, path=None, **kwargs):
        super(WaterBenchIowa, self).__init__(path=path, timestep='H', **kwargs)

        self._download()

        self._maybe_to_netcdf()

    @property
    def static_map(self) -> Dict[str, str]:
        return {
            'area': catchment_area(),
            'slope': slope('perc'),
        }

    @property
    def dyn_map(self):
        return {
        'discharge': observed_streamflow_mm(),
        'precipitation': total_precipitation(),
        }

    def stations(self)->List[str]:
        return [fname.split('_')[0] for fname in os.listdir(self.ts_path) if fname.endswith('.csv')]

    @property
    def ts_path(self)->str:
        return os.path.join(self.path, 'data_time_series', 'data_time_series')

    @property
    def static_features(self)->List[str]:
        return ['travel_time', catchment_area(), slope('perc'), 'loam', 'silt',
                'sandy_clay_loam', 'silty_clay_loam']

    @property
    def static_map(self)->Dict[str, str]:
        return {
            'area': catchment_area(),
            'slope': slope('perc'),
        }

    def fetch_static_features(
            self,
            stations: Union[str, List[str]] = "all",
            static_features:Union[str, List[str]] = "all"
    )->pd.DataFrame:
        """

        Parameters
        ----------
            stations : str
                name/id of station of which to extract the data
            static_features : list/str, optional (default="all")
                The name/names of features to fetch. By default, all available
                static features are returned.

        Examples
        ---------
        >>> from aqua_fetch import WaterBenchIowa
        >>> dataset = WaterBenchIowa()
        get the names of stations
        >>> stns = dataset.stations()
        >>> len(stns)
            125
        get all static data of all stations
        >>> static_data = dataset.fetch_static_features(stns)
        >>> static_data.shape
           (125, 7)
        get static data of one station only
        >>> static_data = dataset.fetch_static_features('592')
        >>> static_data.shape
           (1, 7)
        get the names of static features
        >>> dataset.static_features
        get only selected features of all stations
        >>> static_data = dataset.fetch_static_features(stns, ['slope', 'area_km2'])
        >>> static_data.shape
           (125, 2)
        >>> data = dataset.fetch_static_features('592', static_features=['slope', 'area_km2'])
        >>> data.shape
           (1, 2)

        """
        stations = check_attributes(stations, self.stations())

        static_features = check_attributes(static_features, self.static_features, 'static_features')

        dfs = []
        for stn in stations:
            fname = os.path.join(self.ts_path, f"{stn}_data.csv")
            df = pd.read_csv(fname, nrows=1)
            dfs.append(df.iloc[0, :].rename(stn))

        df = pd.concat(dfs, axis=1).T

        df.rename(columns=self.static_map, inplace=True)

        return df.loc[stations, static_features]

    def _read_stn_dyn(self, stn)->pd.DataFrame:
        fname = os.path.join(self.ts_path, f"{stn}_data.csv")
        df = pd.read_csv(fname)
        df.index = pd.to_datetime(df.pop('datetime'))
        df = df.loc[:, ['precipitation', 'discharge', 'et']]

        df.rename(columns=self.dyn_map, inplace=True)
        return df

    @property
    def start(self):
        return pd.Timestamp("20111001 12:00:00")

    @property
    def end(self):
        return pd.Timestamp("20180930 11:00:00")
