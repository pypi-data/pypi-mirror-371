import re
from enum import Enum
import os

import pandas as pd
import numpy as np
from bassa_reg.bassa import Bassa, BassaConfigurations
from bassa_reg.spike_and_slab.spike_and_slab import SpikeAndSlabConfigurations, SpikeAndSlabRegression
from bassa_reg.spike_and_slab.spike_and_slab_util_models import SpikeAndSlabPriors


class CaseStudy3DataSet(Enum):
    AnatSi = 'Anat_SI.csv'
    RDKit = 'rdkit_fingerprints_new.csv'
    Kraken = 'yonatan_kraken_new.csv'

def get_priors(dataset_for_priors: CaseStudy3DataSet):
    if dataset_for_priors == CaseStudy3DataSet.AnatSi:
        return SpikeAndSlabPriors(
                a_alpha_prior=1,
                a_beta_prior=6,
                sigma_alpha_prior=3,
                sigma_beta_prior=3,
                tau_beta_prior=1,
                tau_alpha_prior=1,
            )
    elif dataset_for_priors == CaseStudy3DataSet.RDKit:
        return SpikeAndSlabPriors(
                a_alpha_prior=1,
                a_beta_prior=6,
                sigma_alpha_prior=3,
                sigma_beta_prior=3,
                tau_beta_prior=1,
                tau_alpha_prior=0.1,
            )
    elif dataset_for_priors == CaseStudy3DataSet.Kraken:
        return SpikeAndSlabPriors(
            a_alpha_prior=1,
            a_beta_prior=2,
            sigma_alpha_prior=1,
            sigma_beta_prior=1,
            tau_beta_prior=1,
            tau_alpha_prior=1,
        )

    else:
        raise ValueError("Unknown dataset")

def data_preparation(chosen_dataset: CaseStudy3DataSet):
    path = chosen_dataset.value
    data = pd.read_csv(path)
    y = data['measured ddG']
    data.drop(['ligand name', 'measured ddG'], axis=1, inplace=True)
    try:
        data.drop(['Measured ddG'], axis=1, inplace=True)
    except KeyError:
        pass

    if chosen_dataset == CaseStudy3DataSet.Kraken:
        data = data.drop('pyr_alpha_boltz', axis=1)
        data = data.drop('Kraken ID', axis=1)
        data = data.drop("Cone angle(article)", axis=1)
        data = data.drop("smiles", axis=1)

    elif chosen_dataset == CaseStudy3DataSet.AnatSi:
        data = data.drop("smiles", axis=1)

    elif chosen_dataset == CaseStudy3DataSet.RDKit:
        data = data.drop(columns=["BCUT2D_CHGHI", "BCUT2D_CHGLO", 'mol'], axis=1)
        data = data.drop("SMILES", axis=1)

    x = data
    return x, y

if __name__ == '__main__':
    dataset = CaseStudy3DataSet.RDKit
    name = dataset.value
    np.random.seed(42)
    # data preparation
    x_data, y_data = data_preparation(dataset)
    priors = get_priors(dataset)

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
    bassa.run(BassaConfigurations(max_restriction=20,
                                  min_points=2,
                                  metric_threshold=0.7,
                                  percentage_cutoff=0.01))