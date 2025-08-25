from matplotlib import pyplot as plt
import numpy as np

from bassa_reg.spike_and_slab.utils.latex_featname import latex_features
from bassa_reg.spike_and_slab.utils.sorted_s_model import SortedSInformation
import matplotlib as mpl

def create_markov_chain_visualization(s_information: SortedSInformation, path: str = None):
    mpl.rcParams['text.usetex'] = True
    S = np.asarray(s_information.top_n_feature_S_values)
    if S.ndim != 2:
        raise ValueError("top_n_feature_S_values must be a 2D array of shape (n_features, n_iterations).")

    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    im = ax.imshow(S, cmap='Greys', aspect='auto', interpolation='none')

    ax.set_title('MCMC Samples by Iterations')
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Top Features')

    names = latex_features(getattr(s_information, 'top_n_feature_names', None))
    if len(names) == S.shape[0]:
        ax.set_yticks(range(S.shape[0]))
        ax.set_yticklabels([rf"${name}$" for name in names])
    else:
        ax.set_yticks(range(S.shape[0]))

    if path is not None:
        fig.savefig(f"{path}/markov_chain_visualization.png", dpi=300)

    return fig, ax

if __name__ == "__main__":
    np.random.seed(0)

    n_features = 10
    n_samples = 16000

    # Example: assign a different probability of 1 to each feature
    probs = np.linspace(0.1, 0.9, n_features)  # from 10% to 90%
    all_s = (np.random.rand(n_features, n_samples) < probs[:, None]).astype(int)
    all_w = np.random.randn(n_features, n_samples)
    feature_names = [f"$\\mathrm{{s}}_{{{i+1}}}$" for i in range(n_features)]

    s_info = SortedSInformation(all_s, all_w, feature_names, throw_away=0.2, top_n_features=10)
    fig_test, ax_test = create_markov_chain_visualization(s_info)
    plt.show()