import os

import pandas as pd
import numpy as np
from bassa_reg.bassa import Bassa, BassaConfigurations
from bassa_reg.spike_and_slab.spike_and_slab import SpikeAndSlabConfigurations, SpikeAndSlabRegression
from bassa_reg.spike_and_slab.spike_and_slab_util_models import SpikeAndSlabPriors

def data_preparation():
    cols_to_remove = ['benzaldehyde', "Rate", "log(Rate)"]
    path = f"dataset_case_study_2.csv"
    df = pd.read_csv(path)
    df = df.dropna()
    y = df['log(Rate)']
    df.drop(cols_to_remove, axis=1, inplace=True)
    x = df
    return x, y


if __name__ == '__main__':
    name = 'Deuteration'
    np.random.seed(42)
    # data preparation
    x_data, y_data = data_preparation()

    priors = SpikeAndSlabPriors(a_alpha_prior=1,
                                a_beta_prior=10,
                                tau_alpha_prior=2,
                                tau_beta_prior=1,
                                sigma_alpha_prior=2,
                                sigma_beta_prior=1)

    config = SpikeAndSlabConfigurations(sampler_iterations=20000,
                                        save_meta_data=True,
                                        save_samples=False)

    abs_dir = os.path.dirname(os.path.abspath(__file__))
    regression = SpikeAndSlabRegression(x=x_data,
                                y=y_data,
                                priors=priors,
                                config=config,
                                project_path=abs_dir,
                                experiment_name=name,)

    regression.run()
    bassa = Bassa(model=regression)
    bassa.run(BassaConfigurations(max_restriction=15,
                                  min_points=2,
                                  metric_threshold=0.7,
                                  percentage_cutoff=0.01))