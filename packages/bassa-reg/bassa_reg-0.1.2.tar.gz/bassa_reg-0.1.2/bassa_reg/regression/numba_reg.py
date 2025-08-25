import pandas as pd
import numpy as np
from numba import jit
from typing import Optional


class NumbaRegressionCore:
    """
    Core regression class with numba-optimized OLS computations.
    """

    def __init__(self):
        self.coefficients: Optional[np.ndarray] = None
        self.intercept: Optional[float] = None
        self.fitted: bool = False

    @staticmethod
    @jit(nopython=True, cache=True)
    def _compute_ols_coefficients(X: np.ndarray, y: np.ndarray) -> np.ndarray:
        """
        Numba-optimized OLS coefficient computation.
        Uses the formula: β = (X^T X)^(-1) X^T y

        Args:
            X: Feature matrix (n_samples, n_features)
            y: Target vector (n_samples,)

        Returns:
            Coefficients array (n_features,)
        """
        # Compute X^T X
        XtX = np.dot(X.T, X)

        # Compute X^T y
        Xty = np.dot(X.T, y)

        # Solve the normal equation: (X^T X) β = X^T y
        coefficients = np.linalg.solve(XtX, Xty)

        return coefficients

    @staticmethod
    @jit(nopython=True, cache=True)
    def _predict_numba(X: np.ndarray, coefficients: np.ndarray) -> np.ndarray:
        """
        Numba-optimized prediction computation.

        Args:
            X: Feature matrix (n_samples, n_features)
            coefficients: Coefficient array (n_features,)

        Returns:
            Predictions array (n_samples,)
        """
        return np.dot(X, coefficients)

    def fit(self, X: np.ndarray, y: np.ndarray, fit_intercept: bool = True) -> None:
        """
        Fit the OLS regression model.

        Args:
            X: Feature matrix (n_samples, n_features)
            y: Target vector (n_samples,)
            fit_intercept: Whether to fit an intercept term
        """
        if fit_intercept:
            # Add intercept column (ones) to X
            X_with_intercept = np.column_stack((np.ones(X.shape[0]), X))
            all_coefficients = self._compute_ols_coefficients(X_with_intercept, y)
            self.intercept = all_coefficients[0]
            self.coefficients = all_coefficients[1:]
        else:
            self.coefficients = self._compute_ols_coefficients(X, y)
            self.intercept = 0.0

        self.fitted = True

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions using the fitted model.

        Args:
            X: Feature matrix (n_samples, n_features)

        Returns:
            Predictions array (n_samples,)
        """
        if not self.fitted:
            raise ValueError("Model must be fitted before making predictions.")

        # Use numba-optimized prediction
        predictions = self._predict_numba(X, self.coefficients)

        # Add intercept
        if self.intercept is not None:
            predictions += self.intercept

        return predictions


class NumbaRegression:
    """
    Main regression interface that handles pandas DataFrames and uses NumbaRegressionCore.
    """

    def __init__(self, fit_intercept: bool = True):
        self.core = NumbaRegressionCore()
        self.fit_intercept = fit_intercept
        self.feature_names_: Optional[list] = None
        self.fitted: bool = False

    def fit(self, x_train: pd.DataFrame, y_train: pd.DataFrame) -> 'NumbaRegression':
        """
        Fit the regression model.

        Args:
            x_train: Training features DataFrame
            y_train: Training targets DataFrame

        Returns:
            self for method chaining
        """
        # Convert to numpy arrays
        X = x_train.values.astype(np.float64)
        y = y_train.values.ravel().astype(np.float64)  # Flatten to 1D

        # Store feature names for reference
        self.feature_names_ = list(x_train.columns)

        # Fit the core model
        self.core.fit(X, y, fit_intercept=self.fit_intercept)
        self.fitted = True

        return self

    def predict(self, x_test: pd.DataFrame) -> np.ndarray:
        """
        Make predictions on test data.

        Args:
            x_test: Test features DataFrame

        Returns:
            Predictions array
        """
        if not self.fitted:
            raise ValueError("Model must be fitted before making predictions.")

        # Convert to numpy array
        X_test = x_test.values.astype(np.float64)

        # Make predictions using the core
        y_preds = self.core.predict(X_test)

        return y_preds

    @property
    def coefficients(self) -> Optional[np.ndarray]:
        """Get the fitted coefficients (excluding intercept)."""
        return self.core.coefficients

    @property
    def intercept(self) -> Optional[float]:
        """Get the fitted intercept."""
        return self.core.intercept

    def get_coefficients_df(self) -> Optional[pd.DataFrame]:
        """
        Get coefficients as a pandas DataFrame with feature names.

        Returns:
            DataFrame with feature names and coefficients
        """
        if not self.fitted:
            return None

        coef_data = []
        if self.intercept is not None and self.fit_intercept:
            coef_data.append({"feature": "intercept", "coefficient": self.intercept})

        if self.coefficients is not None and self.feature_names_ is not None:
            for name, coef in zip(self.feature_names_, self.coefficients):
                coef_data.append({"feature": name, "coefficient": coef})

        return pd.DataFrame(coef_data)


# Example usage:
if __name__ == "__main__":
    # Generate sample data
    np.random.seed(42)
    n_samples, n_features = 1000, 5

    X_data = np.random.randn(n_samples, n_features)
    true_coefficients = np.array([1.5, -2.0, 0.8, -0.5, 1.2])
    true_intercept = 3.0
    y_data = X_data @ true_coefficients + true_intercept + 0.1 * np.random.randn(n_samples)

    # Create DataFrames
    feature_names = [f"feature_{i}" for i in range(n_features)]
    x_train_df = pd.DataFrame(X_data, columns=feature_names)
    y_train_df = pd.DataFrame(y_data, columns=["target"])

    # Fit the model
    model = NumbaRegression(fit_intercept=True)
    model.fit(x_train_df, y_train_df)

    # Make predictions
    y_preds = model.predict(x_train_df)

    # Display results
    print("Coefficients DataFrame:")
    print(model.get_coefficients_df())
    print(f"\nTrue coefficients: {true_coefficients}")
    print(f"Fitted coefficients: {model.coefficients}")
    print(f"True intercept: {true_intercept}")
    print(f"Fitted intercept: {model.intercept}")
    print(f"Mean squared error: {np.mean((y_data - y_preds) ** 2):.6f}")