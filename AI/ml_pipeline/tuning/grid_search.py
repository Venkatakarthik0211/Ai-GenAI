"""GridSearchCV wrapper for hyperparameter tuning."""

from sklearn.model_selection import GridSearchCV
from typing import Dict, Any
import time


class GridSearchWrapper:
    """Wrapper for GridSearchCV with MLflow logging."""

    def __init__(self, estimator, param_grid: Dict[str, list], cv: int = 5, scoring: str = "accuracy"):
        self.estimator = estimator
        self.param_grid = param_grid
        self.cv = cv
        self.scoring = scoring
        self.grid_search = None

    def fit_predict(self, X_train, y_train, X_test, y_test) -> Dict[str, Any]:
        """Fit model with grid search and predict."""
        start_time = time.time()

        self.grid_search = GridSearchCV(
            self.estimator,
            self.param_grid,
            cv=self.cv,
            scoring=self.scoring,
            n_jobs=-1,
            verbose=1
        )

        self.grid_search.fit(X_train, y_train)
        y_pred = self.grid_search.predict(X_test)

        train_time = time.time() - start_time

        # Calculate metrics (simplified)
        from sklearn.metrics import accuracy_score
        test_score = accuracy_score(y_test, y_pred)

        return {
            "algorithm_name": type(self.estimator).__name__,
            "best_params": self.grid_search.best_params_,
            "cv_mean_score": self.grid_search.best_score_,
            "cv_std_score": 0.0,  # TODO: Calculate from cv_results_
            "test_score": test_score,
            "train_time": train_time,
            "model": self.grid_search.best_estimator_,
            "feature_importance": None,
            "confusion_matrix": None,
            "classification_report": None,
        }
