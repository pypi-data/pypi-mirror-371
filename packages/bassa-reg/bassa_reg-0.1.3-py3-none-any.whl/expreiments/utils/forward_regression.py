import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score


def forward_regression_n_features(x_train, y_train, x_test, n_features):
    selected_features = []
    remaining_features = list(x_train.columns)
    best_r2 = -np.inf

    for _ in range(min(n_features, len(x_train.columns))):
        best_new_r2 = best_r2
        best_new_feature = None

        for feature in remaining_features:
            features_to_try = selected_features + [feature]
            model = LinearRegression()
            model.fit(x_train[features_to_try], y_train)
            r2 = r2_score(y_train, model.predict(x_train[features_to_try]))
            if r2 > best_new_r2:
                best_new_r2 = r2
                best_new_feature = feature

        if best_new_feature is not None:
            selected_features.append(best_new_feature)
            remaining_features.remove(best_new_feature)
            best_r2 = best_new_r2
        else:
            break

    # Make predictions on x_test
    final_model = LinearRegression()
    if selected_features:
        final_model.fit(x_train[selected_features], y_train)
        predictions = final_model.predict(x_test[selected_features])
    else:
        # If no features were selected, predict mean
        predictions = np.full(len(x_test), y_train.mean())

    return predictions, selected_features