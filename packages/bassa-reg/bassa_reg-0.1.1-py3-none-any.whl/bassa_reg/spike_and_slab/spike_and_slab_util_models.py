from typing import Union
import pandas as pd

import pickle
import scipy.sparse as sp
import numpy as np
from typing import List

class SpikeAndSlabLoader:
    """
    This class is used to load the parameters of a previous experiment.
    """
    a: List[float]
    tau: List[float]
    sigma: List[float]
    w: np.array
    s: np.array
    log_prob: dict
    continue_experiment: bool
    path: str

    def __init__(self, path: str):
        print("Loading Files")
        self.path = path
        self.log_prob = {'total': [], 'partial': []}
        try:
            samples_path = f"{path}/samples/"
            # Load the sparse binary matrix
            self.s = sp.load_npz(f"{samples_path}/s.npz").toarray()

            # Load the list of arrays (w)
            self.w = sp.load_npz(f"{samples_path}/w.npz").toarray()

            # Load the list of numbers (a)
            loaded_a = np.load(f"{samples_path}/a.npz")
            self.a = [loaded_a[f"arr_{i}"] for i in range(len(loaded_a.files))]

            # Load the list of numbers (tau)
            loaded_tau = np.load(f"{samples_path}/tau.npz")
            self.tau = [loaded_tau[f"arr_{i}"] for i in range(len(loaded_tau.files))]

            # Load the list of numbers (sigma)
            loaded_sigma = np.load(f"{samples_path}/sigma.npz")
            self.sigma = [loaded_sigma[f"arr_{i}"] for i in range(len(loaded_sigma.files))]
        except FileNotFoundError:
            raise FileNotFoundError(f"The path provided does not contain the necessary files, path provided:"
                                    f" {path}. Make sure you have a folder named 'samples' under this path with saved"
                                    f" parameters. If you didn't set the 'save_samples' parameter to True when running,"
                                    f" the parameters will not be saved.")


class SpikeAndSlabPriors:
    """
    This class is used to store the prior parameters for the Spike and Slab model.
    """
    a_alpha_prior: float
    a_beta_prior: float
    tau_alpha_prior: float
    tau_beta_prior: float
    sigma_alpha_prior: float
    sigma_beta_prior: float
    feature_start_bias: Union[pd.Series, None]

    def __init__(self, a_alpha_prior: float = 2,
                 a_beta_prior: float = 10,
                 tau_alpha_prior: float = 5,
                 tau_beta_prior: float = 4,
                 sigma_alpha_prior: float = 7,
                 sigma_beta_prior: float = 4,
                 feature_start_bias: Union[pd.Series, None] = None):

        self.a_alpha_prior = a_alpha_prior
        self.a_beta_prior = a_beta_prior
        self.tau_alpha_prior = tau_alpha_prior
        self.tau_beta_prior = tau_beta_prior
        self.sigma_alpha_prior = sigma_alpha_prior
        self.sigma_beta_prior = sigma_beta_prior
        self.feature_start_bias = feature_start_bias

class TestSet:
    def __init__(self, x_test: pd.DataFrame,
                 samples_per_y: int,
                 iterations: int,
                 y_test: Union[pd.DataFrame, None] = None):
        self.x_test = x_test
        self.y_test = y_test
        self.scaled_x_test = None
        self.scaled_y_test = None
        self.samples_per_y = samples_per_y
        self.iterations = iterations
        self.y_pred = None


class PlotScenario:
    def __init__(self, data: np.array,
                 log_prob: np.array,
                 title: str,
                 x_label: str,
                 y_label: str):
        self.data = data
        self.log_prob = log_prob
        self.title = title
        self.x_label = x_label
        self.y_label = y_label


class GewekeConfiguration:

    def __init__(self, throw_away: Union[float, None] = None,
                 do_geweke: bool = False,
                 a_bin_size: float = 0.01,
                 y_bin_size: float = 0.1,
                 default_bin_size: float = 0.01):
        if throw_away is None and do_geweke:
            assert False, "If you want to do Geweke's test, you must specify the throw_away parameter"
        self.do_geweke = do_geweke
        self.throw_away = throw_away
        self.a_bin_size = a_bin_size
        self.y_bin_size = y_bin_size
        self.default_bin_size = default_bin_size

class ExperimentalDesignDataset:

    def __init__(self, x: pd.DataFrame,
                 probability_samples: int,
                 entropy_samples: int,
                 x_ids: Union[None, pd.DataFrame] = None,
                 batch_size: int = 35,
                 force_cpu: bool = True,):
        self.x = x
        self.probability_samples = probability_samples
        self.entropy_samples = entropy_samples
        self.batch_size = batch_size
        self.force_cpu = force_cpu
        self.x_ids = x_ids