from typing import List

import pandas as pd
from upsetplot import UpSet, from_memberships
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.lines import Line2D
import warnings

from bassa_reg.spike_and_slab.bassa_survival import SurvivalSample
from bassa_reg.spike_and_slab.utils.bassa_enums import SurvivalMetric
from bassa_reg.spike_and_slab.utils.latex_featname import latex_features

warnings.filterwarnings("ignore", category=FutureWarning)

def generate_upset_plot(data_survival: List[SurvivalSample], metric: SurvivalMetric, path: str = None):
    mpl.rcParams.update({
        "text.usetex": True,
        "font.family": "serif",
        "font.serif": ["Computer Modern Roman"],
    })

    for sample in data_survival:
        sample.feature_names = latex_features(sample.feature_names)

    bar_color = "black"
    text_color = "black"

    # ───────────────────  Data  ───────────────────
    data = {
        "Features": [
        ],
        "R2": [
        ],
        "Q2": [

        ],
        "MSE": [
        ],
        "MAE": []
    }

    for sample in data_survival:
        data["Features"].append(",".join(sample.feature_names))
        data["R2"].append(sample.r2)
        data["Q2"].append(sample.q2)
        data["MSE"].append(sample.mse)
        data["MAE"].append(sample.mae)

    df = pd.DataFrame(data)

    # ───────────────────  helper: raw → LaTeX  ───────────────────


    # memberships (LaTeX strings so tick labels look nice)
    memberships = [
        tuple(sorted(f.strip() for f in row.split(",")))
        for row in df["Features"]
    ]


    metric_name = r"$R^2$"
    if metric == SurvivalMetric.R2:
        upset_data = from_memberships(memberships, data=df["R2"])
    elif metric == SurvivalMetric.Q2:
        upset_data = from_memberships(memberships, data=df["Q2"])
        metric_name = r"$Q^2$"
    else:
        upset_data = from_memberships(memberships, data=df["R2"])

    # ────────────────  Build the UpSet object first  ────────────────
    upset = UpSet(
        upset_data,
        show_counts="%.3f",
        sort_by="cardinality",
        totals_plot_elements=0,
        facecolor=bar_color,
        other_dots_color=0.12,
        shading_color=0.0,
        with_lines=False,
    )

    degrees = upset.intersections.index.to_frame().sum(axis=1).astype(int)
    unique_deg = sorted(degrees.unique())

    def is_grayish(rgba, threshold=0.05):
        r, g, b = rgba[:3]
        return abs(r - g) < threshold and abs(g - b) < threshold and abs(r - b) < threshold

    base_cmap = mpl.colormaps.get_cmap("Set2")
    norm = mpl.colors.Normalize(vmin=min(unique_deg), vmax=max(unique_deg))

    def pastel(rgba, w=1):
        r, g, b, _ = rgba
        return (1 - w) + w * r, (1 - w) + w * g, (1 - w) + w * b, 1.0

    valid_colors = [
        pastel(base_cmap(i / (base_cmap.N - 1)))
        for i in range(base_cmap.N)
        if not is_grayish(base_cmap(i / (base_cmap.N - 1)))
    ]

    for d, colour in zip(unique_deg, valid_colors):
        upset.style_subsets(
            min_degree=d,
            max_degree=d,
            facecolor=colour,
            edgecolor=colour,
        )

    upset.plot()
    fig = plt.gcf()
    fig.set_size_inches(10, 6)

    for ax in fig.get_axes():
        if ax.get_ylabel() == "Intersection size":
            ax.set_ylabel(fr"Model {metric_name} Value", color=text_color)
            ax.grid(False)
            ax.set_yticks([])
        ax.tick_params(axis="x", colors=text_color)
        ax.tick_params(axis="y", colors=text_color)
        for line in ax.lines:
            line.set_color(text_color)
        for txt in ax.texts:
            txt.set_color(text_color)
        for spine in ax.spines.values():
            spine.set_edgecolor(text_color)

    plt.subplots_adjust(bottom=0.12, left=0.05)
    legend_handles = [
        Line2D([0], [0],
               marker='o', linestyle='None',
               markerfacecolor=color, markeredgecolor='none', markersize=10,
               label=str(degree))
        for degree, color in zip(unique_deg, valid_colors)
    ]

    fig = plt.gcf()
    legend_ax = fig.add_axes((0.05, 0.02, 0.90, 0.15))
    legend_ax.axis("off")

    legend_ax.legend(handles=legend_handles,
                     title=r"Number of Features",
                     ncol=len(legend_handles),
                     loc="center",
                     frameon=False)

    if path is not None:
        plt.savefig(f"{path}/bassa_plot.png", dpi=300)
