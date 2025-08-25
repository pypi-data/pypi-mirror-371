from typing import List

from .spike_and_slab.bassa_survival import create_survival_samples, survival_chart, save_survival_table
from .spike_and_slab.spike_and_slab import SpikeAndSlabRegression
from .spike_and_slab.utils.bassa_enums import SurvivalMetric
from .spike_and_slab.utils.chain_visualization import create_markov_chain_visualization
from .spike_and_slab.utils.feature_stats import save_feature_stats_to_csv
from .spike_and_slab.utils.sorted_s_model import SortedSInformation
from .spike_and_slab.utils.upsert_plot import generate_upset_plot

class BassaOutputConfigurations:
    def __init__(self,
                 output_upset_plot: bool = True,
                 output_survival_chart: bool = True,
                 output_survival_table: bool = True,
                 output_feature_stats: bool = True,
                 output_markov_chain: bool = True):
        self.upset_plot = output_upset_plot
        self.survival_chart = output_survival_chart
        self.survival_table = output_survival_table
        self.feature_stats = output_feature_stats
        self.markov_chain = output_markov_chain


class BassaConfigurations:
    def __init__(self,
                 min_points=2,
                 max_restriction=20,
                 top_n_features: int = 20,
                 percentage_cutoff = 0.05,
                 metric_threshold=0.5,
                 throw_out_ratio: float = 0.20,
                 metric: SurvivalMetric = SurvivalMetric.R2,
                 output_config: BassaOutputConfigurations = BassaOutputConfigurations()):
        self.min_points = min_points
        self.max_restriction = max_restriction
        self.percentage_cutoff = percentage_cutoff
        self.metric_threshold = metric_threshold
        self.metric = metric
        self.output_config = output_config
        self.throw_out_ratio = throw_out_ratio
        self.top_n_features = top_n_features



class Bassa:
    def __init__(self, model : SpikeAndSlabRegression):

        self.model = model
        if not model.finished:
            raise ValueError("You must run the model one before using Bassa.")

        self.top_n_features = None
        self.s_information = None
        self.scaler_y = model.scaler_y
        self.full_name = model.full_experiment_name
        self.path = model.project_path + f"/{model.full_experiment_name}"

    def run(self,
            config: BassaConfigurations = BassaConfigurations()):

        self.top_n_features = min(config.top_n_features if config.top_n_features is not None else self.model.x.shape[1],
                                  self.model.x.shape[1])
        self.s_information = SortedSInformation(self.model.all_s, self.model.all_w,
                                                self.model.feature_names, config.throw_out_ratio, config.top_n_features)

        ls = create_survival_samples(self.model.x,self.model.y, self.model.feature_names, self.s_information,
                                     config.max_restriction, config.percentage_cutoff,
                                     r2_value_to_drop_model=config.metric_threshold, start=None, end=None)

        if config.output_config.survival_chart:
            survival_chart(ls, self.path, min_points=config.min_points)

        if config.output_config.survival_table:
            save_survival_table(ls, self.path, min_points=config.min_points)

        if config.output_config.upset_plot:
            generate_upset_plot(ls, config.metric, self.path)

        if config.output_config.feature_stats:
            save_feature_stats_to_csv(self.s_information, self.path)

        if config.output_config.markov_chain:
            create_markov_chain_visualization(self.s_information, self.path)