from typing import Optional, List

import numpy as np


class SortedSInformation:
    def __init__(self, all_s: np.array, all_w: np.array, feature_names: List[str], throw_away: float,
                 top_n_features: Optional[int] = None):
        self.all_s = all_s
        self.all_w = all_w
        self.feature_names = feature_names
        self.throw_away = throw_away
        self.top_n_features = min(top_n_features if top_n_features is not None else len(feature_names),
                                  len(feature_names))

        self.top_n_feature_names = None
        self.top_n_feature_indices = None
        self.top_n_feature_S_values = None
        self.W_after_throwout = None
        self.S_after_throwout = None
        self.top_n_feature_W_values = None

        self.sort_s_values()

    def sort_s_values(self):
        num_to_discard = int(self.throw_away * self.all_s.shape[1])
        self.S_after_throwout = self.all_s[:, num_to_discard:]


        N = self.top_n_features

        ones_count = np.sum(self.S_after_throwout, axis=1)
        sorted_indices = np.argsort(ones_count)[::-1][:N]
        self.top_n_feature_names = np.array(self.feature_names)[sorted_indices]
        self.top_n_feature_indices = sorted_indices

        self.W_after_throwout = self.all_w[:, num_to_discard:]
        self.top_n_feature_W_values = self.W_after_throwout[self.top_n_feature_indices, :]
        self.top_n_feature_S_values = self.S_after_throwout[self.top_n_feature_indices, :]