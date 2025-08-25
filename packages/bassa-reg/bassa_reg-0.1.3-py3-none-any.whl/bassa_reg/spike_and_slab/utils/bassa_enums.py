from enum import Enum


class RegressionMetric(Enum):
    AIC = 'AIC'
    BIC = 'BIC'
    R2 = 'R^2'
    ADJ_R2 = 'Adjusted R^2'
    Q2 = 'Q^2'

class ScalerType(Enum):
    MINMAX = "minmax"
    STANDARD = "standard"


class SurvivalMetric(Enum):
    Q2 = 'Q^2'
    R2 = 'R^2'
    R2_ADJUSTED = 'R^2 Adjusted'
