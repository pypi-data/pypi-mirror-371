import os
import uuid

import tqdm

import pandas as pd
import numpy as np
from typing import Union
import scipy.sparse as sp
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import bassa_reg.spike_and_slab.spike_and_slab_util_models as models
from bassa_reg.spike_and_slab.spike_and_slab_core import SpikeAndSlabCore
from bassa_reg.spike_and_slab.utils.bassa_enums import ScalerType
from bassa_reg.spike_and_slab.utils.gewekes_plot import geweke_plot
from bassa_reg.spike_and_slab.utils.util_functions import get_date_for_experiment_name, calc_mae, calc_mse, calc_r2

class SpikeAndSlabConfigurations:
    def __init__(self,
                 sampler_iterations: int = 20000,
                 top_n_features_to_show: int = 20,
                 internal_y_to_sample: int = 20,
                 save_meta_data: bool = True,
                 save_samples: bool = False,
                 verbose: bool = True,
                 dont_save_anything: bool = False,
                 geweke: models.GewekeConfiguration = models.GewekeConfiguration()):
        self.sampler_iterations = sampler_iterations
        self.top_n_features_to_show = top_n_features_to_show
        self.internal_y_to_sample = internal_y_to_sample
        self.save_meta_data = save_meta_data
        self.save_samples = save_samples
        self.verbose = verbose
        self.geweke = geweke
        self.dont_save_anything = dont_save_anything

