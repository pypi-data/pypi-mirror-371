import os
import warnings
import pandas as pd
import numpy as np
from sklearn.model_selection import KFold

from bassa_reg.bassa import Bassa, BassaConfigurations
from bassa_reg.spike_and_slab.spike_and_slab import SpikeAndSlabConfigurations, SpikeAndSlabRegression
from bassa_reg.spike_and_slab.spike_and_slab_util_models import SpikeAndSlabPriors, TestSet
from bassa_reg.spike_and_slab.utils.util_functions import get_date_for_experiment_name
from expreiments.case_study_1.model_exploration import data_preparation
from expreiments.utils.forward_regression import forward_regression_n_features
from expreiments.utils.lasso_regression import lars_lasso_n_features
from sklearn.exceptions import ConvergenceWarning

warnings.filterwarnings("ignore", category=ConvergenceWarning)

if __name__ == '__main__':
    name = 'Dataset_2019_JPR'
    np.random.seed(42)
    # data preparation
    x, y = data_preparation()

    # how many folds to create
    folds = 3

    # how many times to repeat the folds
    fold_repetitions = 3

    # how many extrapolation datasets to create
    extrapolation_steps = 0

    # how many samples to add in each extrapolation step
    extrapolation_step_length = 4

    # how many features to add to the lasso/forward stepwise regression
    feature_counts = [5, 6, 7, 8, 9, 11, 12, 13]

    priors = SpikeAndSlabPriors(
        a_alpha_prior=1,
        a_beta_prior=10,
        sigma_alpha_prior=10,
        sigma_beta_prior=10,
        tau_beta_prior=1,
        tau_alpha_prior=0.1,
    )

    datasets = []
    results = []

    for i in range(fold_repetitions):
        kf = KFold(n_splits=folds, shuffle=True, random_state=42 + i)
        fold = 1
        for train_index, val_index in kf.split(x):
            X_train, X_test = x.iloc[train_index].copy(), x.iloc[val_index].copy()
            y_train, y_test = y.iloc[train_index].copy(), y.iloc[val_index].copy()
            datasets.append((X_train, X_test, y_train, y_test, f"run_{i}_fold_{fold}"))
            fold += 1

    base_size = int(0.2 * len(y))

    extrap_directions = [(False, "top"), (True, "bottom")]
    for extrap, direction in extrap_directions:
        y_sorted = y.sort_values(ascending=extrap)
        x_sorted = x.reindex(y_sorted.index)

        for current_size in range(base_size, base_size + extrapolation_step_length * extrapolation_steps, extrapolation_step_length):
            X_test = x_sorted.iloc[:current_size]
            y_test = y_sorted.iloc[:current_size]
            X_train = x_sorted.iloc[current_size:]
            y_train = y_sorted.iloc[current_size:]

            datasets.append((X_train, X_test, y_train, y_test,
                             f"extrap_{direction}_{current_size}"))

    exp_dir = os.path.dirname(os.path.abspath(__file__))
    metrics_dir = os.path.join(exp_dir, f"metrics_{get_date_for_experiment_name()}")
    os.makedirs(metrics_dir, exist_ok=True)

    results_list = []
    for dataset in datasets:
        dataset_x_train = dataset[0]
        dataset_x_test = dataset[1]
        dataset_y_train = dataset[2]
        dataset_y_test = dataset[3]
        dataset_name = dataset[4]

        spike_and_slab_test_set = TestSet(x_test=dataset_x_test,
                                          samples_per_y=50, iterations=100)

        config = SpikeAndSlabConfigurations(sampler_iterations=1000,
                                            dont_save_anything=True)

        abs_dir = os.path.dirname(os.path.abspath(__file__))
        regression = SpikeAndSlabRegression(x=dataset_x_train,
                                            y=dataset_y_train,
                                            priors=priors,
                                            config=config,
                                            test_set=spike_and_slab_test_set,
                                            project_path=abs_dir,
                                            experiment_name=name,)
        regression.run()
        spike_and_slab_predictions = regression.test_set.y_pred
        mse_result_spike_and_slab = np.mean((dataset_y_test - spike_and_slab_predictions) ** 2)
        result_dict = {"dataset": dataset_name, "mcmc_mse": float(round(mse_result_spike_and_slab,5))}

        print(f"Running lasso and forward regression for dataset: {dataset_name}")
        for feature_count in feature_counts:
            forward_predictions, selected_features = forward_regression_n_features(x_train=dataset_x_train,
                                                                                   y_train=dataset_y_train,
                                                                                   x_test=dataset_x_test,
                                                                                   n_features=feature_count)
            mse_result_regression = np.mean((dataset_y_test - forward_predictions) ** 2)
            result_dict[f"forward_{feature_count}"] = float(round(mse_result_regression,5))

            lasso_predictions, lasso_features = lars_lasso_n_features(x_train=dataset_x_train,
                                                                                   y_train=dataset_y_train,
                                                                                   x_test=dataset_x_test,
                                                                                   n_features=feature_count)
            mse_result_lasso = np.mean((dataset_y_test - lasso_predictions) ** 2)
            result_dict[f"lasso_{feature_count}"] = float(round(mse_result_lasso,5))

        results_list.append(result_dict)


    results_df = pd.DataFrame(results_list)
    results_df.to_csv(os.path.join(metrics_dir, "prediction_results.csv"), index=False)




