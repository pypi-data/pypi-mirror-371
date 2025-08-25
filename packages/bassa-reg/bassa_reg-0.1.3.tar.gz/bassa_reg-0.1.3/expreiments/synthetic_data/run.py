import os

import numpy as np
import pandas as pd

from bassa_reg import Bassa, BassaConfigurations
from bassa_reg.spike_and_slab.spike_and_slab import SpikeAndSlabRegression, SpikeAndSlabConfigurations
from bassa_reg.spike_and_slab.spike_and_slab_util_models import SpikeAndSlabPriors

# Generate random features
np.random.seed(43)
N = 100
M = 4
K = 2
coefficients = np.array([0.22, 0.055])  # Coefficients for the K features
noise_level = 0.13

X = pd.DataFrame(np.random.randn(N, M), columns=[f's_{i+1}' for i in range(M)])

# Generate linear coefficients for K features
Y = X.iloc[:, :K].dot(coefficients) + np.random.randn(N) * noise_level
Y = pd.Series(Y)

# Run the regression
print("Running regression")
priors = SpikeAndSlabPriors()
config = SpikeAndSlabConfigurations()
abs_dir = os.path.dirname(os.path.abspath(__file__))
regression = SpikeAndSlabRegression(x=X,
                          y=Y,
                          priors=priors,
                          project_path=abs_dir,
                          experiment_name="Paper Synthetic Dataset")
regression.run()
bassa_config = BassaConfigurations(min_points=0, percentage_cutoff=0, metric_threshold=0, max_restriction=M)
bassa = Bassa(model=regression, )
bassa.run(config=bassa_config)