class SpikeAndSlabRegression:
    def __init__(self, x: pd.DataFrame,
                 y: pd.Series,
                 experiment_name: str,
                 project_path: str,
                 test_set: Union[models.TestSet, None] = None,
                 priors: models.SpikeAndSlabPriors = models.SpikeAndSlabPriors(),
                 load_experiment: Union[models.SpikeAndSlabLoader, None] = None,
                 config: SpikeAndSlabConfigurations = SpikeAndSlabConfigurations(),
                ):

        self.priors = priors
        self.exp_name = experiment_name
        self.project_path = project_path
        self.config = config
        self.loaded_experiment = load_experiment
        self.unique_run_id = uuid.uuid4()
        self.core = None
        self.finished = False

        self.original_x = x.copy()
        self.original_y = y.copy()
        self.test_set = test_set

        # a values
        self.a = 0 if load_experiment is None else load_experiment.a[-1]
        self.all_a = [] if load_experiment is None else load_experiment.a
        self.a_all_alphas = []
        self.a_all_betas = []
        self.a_alpha_prior = priors.a_alpha_prior
        self.a_beta_prior = priors.a_beta_prior

        # tau values
        self.tau = 0 if load_experiment is None else load_experiment.tau[-1]
        self.all_tau = [] if load_experiment is None else load_experiment.tau
        self.all_tau_alphas = []
        self.all_tau_betas = []
        self.tau_alpha_prior = priors.tau_alpha_prior
        self.tau_beta_prior = priors.tau_beta_prior

        # sigma values
        self.sigma = 0 if load_experiment is None else load_experiment.sigma[-1]
        self.all_sigma = [] if load_experiment is None else load_experiment.sigma
        self.all_sigma_alphas = []
        self.all_sigma_betas = []
        self.sigma_alpha_prior = priors.sigma_alpha_prior
        self.sigma_beta_prior = priors.sigma_beta_prior

        self.w = [] if load_experiment is None else load_experiment.w[-1]
        self.all_w = [] if load_experiment is None else load_experiment.w
        self.s = [] if load_experiment is None else load_experiment.s[:, -1].tolist()

        self.all_mse = []

        # convert anything to numpy array
        final_x = x
        final_y = y
        if not isinstance(x, np.ndarray):
            final_x = x.to_numpy().astype(np.float64)
        if not isinstance(y, np.ndarray):
            final_y = y.to_numpy().astype(np.float64)

        self.feature_names = self.original_x.columns

        self.scaler_x = get_scaler(ScalerType.STANDARD)
        self.x = self.scaler_x.fit_transform(final_x)
        self.scaler_y = get_scaler(ScalerType.STANDARD)
        self.y = self.scaler_y.fit_transform(final_y.reshape(-1, 1))
        # make y a 1d array
        self.y = self.y[:, 0]

        self.duplicates = ""
        self.x, self.duplicates, self.feature_names = find_identical_columns(self.x, self.feature_names)
        self.original_x_deduplicated, _, self.original_x_deduplicated_feature_names = find_identical_columns(self.x,
                                                                                                               self.feature_names)
        self.feature_types = ['continuous'] * self.x.shape[1]

        if self.test_set is not None:
            # 1. Scale test set (all features, to match scaler expectations)
            np_x_test = self.test_set.x_test.to_numpy().astype(np.float64)
            scaled_x_test_full = self.scaler_x.transform(np_x_test)

            # 2. Remove duplicate columns from the SCALED test set
            columns_to_remove = [col for sublist in self.duplicates.values() for col in sublist]
            # Find the column indices to remove (must match the train set's original columns)
            col_indexes = [self.original_x.columns.get_loc(col) for col in columns_to_remove]
            scaled_x_test_dedup = np.delete(scaled_x_test_full, col_indexes, axis=1)

            self.test_set.scaled_x_test = scaled_x_test_dedup

            # (Optional) Handle y scaling as before
            if self.test_set.y_test is not None:
                np_y_test = self.test_set.y_test.to_numpy().astype(np.float64)
                self.test_set.scaled_y_test = self.scaler_y.transform(np_y_test.reshape(-1, 1)).flatten()

        self.internal_y_samples = None

        self.all_s = np.zeros((self.x.shape[1], self.config.sampler_iterations))

        if load_experiment is not None:
            self.all_s = np.zeros((self.x.shape[1], self.config.sampler_iterations + load_experiment.s.shape[1]))
            self.all_s[:, :load_experiment.s.shape[1]] = load_experiment.s
            self.all_w = np.zeros((self.x.shape[1], self.config.sampler_iterations + load_experiment.w.shape[1]))
            self.all_w[:, :load_experiment.w.shape[1]] = load_experiment.w



        # helper variables
        self.priors: models.SpikeAndSlabPriors = priors
        self.geweke: models.GewekeConfiguration = self.config.geweke
        self.geweke_pairs = [[], [], [], [], []]
        self.exp_subtraction_threshold : int = 50

        self.current_size = 0
        self.y_prior = None
        self.xs = None
        self.s_sums = []  # amount of s's that are 1
        self.s_ratios = None

        self.current_iter = 0

        self.current_time = get_date_for_experiment_name()
        self.full_experiment_name = f"{self.exp_name}-{self.current_time}"
        self.train_dir = 'logs/' + self.current_time

    def sample_geweke(self):
        sigma0 = np.random.gamma(self.sigma_alpha_prior,
                                 scale=1 / self.sigma_beta_prior) ** -0.5
        tau0 = np.random.gamma(self.tau_alpha_prior,
                               scale=1 / self.tau_beta_prior) ** -0.5
        a0 = np.random.beta(self.a_alpha_prior, self.a_beta_prior)

        s0 = np.random.binomial(1, a0, size=self.x.shape[1])
        w0_raw = np.random.normal(0.0, tau0, size=self.x.shape[1])
        w0 = w0_raw * s0

        y0 = self.x @ w0 + np.random.normal(0.0, sigma0, self.x.shape[0])

        _y, _sigma, _tau, _a = self.y, self.sigma, self.tau, self.a
        _s, _w = self.s.copy(), self.w.copy()

        self.y, self.sigma, self.tau, self.a = y0, sigma0, tau0, a0
        self.s, self.w = s0.copy(), w0[s0 == 1] if s0.sum() else np.array([0.])

        sigma1, tau1, a1 = self.sigma, self.tau, self.a
        s1 = self.s.copy()
        w1 = np.zeros_like(w0)
        if s1.sum():
            w1[s1 == 1] = self.w

        self.y, self.sigma, self.tau, self.a = _y, _sigma, _tau, _a
        self.s, self.w = _s, _w

        self.geweke_pairs[0].append((sigma0, sigma1))
        self.geweke_pairs[1].append((tau0, tau1))
        self.geweke_pairs[2].append((a0, a1))
        self.geweke_pairs[3].append((s0.sum(), s1.sum()))

    def init_vars(self):
        self.a = np.random.beta(self.a_alpha_prior, self.a_beta_prior, size=1)[0]
        self.s = np.random.binomial(1, self.a, size=self.x.shape[1])
        multiplier = 1.01
        i = 1
        while np.sum(self.s) == 0:
            self.s = np.random.binomial(1, self.a * multiplier ** i, size=self.x.shape[1])
            i += 1

        if self.priors.feature_start_bias is not None:
            self.s = np.zeros(self.x.shape[1])
            for feature in self.priors.feature_start_bias:
                if feature in self.feature_names:
                    index = self.feature_names.index(feature)
                    self.s[index] = 1


        if self.loaded_experiment is None:
            self.xs = get_xs(self.s, self.x)
            self.current_size = np.sum(self.s)
            self.sigma = np.random.gamma(self.sigma_alpha_prior, scale=1 / self.sigma_beta_prior, size=1)[0] ** -0.5
            self.tau = np.random.gamma(self.tau_alpha_prior, scale=1 / self.tau_beta_prior, size=1)[0] ** -0.5
            self.w = np.random.normal(loc=0, scale=self.tau, size=(1, int(self.current_size)))
        else:
            self.xs = get_xs(self.s, self.x)
            self.current_size = np.sum(self.s)
            self.a = self.all_a[-1]
            self.sigma = self.all_sigma[-1]
            self.tau = self.all_tau[-1]
            self.w = self.all_w[-1]

    def save(self):
        if self.config.dont_save_anything:
            return

        if self.config.save_meta_data or self.config.save_samples:
            os.mkdir(self.full_experiment_name)

        if self.config.save_samples:
            samples_path = os.path.join(self.full_experiment_name, "samples")
            os.mkdir(samples_path)
            sp.save_npz(f"{samples_path}/s.npz", sp.csr_matrix(self.all_s))
            sp.save_npz(f"{samples_path}/w.npz", sp.csr_matrix(self.all_w))
            np.savez_compressed(f"{samples_path}/a.npz", *self.all_a)
            np.savez_compressed(f"{samples_path}/tau.npz", *self.all_tau)
            np.savez_compressed(f"{samples_path}/sigma.npz", *self.all_sigma)

        mse_on_train = ""
        mae_on_train = ""
        r2_on_train = ""
        if self.internal_y_samples is not None:
            y_predict_transformed = self.scaler_y.inverse_transform(self.internal_y_samples)
            _predict_mean = np.mean(y_predict_transformed, axis=0)
            mse_on_train = calc_mse(self.original_y, _predict_mean)
            mae_on_train = calc_mae(self.original_y, _predict_mean)
            r2_on_train = calc_r2(self.original_y, _predict_mean)

        if not self.geweke.do_geweke:
            if self.config.save_meta_data:
                data = {
                    'name': [self.exp_name],
                    'continued_from': [self.loaded_experiment.path if self.loaded_experiment is not None else None],
                    'iterations': [self.config.sampler_iterations],
                    'a_alpha': [self.a_alpha_prior],
                    'a_beta': [self.a_beta_prior],
                    'tau_alpha': [self.tau_alpha_prior],
                    'tau_beta': [self.tau_beta_prior],
                    'sigma_alpha': [self.sigma_alpha_prior],
                    'sigma_beta': [self.sigma_beta_prior],
                    'duplicates': [self.duplicates],
                    'mse_on_train': [round(mse_on_train,4) if self.internal_y_samples is not None else None],
                    'mae_on_train': [round(mae_on_train,4) if self.internal_y_samples is not None else None],
                    'r2_on_train': [round(r2_on_train,4) if self.internal_y_samples is not None else None],
                }
                pd.DataFrame(data).to_csv(f"{self.full_experiment_name}/meta_data.csv", index=False)

            if self.test_set is not None:
                y_test = self.test_set.y_test
                y_predictions = self.test_set.y_pred
                mse_on_test = calc_mse(y_test, y_predictions)
                mae_on_test = calc_mae(y_test, y_predictions)

                pred_dir = f"{self.full_experiment_name}/predictions"
                os.mkdir(pred_dir)
                df_preds = pd.DataFrame({
                    'y_test': y_test,
                    'y_pred': y_predictions
                })
                df_preds.to_csv(f"{pred_dir}/values.csv", index=False)

                # Save mse & mae
                df_metrics = pd.DataFrame({
                    'mse': [mse_on_test],
                    'mae': [mae_on_test],
                    'samples_per_y' : [self.test_set.samples_per_y],
                    'predictions_iterations': [self.test_set.iterations],
                })
                df_metrics.to_csv(f"{pred_dir}/data.csv", index=False)

        if self.geweke.do_geweke:
            geweke_plot(self.geweke_pairs, self.geweke)

    def cycle_core(self):
        self.core.cycle(False)
        self.core.a = self.a
        self.core.tau = self.tau
        self.core.sigma = self.sigma
        self.core.s = self.s
        self.core.w = self.w

    def run(self):
        priors_tuple = (
            self.a_alpha_prior,
            self.a_beta_prior,
            self.sigma_alpha_prior,
            self.sigma_beta_prior,
            self.tau_alpha_prior,
            self.tau_beta_prior
        )

        start_iteration = 0
        total_iterations = self.config.sampler_iterations
        progress_bar = tqdm.tqdm(range(start_iteration, total_iterations), disable=not self.config.verbose,
                                  initial=start_iteration, total=total_iterations)
        sampling_start_iter =  int(total_iterations * 0.9)

        if self.test_set is not None:
            prediction_iterations = self.test_set.iterations
            x_test = self.test_set.scaled_x_test
        else:
            prediction_iterations = 0
            x_test = np.zeros((1, self.x.shape[1]))  # dummy value, not used

        core = SpikeAndSlabCore(self.x,
                                self.y,
                                x_test,
                                priors_tuple,
                                self.config.sampler_iterations,
                                prediction_iterations)
        self.core = core

        if self.loaded_experiment is None:
            a = np.random.beta(self.a_alpha_prior, self.a_beta_prior, size=1)[0].astype(np.float32)
            s = np.random.binomial(1, a, size=self.x.shape[1]).astype(np.float32)
            tau = np.random.beta(self.tau_alpha_prior, self.tau_beta_prior, size=1)[0].astype(np.float32)
            sigma = np.random.beta(self.sigma_alpha_prior, self.sigma_beta_prior, size=1)[0].astype(np.float32)
            multiplier = 1.01
            i = 1
            while np.sum(s) == 0:
                s = np.random.binomial(1, a * multiplier * i, size=self.x.shape[1]).astype(np.float32)
                i += 1
            w = np.random.normal(loc=0, scale=tau, size=int(np.sum(s))).astype(np.float32)

        else:
            a = self.loaded_experiment.a[-1]
            tau = self.loaded_experiment.tau[-1]
            sigma = self.loaded_experiment.sigma[-1]
            s = self.loaded_experiment.s[:, -1]
            w = self.loaded_experiment.w[:, -1]
        core.set_initial_state(a, s, w, tau, sigma)

        for self.current_iter in progress_bar:
            if self.geweke.do_geweke:
                core.sample_geweke()
            core.cycle()

            if self.current_iter > sampling_start_iter:
               core.compute_internal_y_prediction()

            description = (
                f"a: {round(core.a, 3)}, variables: {sum(core.s)}/{len(core.s)}, "
                f"sigma: {round(core.sigma, 3)}, tau: {round(core.tau, 3)}"
            )
            progress_bar.set_description(description)

        # Test set predictions
        if self.test_set is not None:
            progress_bar = tqdm.tqdm(range(prediction_iterations), disable=not self.config.verbose)
            for i in progress_bar:
                progress_bar.set_description(f"Predicting y: {i}/{prediction_iterations}")
                core.predict_on_test_set(i, self.test_set.samples_per_y)
                core.cycle(False)
            predictions = core.y_predictions
            self.test_set.y_pred = pd.Series(predictions.mean(axis=1))
            self.test_set.y_pred = self.scaler_y.inverse_transform(self.test_set.y_pred.values.reshape(-1, 1)).flatten()

        self.a = core.a
        self.tau = core.tau
        self.sigma = core.sigma
        self.w = core.w
        self.s = core.s
        if self.loaded_experiment is None:
            self.all_a = core.a_chain
            self.all_tau = core.tau_chain
            self.all_sigma = core.sigma_chain
            self.all_w = core.w_chain
            self.all_s = core.s_chain
        else:
            self.all_a = self.loaded_experiment.a + core.a_chain
            self.all_tau = self.loaded_experiment.tau + core.tau_chain
            self.all_sigma = self.loaded_experiment.sigma + core.sigma_chain
            self.all_w = self.loaded_experiment.w + core.w_chain
            self.all_s[:, self.loaded_experiment.s.shape[1]:] = core.s_chain
        self.internal_y_samples = core.internal_y_predictions.T
        self.internal_y_samples = self.internal_y_samples[~np.all(self.internal_y_samples == 0, axis=1)]

        n = core.geweke_index  # number of stored Geweke samples

        # sigma: prior/posterior pairs
        for i in range(n):
            self.geweke_pairs[0].append((core.geweke_sigma[i, 0], core.geweke_sigma[i, 1]))
            self.geweke_pairs[1].append((core.geweke_tau[i, 0], core.geweke_tau[i, 1]))
            self.geweke_pairs[2].append((core.geweke_a[i, 0], core.geweke_a[i, 1]))
            self.geweke_pairs[3].append((core.geweke_s_sum[i, 0], core.geweke_s_sum[i, 1]))

        self.save()
        self.finished = True
        return


def get_scaler(scaler_type: ScalerType):
    if scaler_type.value == "minmax":
        return MinMaxScaler()
    elif scaler_type.value == "standard":
        return StandardScaler()
    else:
        return None

def get_xs(s, x):
    # find the indices of the non-zero elements of V
    indices = np.nonzero(s)[0]

    # select the columns of M with the non-zero indices
    xs = x[:, indices]

    return xs

def find_identical_columns(arr, names):
    _, idx, counts = np.unique(arr, axis=1, return_index=True, return_counts=True)
    unique_indices = sorted(idx)  # Ensure the order of columns is preserved

    # Extract the unique columns and their names
    unique_arr = arr[:, unique_indices]
    final_names = [names[i] for i in unique_indices]

    # Construct features_dict to reflect the relationship between unique columns and removed duplicates
    features_dict = {}
    for i, count in zip(idx, counts):
        if count > 1:  # If there are duplicates
            # Find all names that correspond to the same column as names[i]
            duplicates = [name for j, name in enumerate(names) if
                          arr[:, j].tolist() == arr[:, i].tolist() and j != i]
            features_dict[names[i]] = duplicates

    return unique_arr, features_dict, final_names