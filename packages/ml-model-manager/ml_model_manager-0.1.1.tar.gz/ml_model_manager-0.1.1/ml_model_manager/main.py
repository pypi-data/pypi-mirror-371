# src/model.py
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier, VotingClassifier
from sklearn.svm import SVC
import xgboost as xgb
import warnings

class MLModelManager:
    def __init__(self):
        self.models = {}
        self.feature_columns = []

    def train_models(self, X, y, estimators=None, voting_type="soft", custom_estimators=None):
        """
        Train models using provided dataset.
        If no estimators are passed, defaults will be used.
        Supports custom estimators via dictionary.
        """
        self.feature_columns = X.columns.tolist()

        # Predefined models with pipelines
        available_models = {
            "logistic": Pipeline([
                ("scaler", StandardScaler()),
                ("clf", LogisticRegression(max_iter=1000))
            ]),
            "knn": Pipeline([
                ("scaler", StandardScaler()),
                ("clf", KNeighborsClassifier(n_neighbors=5))
            ]),
            "naive_bayes": GaussianNB(),  # NB often works best raw
            "decision_tree": DecisionTreeClassifier(max_depth=5, random_state=42),
            "gradient_boosting": GradientBoostingClassifier(
                n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42
            ),
            "xgboost": xgb.XGBClassifier(
                n_estimators=100, learning_rate=0.1, max_depth=3,
                use_label_encoder=False, eval_metric="logloss", random_state=42
            ),
            "svm": Pipeline([
                ("scaler", StandardScaler()),
                ("clf", SVC(probability=True, random_state=42))
            ]),
            "sgd": Pipeline([
                ("scaler", StandardScaler()),
                ("clf", SGDClassifier(max_iter=1000, tol=1e-3, random_state=42))
            ]),
            "random_forest": RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
        }

        # Merge user custom estimators
        if custom_estimators:
            available_models.update(custom_estimators)

        # If user didn’t specify → train all
        if estimators is None:
            estimators = list(available_models.keys())

        # Train models
        for name in estimators:
            if name == "voting":
                continue  # handled later

            if name not in available_models:
                raise ValueError(f"Estimator '{name}' not found in available or custom estimators.")

            model = available_models[name]
            model.fit(X, y)
            self.models[name] = model

        # Handle voting if requested
        if "voting" in estimators:
            if len(estimators) < 3:  # voting + at least 2 base models
                warnings.warn(
                    "Voting requires at least two base estimators. Falling back to default models.",
                    UserWarning
                )
                # fallback: use all trained models
                voting_estimators = [(name, model) for name, model in self.models.items()]
            else:
                voting_estimators = [(name, self.models[name]) for name in estimators if name != "voting"]

            voting = VotingClassifier(estimators=voting_estimators, voting=voting_type)
            voting.fit(X, y)
            self.models["voting"] = voting

    def predict(self, model_name, features):
        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' not found. Train it first.")
        X = pd.DataFrame([features], columns=self.feature_columns)
        return self.models[model_name].predict(X)[0]

    def batch_predict(self, model_name, features_list):
        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' not found. Train it first.")
        X = pd.DataFrame(features_list, columns=self.feature_columns)
        return self.models[model_name].predict(X)

    def predict_proba(self, model_name, features):
        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' not found. Train it first.")
        model = self.models[model_name]
        if not hasattr(model, "predict_proba"):
            raise NotImplementedError(f"Model '{model_name}' does not support probability predictions.")
        X = pd.DataFrame([features], columns=self.feature_columns)
        return model.predict_proba(X)[0]
