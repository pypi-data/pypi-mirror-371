import math

import matplotlib.pyplot as plt
import numpy as np
from typing import List, Union
from collections import Counter
from matplotlib import rc
from matplotlib.lines import Line2D
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import statsmodels.api as sm
import pandas as pd
from sklearn.metrics import r2_score
from sklearn.model_selection import LeaveOneOut
from tqdm import tqdm

from bassa_reg.spike_and_slab.utils.sorted_s_model import SortedSInformation

rc('text', usetex=False)
rc('font', family='serif')

plt.rcParams.update({
    'font.size': 12,
    'axes.titlesize': 14,
    'axes.labelsize': 14,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'legend.fontsize': 12
})

def calculate_q2(X, y):
    # X and y should be pandas DataFrame/Series
    # Add constant for OLS
    X = sm.add_constant(X)
    loo = LeaveOneOut()
    predictions = []
    samples = []
    for train_index, test_index in loo.split(X):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train = y.iloc[train_index]
        # Fit the model
        model = sm.OLS(y_train, X_train, hasconst=True).fit()
        pred = model.predict(X_test)
        y_test = y.iloc[test_index]
        predictions.append(pred.values[0])
        samples.append(y_test.values[0])

    r2 = r2_score(samples, predictions)
    return r2

class SurvivalSample:
    """
    Simple class to store data for each 'sample' or 'curve'.

    Arguments
    ---------
    name : str
        Name or identifier for the sample (optional but useful for legends).
    feature_names : list of str
        Names of the features included in this sample.
    x_values : list of floats
        The X-axis values.
    y_values : list of floats
        The Y-axis values.
    num_features : int
        The number of features in this combination (often used for line thickness or other plotting).
    q2 : float
        The leave-one-out R^2 (q^2).
    r2 : float
        The standard R^2 from an OLS fit on the entire dataset.
    mae : float
        Mean Absolute Error for the OLS fit.
    mse : float
        Mean Squared Error for the OLS fit.
    """

    def __init__(
        self,
        name: str,
        feature_names: List[str],
        x_values: List[float],
        y_values: List[float],
        num_features: int,
        q2: float,
        r2: float,
        mae: float,
        mse: float,
        ratio: float
    ):
        self.name = name
        self.feature_names = feature_names
        self.x_values = x_values
        self.y_values = y_values
        self.num_features = num_features
        self.q2 = q2
        self.r2 = r2
        self.mae = mae
        self.mse = mse
        self.ratio = ratio


def create_survival_samples(
        x: np.array,
        y: np.array,
        feature_names: List[str],
        s_info: SortedSInformation,
        max_restriction: int,
        percentage_cutoff: float,
        r2_value_to_drop_model: Union[float, None] = None,
        start: Union[int, None] = None,
        end: Union[int, None] = None,
        add_empty: bool = False
) -> List[SurvivalSample]:
    """
    Generates a list of SurvivalSample objects by scanning the MCMC chain
    for each integer 'restriction' n in [1, max_restriction].

    For each n:
      1) Look only at the first n 'top features' (rows) in the MCMC matrix slice.
      2) Count how often each combination (0/1 pattern) appears.
      3) Convert that count into a percentage (relative to the total columns in the slice).
      4) If the percentage is >= percentage_cutoff, record a SurvivalSample
         for that combination with its metrics (q^2, r^2, MAE, MSE).

    This version now **includes** the empty model (all-zero combination), labeled as "{empty}".
    """

    # Convert x and y to DataFrame / Series for easy OLS computations
    X_df = pd.DataFrame(x, columns=feature_names)
    y_series = pd.Series(y)

    # Grab the matrix of top-feature inclusions
    # Shape: (number_of_top_features, number_of_MCMC_samples)
    S = s_info.top_n_feature_S_values
    top_feature_names = s_info.top_n_feature_names

    # If start/end not provided, use full range
    if start is None:
        start = 0
    if end is None:
        end = S.shape[1]

    # Slice the columns (MCMC samples)
    S_slice = S[:, start:end]
    total_columns = S_slice.shape[1]  # how many MCMC samples in the chosen slice

    # We'll keep a dictionary that maps from combo_name -> SurvivalSample
    survival_dict = {}

    # For each possible "restriction" n in [1..max_restriction]
    for n in tqdm(range(1, max_restriction + 1)):
        if n > S_slice.shape[0]:
            # If n exceeds the number of available top features, stop
            break

        # shape -> (n, total_columns).T -> (total_columns, n)
        restricted_s_vectors = S_slice[:n, :].T

        # Convert each row (e.g. [0,1,1,...]) into a tuple
        combination_arr = [tuple(row) for row in restricted_s_vectors]

        # Count how many times each combination appears
        combination_counts = Counter(combination_arr)

        # For each unique combination
        for combo, count in combination_counts.items():
            fraction = count / total_columns

            # Only process if fraction above threshold
            if fraction >= percentage_cutoff:
                # Identify which features are active
                active_features = [
                    top_feature_names[i] for i in range(n) if combo[i] == 1
                ]

                # -----------------------------
                # **New**: if sum(combo) == 0,
                # label as "{empty}" rather than skipping
                # -----------------------------
                if sum(combo) == 0:
                    combo_name = "{empty}"
                    if not add_empty:
                        continue
                else:
                    combo_name = ", ".join(active_features)

                # If we haven't seen this combination yet, compute its metrics and store
                if combo_name not in survival_dict:
                    # Compute q^2
                    X_sub = X_df[active_features]  # will be empty if sum(combo) == 0
                    q2_val = calculate_q2(X_sub, y_series)

                    # OLS for R^2, MSE, and MAE
                    X_sub_const = sm.add_constant(X_sub, has_constant='add')
                    model = sm.OLS(y_series, X_sub_const).fit()
                    preds = model.predict(X_sub_const)

                    r2_val = r2_score(y_series, preds)

                    if r2_value_to_drop_model is not None and r2_val < r2_value_to_drop_model:
                        continue

                    mse_val = mean_squared_error(y_series, preds)
                    mae_val = mean_absolute_error(y_series, preds)

                    survival_dict[combo_name] = SurvivalSample(
                        name=combo_name,
                        feature_names=active_features,
                        x_values=[],
                        y_values=[],
                        num_features=sum(combo),  # 0 if empty
                        q2=q2_val,
                        r2=r2_val,
                        mae=mae_val,
                        mse=mse_val,
                        ratio=fraction
                    )

                # Append new (n, fraction) to the existing SurvivalSample
                survival_dict[combo_name].x_values.append(n)
                survival_dict[combo_name].y_values.append(fraction * 100)

    # Return the aggregated samples
    return list(survival_dict.values())


