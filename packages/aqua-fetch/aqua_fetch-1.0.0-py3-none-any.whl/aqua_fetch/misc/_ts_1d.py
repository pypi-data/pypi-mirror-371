
from aqua_fetch._datasets import Datasets


class NorSWE(Datasets):
    """
    11.5 million observational data of snow water equivalent, snow depth and bulk
    snow density from Northern Hemisphere (Russia, Finland, Nepal, Canada, Switzerland, 
    Norway and US) from more than 10,000 stations spanning from 1979 to 2021. The dataset 
    is from manual snow courses, automated sensors and single point observations.
    For more information, see the ` Mortimer and Vionnet, 2025 <https://doi.org/10.5194/essd-17-3619-2025>`_.
    The dataset is available at `zenodo <https://zenodo.org/records/152633700>`_.
    """

    url = "https://zenodo.org/records/15263370"