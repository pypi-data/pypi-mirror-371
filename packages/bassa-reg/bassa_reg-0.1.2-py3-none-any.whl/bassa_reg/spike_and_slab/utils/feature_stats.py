import pandas as pd
import numpy as np

from bassa_reg.spike_and_slab.utils.sorted_s_model import SortedSInformation

def save_feature_stats_to_csv(s_information : SortedSInformation, path: str):
    S = s_information.S_after_throwout

    ones_count = np.sum(S, axis=1)
    relative_occurrence = np.round(ones_count / S.shape[1], 3)

    # Initialize an array to store stand-alone occurrences
    stand_alone_occurrence = np.zeros_like(ones_count)

    # Check each row in S and count rows with exactly one '1'
    single_one_vectors_count = 0
    for i in range(S.shape[1]):
        column_vector = S[:, i]
        if np.sum(column_vector) == 1:  # Only one feature is '1'
            single_one_vectors_count += 1
            # Find the index of that '1' and increment the corresponding count
            index = np.where(column_vector == 1)[0][0]
            stand_alone_occurrence[index] += 1

    # Handle case where no single '1' vectors exist
    if single_one_vectors_count == 0:
        stand_alone_occurrence = np.zeros_like(ones_count)

    # Calculate the ratio of stand-alone occurrence to total single '1' vectors
    if single_one_vectors_count > 0:
        ratio_single_occurrence = stand_alone_occurrence / single_one_vectors_count
    else:
        ratio_single_occurrence = np.zeros_like(ones_count)

    # Round ratio_single_occurrence 3 digits
    ratio_single_occurrence = np.round(ratio_single_occurrence, 3)

    df = pd.DataFrame({
        'feature name': s_information.feature_names,
        'relative occurrence': relative_occurrence,
        # 'stand-alone occurrence': stand_alone_occurrence,
        # 'total single 1 vectors': single_one_vectors_count,  # This will be the same for all rows
        # 'ratio of stand-alone to single 1 vectors': ratio_single_occurrence
    })

    # Sort the data frame
    df = df.sort_values(by='relative occurrence', ascending=False)

    # Save to CSV
    df.to_csv(f"{path}/feature_stats.csv", index=False)