def survival_chart(
        samples: List[SurvivalSample],
        path: str,
        min_points: int = 0
) -> None:
    """Plot the survival chart with lines labeled 'Model 1', 'Model 2', etc., and save as PNG."""
    # Filter
    filtered = [s for s in samples if len(s.x_values) > min_points]
    if not filtered:
        print(f"No samples have more than {min_points} points.")
        return

    # Create figure
    fig, ax = plt.subplots(figsize=(6, 5))

    # Determine min/max for x, y
    min_x = min(min(s.x_values) for s in filtered)
    max_x = max(max(s.x_values) for s in filtered)
    min_y = min(min(s.y_values) for s in filtered)
    max_y = max(max(s.y_values) for s in filtered)

    # Color map
    colors = plt.cm.viridis(np.linspace(0, 1, len(filtered)))

    # Plot lines
    for i, (sample, color) in enumerate(zip(filtered, colors), start=1):
        ax.plot(
            sample.x_values,
            sample.y_values,
            label=f"Model {i}",
            linewidth=2,
            color=color
        )
        ax.scatter(
            sample.x_values,
            sample.y_values,
            color=color,
            edgecolors="black",
            s=50,
            zorder=3
        )

    ax.set_title("Survival Curves")
    ax.set_xlabel("Features")
    ax.set_ylabel("Combination Inclusion (%)")

    # Pad y-range
    y_padding = 0.05 * (max_y - min_y)
    ax.set_ylim(min_y - y_padding, max_y + y_padding)

    # Set x-ticks if integral
    ax.set_xlim(min_x, max_x)
    ax.set_xticks(range(int(min_x), int(max_x) + 1))

    ax.legend(loc="upper right")

    plt.tight_layout()
    plt.savefig(f"{path}/survival_chart.png", dpi=300)
    plt.close(fig)


def save_survival_table(
        samples: List[SurvivalSample],
        path: str,
        min_points: int = 0
) -> None:
    """
    Generate a CSV file containing the survival analysis data using pandas
    """
    filtered = [s for s in samples if len(s.x_values) > min_points]
    if not filtered:
        print(f"No samples have more than {min_points} points.")
        return

    # Create DataFrame with automatic model numbering and formatted values
    df = pd.DataFrame([{
        "Model": f"Model {i}",
        "Features": sample.name,
        "R^2": f"{sample.r2:.4f}",
        "Q^2": f"{sample.q2:.4f}",
        "MSE": f"{sample.mse:.4f}",
        "MAE": f"{sample.mae:.4f}"
    } for i, sample in enumerate(filtered, start=1)])

    # Save to CSV with proper path handling
    df.to_csv(f"{path}/survival_table.csv", index=False)