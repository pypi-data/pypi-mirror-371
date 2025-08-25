import numpy as np
import matplotlib.pyplot as plt

from bassa_reg.spike_and_slab.spike_and_slab_util_models import GewekeConfiguration


def geweke_plot(geweke_pairs: list, config: GewekeConfiguration):
    # Create the Gweke plot
    names = ["Sigma", "Tau", "a", "Number of S's"]
    fig, axes = plt.subplots(nrows=len(names), ncols=2, figsize=(12, 20))

    for i in range(len(names)):
        ax1 = axes[i, 0]
        ax2 = axes[i, 1]

        # Flatten the vectors
        data = geweke_pairs[i]

        throw_away = int(len(data) * config.throw_away)
        data = data[throw_away:]
        if names[i] == "Number of S's":
            x = np.array([pair[0] for pair in data])
            y = np.array([pair[1] for pair in data])
        else:
            x = [pair[0] for pair in data]
            y = [pair[1] for pair in data]

        # Define bin edges for the histograms
        if names[i] == 'a':
            bins = np.arange(min(x), max(x) + config.a_bin_size, config.a_bin_size)
        elif names[i] != 'W Distributions':
            bins = np.arange(min(x), max(x) + config.default_bin_size, config.default_bin_size)

        # Create the histograms
        hist1, bin_edges, _ = ax1.hist(x, bins=bins, alpha=0.5, density=True,
                                       label=f'{names[i]} From Chain (Mean: {str(round(np.mean(x), 4))}, STD: {str(round(np.std(x), 4))})')

        if names[i] == 'a':
            bins = np.arange(min(y), max(y) + config.a_bin_size, config.a_bin_size)
        elif names[i] != 'W Distributions':
            bins = np.arange(min(y), max(y) + config.default_bin_size, config.default_bin_size)

        hist2, bin_edges, _ = ax1.hist(y, bins=bins, alpha=0.5, density=True,
                                       label=f'{names[i]} From Priors (Mean: {str(round(np.mean(y), 4))}, STD: {str(round(np.std(y), 4))})')
        ax1.set_xlabel(f'Distribution of {names[i]}')
        ax1.set_title(f'Distribution Histograms - {names[i]}')
        ax1.legend()

        # Add Q-Q plot
        prior_quantiles = np.quantile(x, np.arange(0, 1, 0.01))
        posterior_quantiles = np.quantile(y, np.arange(0, 1, 0.01))

        ax2.scatter(x=prior_quantiles, y=posterior_quantiles, label='Actual fit')
        ax2.plot(prior_quantiles, prior_quantiles, color='red', label='Line of perfect fit')
        ax2.set_xlabel(f'Quantile of {names[i]} from Prior')
        ax2.set_ylabel(f'Quantile of {names[i]} from Chain')
        ax2.legend()
        ax2.set_title(f"QQ plot - {names[i]}")

    fig.subplots_adjust(hspace=0.5)
    # Show the plot
    plt.show()
