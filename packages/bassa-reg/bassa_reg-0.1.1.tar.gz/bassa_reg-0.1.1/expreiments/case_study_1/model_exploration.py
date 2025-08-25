import os

import pandas as pd
import numpy as np
from bassa_reg.bassa import Bassa, BassaConfigurations
from bassa_reg.spike_and_slab.spike_and_slab import SpikeAndSlabConfigurations, SpikeAndSlabRegression
from bassa_reg.spike_and_slab.spike_and_slab_util_models import SpikeAndSlabPriors


def data_preparation():
    cols_to_remove = ['Rxn_Type', 'Imine', 'Nucleophile',
                      'Catalyst_Ar_grp', "Temp", "Catalyst_Loading", 'Solvent', "ddG"]
    path = f"dataset_case_study_1.csv"
    df = pd.read_csv(path)
    df = df.dropna()
    y = df['ddG']
    df.drop(cols_to_remove, axis=1, inplace=True)
    x = df
    return x, y

if __name__ == '__main__':
    name = 'Dataset_2019_JPR'
    np.random.seed(42)
    # data preparation
    x_data, y_data = data_preparation()

    priors = SpikeAndSlabPriors(
        a_alpha_prior=1,
        a_beta_prior=10,
        sigma_alpha_prior=10,
        sigma_beta_prior=10,
        tau_beta_prior=1,
        tau_alpha_prior=0.1,
    )

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
    bassa.run(BassaConfigurations(min_points=3,
                                  metric_threshold=0.7,
                                  percentage_cutoff=0.015))
