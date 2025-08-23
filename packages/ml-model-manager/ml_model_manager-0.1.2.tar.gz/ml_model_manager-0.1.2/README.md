# ml_model_manager

A lightweight Python package for training, managing, and predicting with multiple machine learning models.  
Supports classical ML algorithms, pipelines, ensemble learning (Voting), and user-defined custom estimators.  

---

## Features
- Preconfigured ML models: Logistic Regression, KNN, Naive Bayes, Decision Tree, Random Forest, Gradient Boosting, XGBoost, SVM, SGD.  
- Voting Classifier support (soft/hard voting).  
- Plug-and-play with **custom estimators**.  
- Built-in pipelines with `StandardScaler` where useful.  
- Easy single prediction and batch predictions.  
- Probability predictions (`predict_proba`) when available.  

---

## Installation
```
pip install ml-model-manager
```

---

## Quick Start

```python
import pandas as pd
from ml_model_manager import MLModelManager

# Example dataset
X = pd.DataFrame({
    "feature1": [1, 2, 3, 4],
    "feature2": [10, 20, 30, 40]
})
y = [0, 1, 0, 1]

# Initialize manager
manager = MLModelManager()

# Train default models
manager.train_models(X, y)

# Single prediction
print(manager.predict("logistic", {"feature1": 5, "feature2": 50}))

# Batch prediction
print(manager.batch_predict("knn", [
    {"feature1": 6, "feature2": 60},
    {"feature1": 2, "feature2": 25}
]))

# Probability prediction
print(manager.predict_proba("logistic", {"feature1": 5, "feature2": 50}))
```

---

## Voting Classifier

The `voting` estimator combines predictions from multiple trained models (soft or hard voting).

```python
# Use Logistic, KNN and Voting
manager.train_models(X, y, estimators=["logistic", "knn", "voting"], voting_type="soft")

print(manager.predict("voting", {"feature1": 7, "feature2": 70}))
```

⚠️ If fewer than 2 base models are given with `voting`, it falls back to all trained models with a warning.

---

## Custom Estimators

You can extend with your own models:

```python
from sklearn.linear_model import RidgeClassifier

custom = {
    "ridge": RidgeClassifier()
}

manager.train_models(X, y, estimators=["ridge"])
print(manager.predict("ridge", {"feature1": 8, "feature2": 80}))
```

---

## Project Structure
```
ml_model_manager/
 ├── __init__.py
 └── main.py          # MLModelManager class
README.md
setup.py
```

---

## Contributing
Contributions are welcome!  
- Fork the repo  
- Create a feature branch  
- Submit a pull request

---

## License
[MIT License](LICENSE)