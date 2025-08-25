import numpy as np
from sklearn.linear_model import LinearRegression, LassoLars
from sklearn.metrics import r2_score


def lars_lasso_n_features(x_train, y_train, x_test, n_features):
    """
    Performs LARS-LASSO regression and picks up to n_features based on R²
    (among the set of active features across the Lasso path).

    Returns:
        (predictions for x_test, list of selected feature names)
    """
    model = LassoLars(alpha=1e-6, max_iter=1_000_000)
    model.fit(x_train, y_train)

    # Collect possible feature sets from the path
    feature_sets = []
    if model.coef_path_ is not None:
        for coef in model.coef_path_.T:  # Each column is a point in the path
            active_features = [
                x_train.columns[idx]
                for idx, value in enumerate(coef)
                if abs(value) > 1e-10
            ]
            # ensure uniqueness
            if active_features:
                feature_set_tuple = tuple(sorted(active_features))
                if feature_set_tuple not in [tuple(sorted(x)) for x in feature_sets]:
                    feature_sets.append(active_features)
    else:
        # Fallback if coef_path_ is None
        active_features = []
        for idx, value in enumerate(model.coef_):
            if abs(value) > 1e-10:
                active_features.append(x_train.columns[idx])
        if active_features:
            feature_sets.append(active_features)

    # Among all sets with up to n_features, find the one with the best R²
    best_r2 = -np.inf
    best_features = []

    for features in feature_sets:
        if len(features) > n_features:
            continue

        temp_model = LinearRegression()
        temp_model.fit(x_train[features], y_train)
        r2 = r2_score(y_train, temp_model.predict(x_train[features]))
        if r2 > best_r2:
            best_r2 = r2
            best_features = features

    # Predict with the best feature set
    final_model = LinearRegression()
    if best_features:
        final_model.fit(x_train[best_features], y_train)
        predictions = final_model.predict(x_test[best_features])
    else:
        # If no features, fallback to mean
        predictions = np.full(len(x_test), y_train.mean())

    return predictions, best_features